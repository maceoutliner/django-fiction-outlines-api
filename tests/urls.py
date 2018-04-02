# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from fiction_outlines_api.urls import urlpatterns as fiction_outlines_api_urls

urlpatterns = [
    url(r'^', include(fiction_outlines_api_urls, namespace='fiction_outlines_api')),
]
