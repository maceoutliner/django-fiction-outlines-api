# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'fiction_outlines_api'

urlpatterns = [
    path('series/list/', views.SeriesList.as_view(), name='series_listcreate'),
    path('series/<uuid:series>/', views.SeriesDetail.as_view(), name='series_item'),
    path('characters/list/', views.CharacterList.as_view(), name='character_listcreate'),
    path('character/<uuid:character>/', views.CharacterDetail.as_view(), name='character_item'),
    path('character/<uuid:character>/add/<uuid:outline>/',
         views.CharacterInstanceCreateView.as_view(), name='character_instance_create'),
    path('character/<uuid:character>/instance/<uuid:instance>/', views.CharacterInstanceDetailView.as_view(),
         name='character_instance_item'),
    path('locations/', views.LocationList.as_view(), name='location_listcreate'),
    path('location/<uuid:location>/', views.LocationDetail.as_view(), name='location_item'),
    path('location/<uuid:location>/add/<uuid:outline>/', views.LocationInstanceCreateView.as_view(),
         name='location_instance_create'),
    path('location/<uuid:location>/instance/<uuid:instance>/', views.LocationInstanceDetailView.as_view(),
         name='location_instance_item'),
    path('outlines/', views.OutlineList.as_view(), name='outline_listcreate'),
    path('outline/<uuid:outline>/', views.OutlineDetail.as_view(), name='outline_item'),
    path('outline/<uuid:outline>/createarc/', views.ArcCreateView.as_view(), name='arc_create'),
    path('outline/<uuid:outline>/arc/<uuid:arc>/', views.ArcDetailView.as_view(), name='arc_item'),
    path('outline/<uuid:outline>/item/<uuid:storynode>/', views.StoryNodeDetailView.as_view(),
         name='storynode_item'),
    path('storynode/move/<uuid:node_to_move_id>/<uuid:target_node_id>/<position>/', views.StoryNodeMoveView.as_view(),
         name='storynode_move'),
    path('storynode/<uuid:storynode>/<action>/<position>/',
         views.StoryNodeCreateView.as_view(), name='storynode_create'),
    path('arcnode/move/<uuid:node_to_move_id>/<uuid:target_node_id>/<position>/',
         views.ArcNodeMoveView.as_view(), name='arcnode_move'),
    path('arcnode/<uuid:arcnode>/<action>/', views.ArcNodeCreateView.as_view(), name='arcnode_create_default'),
    path('arcnode/<uuid:arcnode>/<action>/<position>/', views.ArcNodeCreateView.as_view(), name='arcnode_create'),
    path('outline/<uuid:outline>/arc/<uuid:arc>/item/<uuid:arcnode>', views.ArcNodeDetailView.as_view(),
         name='arcnode_item'),
]
