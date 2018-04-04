from django.utils.translation import ugettext_lazy as _
from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_rules.mixins import PermissionRequiredMixin
from fiction_outlines.models import Series, Character, Location, Outline
from .serializers import SeriesSerializer, CharacterSerializer, LocationSerializer
from .serializers import OutlineSerializer
import logging

logger = logging.getLogger('api_views')


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
        return Outline.objects.filter(user=self.request.user)


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
        return Outline.objects.all()
