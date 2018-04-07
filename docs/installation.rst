.. _`installation`:

============
Installation
============

At the command line::

    $ easy_install django-fiction-outlines-api

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv django-fiction-outlines-api
    $ pip install django-fiction-outlines-api

Add it and dependencies to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        '
        'rest_framework',
        'taggit',
        'rules.apps.AutodiscoverRulesConfig',
        'rest_framework_rules',
        'fiction_outlines',
        'fiction_outlines_api',
        ...
    )

If you have not already, add ``rules`` to you ``AUTHENTICATION_BACKENDS``.

.. code-block:: python

   AUTHENTICATION_BACKENDS = (
       'rules.permissions.ObjectPermissionBackend',
       'django.contrib.auth.backends.ModelBackend',
   )

Unless you like to live dangerously, it is **STRONGLY** recommend you configure whichever database you use for outlines to have ``ATOMIC_REQUESTS`` to ``True``.

.. code-block:: python

   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "outlines",
           "ATOMIC_REQUESTS": True,
       }}

.. _`django-rules`: https://github.com/dfunckt/django-rules

Add Django Fiction Outlines API's URL patterns:

.. code-block:: python

    from fiction_outlines_api import urls as fiction_outlines_api_urls


    urlpatterns = [
        ...
        url(r'^', include(fiction_outlines_api_urls)),
        ...
    ]

If you haven't already installed ``fiction_outlines`` you should run ``python manage.py migrate`` now.
