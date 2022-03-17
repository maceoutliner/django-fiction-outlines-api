from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class TreeUnavailable(APIException):
    status_code = 503
    default_detail = _('We are having temporary issues with outlines at this time. Please try again later.')
    default_code = 'tree_unavailable'


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = _('Service temporarily unavailable, please try again later.')
    default_code = 'service_unavailable'
