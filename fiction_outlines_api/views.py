import logging
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework_rules.mixins import PermissionRequiredMixin
from fiction_outlines.models import Series, Character, Location, Outline, Arc
from fiction_outlines.models import CharacterInstance, LocationInstance
from fiction_outlines.models import ArcElementNode, StoryElementNode
from fiction_outlines.signals import tree_manipulation
from .serializers import SeriesSerializer, CharacterSerializer, LocationSerializer
from .serializers import OutlineSerializer, ArcSerializer, ArcCreateSerializer, ArcElementNodeSerializer
from .serializers import StoryElementNodeSerializer, CharacterInstanceSerializer, LocationInstanceSerializer
from .mixins import NodeMoveMixin, MultiObjectPermissionsMixin, NodeAddMixin

logger = logging.getLogger('fiction-outlines-api')


class SeriesList(generics.ListCreateAPIView):
    '''
    API view for series list.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SeriesSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Series.objects.filter(user=self.request.user)


class SeriesDetail(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    Retrieves details of a series.
    '''
    serializer_class = SeriesSerializer
    object_permission_required = 'fiction_outlines.view_series'
    permission_classes = (permissions.IsAuthenticated,)
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'series'

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_series'
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_series'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Series.objects.all()


class CharacterList(generics.ListCreateAPIView):
    '''
    API view for character list
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CharacterSerializer

    def perform_create(self, serializer):
        if serializer.validated_data['series']:
            for series in serializer.validated_data['series']:
                if not self.request.user.has_perm('fiction_outlines.edit_series', series):
                    raise PermissionDenied(_('You do not have editing rights for the specified series.'))
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)


class CharacterDetail(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API view for all single item character operations besides create.
    '''
    serializer_class = CharacterSerializer
    object_permission_required = 'fiction_outlines.view_character'
    permission_classes = (permissions.IsAuthenticated,)
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'character'

    def perform_update(self, serializer):
        if 'series' in serializer.validated_data.keys():
            if serializer.validated_data['series']:
                for series in serializer.validated_data['series']:
                    if not self.request.user.has_perm('fiction_outlines.edit_series', series):
                        raise PermissionDenied(_("You do not have editing rights to the specified series."))
        return super().perform_update(serializer)

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_character'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_character'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_character'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Character.objects.all()


class CharacterInstanceCreateView(MultiObjectPermissionsMixin, PermissionRequiredMixin, generics.CreateAPIView):
    '''
    API view for creating a character instance. Expects kwargs in url for character and
    outline. All other data comes from the serializer.
    '''
    serializer_class = CharacterInstanceSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_class_permission_dict = {
        'character': {'obj_class': Character, 'object_permission_required': 'fiction_outlines.edit_character',
                      'lookup_url_kwarg': 'character'},
        'outline': {'obj_class': Outline, 'object_permission_required': 'fiction_outlines.edit_outline',
                    'lookup_url_kwarg': 'outline'},
    }

    def perform_create(self, serializer):
        try:
            serializer.save(character=self.permission_object_dict['character'],
                            outline=self.permission_object_dict['outline'])
        except IntegrityError:
            logger.error("Attempt to create a character instance for a character already present in outline.")
            raise ParseError


class CharacterInstanceDetailView(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API view for non-creation actions on CharacterInstance objects.
    '''
    serializer_class = CharacterInstanceSerializer
    object_permission_required = 'fiction_outlines.view_character_instance'
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'instance'

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_character_instance'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_character_instance'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_character_instance'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return CharacterInstance.objects.all()


class LocationList(generics.ListCreateAPIView):
    '''
    API view for location list
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LocationSerializer

    def perform_create(self, serializer):
        if serializer.validated_data['series']:
            for series in serializer.validated_data['series']:
                if not self.request.user.has_perm('fiction_outlines.edit_series', series):
                    raise PermissionDenied(_('You do not have editing rights for the specified series.'))
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)


class LocationDetail(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API view for all single item location operations besides create.
    '''
    serializer_class = LocationSerializer
    object_permission_required = 'fiction_outlines.view_location'
    permission_classes = (permissions.IsAuthenticated,)
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'location'

    def perform_update(self, serializer):
        if 'series' in serializer.validated_data.keys():
            if serializer.validated_data['series']:
                for series in serializer.validated_data['series']:
                    if not self.request.user.has_perm('fiction_outlines.edit_series', series):
                        raise PermissionDenied(_("You do not have editing rights to the specified series."))
        return super().perform_update(serializer)

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_location'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_location'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_location'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Location.objects.all()


class LocationInstanceCreateView(MultiObjectPermissionsMixin, PermissionRequiredMixin, generics.CreateAPIView):
    '''
    API view for creating a location instance. Expects kwargs in url for location and
    outline. All other data comes from the serializer.
    '''
    serializer_class = LocationInstanceSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_class_permission_dict = {
        'location': {'obj_class': Location, 'object_permission_required': 'fiction_outlines.edit_location',
                     'lookup_url_kwarg': 'location'},
        'outline': {'obj_class': Outline, 'object_permission_required': 'fiction_outlines.edit_outline',
                    'lookup_url_kwarg': 'outline'},
    }

    def perform_create(self, serializer):
        try:
            serializer.save(location=self.permission_object_dict['location'],
                            outline=self.permission_object_dict['outline'])
        except IntegrityError:
            logger.error("Attempt to create a location instance for a location already present in outline.")
            raise ParseError


class LocationInstanceDetailView(PermissionRequiredMixin, generics.RetrieveDestroyAPIView):
    '''
    API view for non-creation actions on LocationInstance objects.
    '''
    serializer_class = LocationInstanceSerializer
    object_permission_required = 'fiction_outlines.view_location_instance'
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'instance'

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_location_instance'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return LocationInstance.objects.all()


class OutlineList(generics.ListCreateAPIView):
    '''
    API view for location list
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OutlineSerializer

    def perform_create(self, serializer):
        if serializer.validated_data['series']:
            if not self.request.user.has_perm('fiction_outlines.edit_series', serializer.validated_data['series']):
                raise PermissionDenied(_('You do not have editing rights for the specified series.'))
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Outline.objects.filter(
            user=self.request.user
        ).select_related('series').prefetch_related('tags',
                                                    'arc_set',
                                                    'storyelementnode_set',
                                                    'characterinstance_set',
                                                    'locationinstance_set')


class OutlineDetail(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API view for all single item location operations besides create.
    '''
    serializer_class = OutlineSerializer
    object_permission_required = 'fiction_outlines.view_outline'
    permission_classes = (permissions.IsAuthenticated,)
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'outline'

    def perform_update(self, serializer):
        if 'series' in serializer.validated_data.keys():
            if (serializer.validated_data['series'] and
                not self.request.user.has_perm('fiction_outlines.edit_series', serializer.validated_data['series'])):
                raise PermissionDenied(_("You do not have editing rights to the specified series."))
        return super().perform_update(serializer)

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_outline'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_outline'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_outline'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Outline.objects.all().select_related('series').prefetch_related('tags',
                                                                               'arc_set',
                                                                               'storyelementnode_set',
                                                                               'characterinstance_set',
                                                                               'locationinstance_set')


class ArcCreateView(PermissionRequiredMixin, generics.CreateAPIView):
    '''
    API for creating arcs. Uses a custom serializer.
    '''
    serializer_class = ArcCreateSerializer
    object_permission_required = 'fiction_outlines.edit_outline'
    permission_required = 'fiction_outlines_api.valid_user'

    def dispatch(self, request, *args, **kwargs):
        self.outline = get_object_or_404(Outline, pk=kwargs['outline'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.outline)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        self.object = self.outline.create_arc(mace_type=serializer.validated_data['mace_type'],
                                              name=serializer.validated_data['name'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        result_serializer = ArcSerializer(self.object)
        headers = self.get_success_headers(result_serializer.data)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ArcDetailView(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API for non-create object operations for Arc model.
    '''
    serializer_class = ArcSerializer
    object_permission_required = 'fiction_outlines.view_arc'
    permission_required = 'fiction_outlines_api.valid_user'
    lookup_url_kwarg = 'arc'

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_arc'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_arc'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_arc'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Arc.objects.all()


class ArcNodeDetailView(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API for viewing a tree of arc nodes.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ArcElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.view_arc_node'
    lookup_url_kwarg = 'arcnode'

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
        except IntegrityError as IE:
            response = Response({'error': str(IE)}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_arc_node'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_arc_node'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_arc_node'
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.arc_element_type in ['mile_hook', 'mile_reso']:
            raise ParseError('You cannot delete the hook or resolution of an arc.')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return ArcElementNode.objects.all()  # pragma: no cover


class ArcNodeCreateView(PermissionRequiredMixin, NodeAddMixin, generics.CreateAPIView):
    '''
    API view for add_child and add_sibling
    '''
    serializer_class = ArcElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.edit_arc_node'
    fields_required_for_add = ('arc_element_type', 'description', 'story_element_node')
    lookup_url_kwarg = 'arcnode'

    def get_queryset(self):
        return ArcElementNode.objects.all()


class ArcNodeMoveView(PermissionRequiredMixin, NodeMoveMixin, generics.GenericAPIView):
    '''
    View for moving arc nodes.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ArcElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.edit_arc_node'
    target_node_type_fieldname = 'arc_element_type'
    related_key = 'arc'

    def get_queryset(self):
        return ArcElementNode.objects.all()


class StoryNodeMoveView(PermissionRequiredMixin, NodeMoveMixin, generics.GenericAPIView):
    '''
    View for moving story nodes.
    '''
    serializer_class = StoryElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.edit_story_node'
    target_node_type_fieldname = 'story_element_type'
    related_key = 'outline'

    def get_queryset(self):
        return StoryElementNode.objects.all()


class StoryNodeCreateView(PermissionRequiredMixin, NodeAddMixin, generics.CreateAPIView):
    '''
    View for adding story nodes.
    '''
    serializer_class = StoryElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.edit_story_node'
    fields_required_for_add = ('story_element_type', 'name', 'description')
    lookup_url_kwarg = 'storynode'

    def get_queryset(self):
        return StoryElementNode.objects.all()


class StoryNodeDetailView(PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API for viewing a tree of story nodes.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StoryElementNodeSerializer
    permission_required = 'fiction_outlines_api.valid_user'
    object_permission_required = 'fiction_outlines.view_story_node'
    lookup_url_kwarg = 'storynode'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if 'story_element_type' in serializer.validated_data.keys():
            try:
                instance = self.get_object()
                tree_manipulation.send(
                    sender=StoryElementNode,
                    instance=instance,
                    action='update',
                    target_node_type=serializer.validated_data['story_element_type']
                )
            except IntegrityError as IE:
                logger.debug('Changing the node to this type would result in an invalid outline sructure. Details: %s' % str(IE))  # noqa: E501
                raise ParseError(_(str(IE)))
        try:
            response = super().update(request, *args, **kwargs)
        except IntegrityError as IE:
            response = Response({'error': str(IE)}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def put(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_story_node'
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.edit_story_node'
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object_permission_required = 'fiction_outlines.delete_story_node'
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return StoryElementNode.objects.all()  # pragma: no cover
