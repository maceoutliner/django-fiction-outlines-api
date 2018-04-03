# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'fiction_outlines_api'

urlpatterns = [
    path('series/list/', views.SeriesList.as_view(), name='series_listcreate'),
    path('series/<uuid:series>/', views.SeriesDetail.as_view(), name='series_item'),
    path('characters/list/', views.CharacterList.as_view(), name='character_listcreate'),
    path('character/<uuid:character>/', views.CharacterDetail.as_view(), name='character_item'),
]
