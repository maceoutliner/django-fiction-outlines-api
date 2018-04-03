from rest_framework import generics
from rest_framework import permissions
from rest_framework_rules.mixins import PermissionRequiredMixin
from fiction_outlines.models import Series, Character
from .serializers import SeriesSerializer, CharacterSerializer
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
