# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

# import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "&p)f@kw!4k0z4^g)bwip4xzc_+th1ae9zh2b@yez_&+u=iknom"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}


AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)


ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "taggit",
    "rest_framework",
    "rules.apps.AutodiscoverRulesConfig",
    "rest_framework_rules",
    "fiction_outlines",
    "fiction_outlines_api",
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]
