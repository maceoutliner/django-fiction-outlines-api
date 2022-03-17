import logging
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from treebeard.exceptions import InvalidPosition, InvalidMoveToDescendant, PathOverflow
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import response, status
from fiction_outlines.signals import tree_manipulation
from fiction_outlines.models import IntegrityError
from .exceptions import TreeUnavailable
from fiction_outlines.models import ArcGenerationError


POSITIONS = ('first-child', 'last-child', 'first-sibling', 'last-sibling', 'left', 'right')

logger = logging.getLogger('fiction-outlines-api')


class MultiObjectPermissionsMixin(object):
    '''
    API Mixin that compares ``n`` objects and their permissions and returns if both are valid.
    Objects can be referred to by key afterwards in self.object_dict.
    permission dict should be:

    {'obj1': {'obj_class': class_model, 'lookup_url_kwarg', 'object_permission_required': 'your rules perm here'}, ...}

    Is it ugly, yes. Does it make doing this in view after view repeatable. Yep.
    '''
    object_class_permission_dict = {}

    def get_permission_object(self, pkval, objectpermission, obj_class):
        '''
        Fetches the permission object and checks it agains the permission specified.

        :param pkval:
            The pk value to use in the search.
        :param objectpermission:
            A permission based on the :module:`rules` format, e.g. "app_name.permission_name"
        :param obj_class:
            The class of the object we are searching for.

        :returns: The found object.
        '''
        queryset = self.filter_queryset(self.get_object_permission_queryset(obj_class))
        filter_kwargs = {self.lookup_field: pkval}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, objectpermission, obj)
        return obj

    def check_object_permissions(self, request, perm, obj):
        '''
        Verifies the object permissions are valid for the current user.

        :param request:
             The request object. The user is retrieved from here.
        :param perm:
             The permission to validate against (in :module:`rules`) format.
        :param obj:
             The object to evaluate.

        :raise PermissionDenied: when user lacks the required permission.
        '''
        if not request.user.has_perm(perm, obj):
            raise PermissionDenied
        return super().check_object_permissions(request, obj)

    def post(self, request, *args, **kwargs):
        self.permission_object_dict = {}
        for obj, attrs in self.object_class_permission_dict.items():
            try:
                self.permission_object_dict[obj] = self.get_permission_object(kwargs[attrs['lookup_url_kwarg']],
                                                                              attrs['object_permission_required'],
                                                                              attrs['obj_class'])
            except PermissionDenied as PD:
                error_response = response.Response({'error_message': str(PD)}, status=status.HTTP_403_FORBIDDEN,
                                                   content_type='application/json')
                error_response.accepted_renderer = request.accepted_renderer
                return error_response
        return super().post(request, *args, **kwargs)

    def get_object_permission_queryset(self, obj_class):
        '''
        Fetches the queryset for the permission object.

        :param obj_class:
            Model class of the object to retrieve.

        :returns: A django queryset for the class.
        '''
        return obj_class.objects.all()


class NodeAddMixin(object):
    '''
    API Mixin for add_sibling and add_child commands.

    :attribute fields_required_for_add:
        A tuple of fields that should be required in the submitted serializer in order to create the object.
    '''
    fields_required_for_add = ('description',)  # Declare in more detail in subclass.

    def post(self, request, *args, **kwargs):
        '''
        Parses kwargs and kicks off evaluation process.

        :keyword action:
            Either ``add_child`` or ``add_sibling``.
        :keyword position:
            If ``add_sibling`` this is required, and must be a value from :data:POSITIONS.
            If action is ``add_child`` this is ignored.

        :raise Http404: if action is not a one of the two permitted options.
        '''
        self.source_node = self.get_object()
        self.action = kwargs['action']
        if self.action not in ['add_child', 'add_sibling']:
            raise Http404
        logger.debug('Action is set as %s' % self.action)
        if 'position' in kwargs.keys() and self.action == 'add_sibling':
            self.pos = kwargs['position']
            if self.pos not in POSITIONS:
                raise ValidationError(_("Not a valid position for adding node."))
        else:
            self.pos = None
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        '''
        Does the final validation of submitted data and if valid proceeds with creation.

        :raises NotImplementedError: if client attempts to specify many-to-many relationship at creation.
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['assoc_characters'] or serializer.validated_data['assoc_locations']:
            raise NotImplementedError(_('Sorry, but specifying linked characters and locations at creation is not currently supported.'))  # noqa: E501
        serializer = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        '''
        The actual creation part.

        :param serializer:
            The serializer object representing the object to be created.

        :raises ValidationError: if the data submitted is invalid or violates the structure of the tree.

        :returns: A serializer representing the created object.
        '''
        kwarg_dict = {}
        for field in self.fields_required_for_add:
            kwarg_dict[field] = serializer.validated_data[field]
            if self.pos:
                kwarg_dict['pos'] = self.pos
        try:
            with transaction.atomic():
                logger.debug('attempting execution of %s for %s' % (self.action, self.source_node))
                new_node = getattr(self.source_node, self.action)(**kwarg_dict)
                logger.debug("New node created with pk of %s, which is a child of %s" %
                             (new_node.pk, new_node.get_parent(update=True)))
        except ArcGenerationError as AE:
            logger.debug("ArcGenerationError: %s" % str(AE))
            raise ValidationError(str(AE))
        except IntegrityError as IE:
            logger.debug("IntegrityError: %s" % str(IE))
            raise ValidationError(str(IE))
        new_serializer = self.get_serializer_class()(new_node)
        logger.debug("New serializer data looks like: %s" % new_serializer.data)
        return new_serializer


class NodeMoveMixin(object):
    '''
    API mixin for move method for nodes.
    '''
    source_node = None
    target_node = None
    target_node_type_fieldname = None  # fieldname to send to tree_manipulation signal.
    pos = None
    related_key = None  # Specify in subclass

    def get_object(self, pkval):
        '''
        Fetches an individual object and verifies that the user has the appropriate
        permissions to move it.

        :param pkval:
             The primary key value to use in the search.

        :returns: Object

        :raises Http404: if object cannot be found

        :raises PermissionDenied: if user does not have the required permissions.
        '''
        logger.debug('generating queryset')
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: pkval}
        logger.debug('Searching for node with: %s' % filter_kwargs)
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_move(self):
        '''
        Validates the proposed move, and if valid, will manipulate the tree accordingly.

        :raises ValidationError: if the move request violates tree structure.

        :raises TreeUnavailable: if the DB tree is out of available nodes.

        :returns: A serializer representing the updated node.
        '''
        logger.debug('Comparing related values from %s' % self.related_key)
        if getattr(self.source_node, self.related_key) != getattr(self.target_node, self.related_key):
            logger.debug('%s and %s do NOT match.' % (getattr(self.source_node, self.related_key),
                                                      getattr(self.target_node, self.related_key)))
            raise ValidationError(_('Nodes must be from the same %s' % self.related_key))
        logger.debug("Keys match!")
        logger.debug("Checking pos vs target...")
        if 'child' not in self.pos and self.target_node.is_root():
            logger.debug("You can't move this to the level of the root!")
            raise ValidationError(_('You cannot move this item to the same level as a root node!'))
        try:
            logger.debug("Sending manipulation signal for %s" % self.source_node.__class__)
            tree_manipulation.send(sender=self.source_node.__class__, instance=self.source_node,
                                   target_node=self.target_node,
                                   target_node_type=getattr(self.target_node, self.target_node_type_fieldname),
                                   action='move', pos=self.pos)
        except IntegrityError as IE:
            logger.error(_('This would result in nodes being children of invalid parent nodes. %s' % str(IE)))
            raise ValidationError(_('This would result in nodes being children of invalid parent nodes. %s' % str(IE)))
        try:
            with transaction.atomic():
                self.source_node.move(target=self.target_node, pos=self.pos)
        except InvalidPosition as IP:  # pragma: no cover Treebeard error that is very hard to trigger.
            logger.error(_("This is not a permitted position. \n Details: %s" % str(IP)))
            raise ValidationError(_('This is not a permitted position. Details: %s' % str(IP)))
        except InvalidMoveToDescendant as IMD:
            logger.error(_('Invalid move to descendant! %s' % str(IMD)))
            raise ValidationError(_('You cannot move an arc element to be the sibling or child of one of its descendants.'))  # noqa: E501
        except PathOverflow as PO:  # pragma: no cover It would take a monumental amount of data to trigger this.
            logger.error(_('There is no further room within the tree for %s!!!!! DETAILS: %s' %
                           (str(self.source_node.__class__), str(PO))))
            raise TreeUnavailable
        return self.get_serializer_class()(self.get_object(self.source_node.pk))

    def post(self, request, *args, **kwargs):
        logger.debug("Trying to fetch source node.")
        self.source_node = self.get_object(kwargs['node_to_move_id'])
        logger.debug("Trying to fetch target node")
        self.target_node = self.get_object(kwargs['target_node_id'])
        self.pos = kwargs['position']
        new_node_serializer = self.perform_move()
        return response.Response(new_node_serializer.data, status=status.HTTP_200_OK)
