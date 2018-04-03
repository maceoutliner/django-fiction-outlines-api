# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.urls import path, include

from fiction_outlines_api.urls import urlpatterns as fiction_outlines_api_urls

urlpatterns = [
    path('api/v1/', include(fiction_outlines_api_urls)),
]
