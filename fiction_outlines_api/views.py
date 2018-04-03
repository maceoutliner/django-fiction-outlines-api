from rest_framework import generics
from rest_framework import permissions
from rest_framework_rules.mixins import PermissionRequiredMixin
from fiction_outlines.models import Series
from .serializers import SeriesSerializer


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
    permission_required = 'fiction_outlines.view_series'

    def put(self, request, *args, **kwargs):
        self.permission_required = 'fiction_outlines.edit_series'
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.permission_required = 'fiction_outlines.delete_series'
        return super().delete(request, *args, **kwargs)
