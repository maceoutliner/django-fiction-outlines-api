# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'fiction_outlines_api'

urlpatterns = [
    path('series/list/', views.SeriesList.as_view(), name='series_listcreate'),
]
