# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('fiction_outlines_api.urls')),
]
