# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path('series/list', views.SeriesList.as_view(), name='series_list'),
]
