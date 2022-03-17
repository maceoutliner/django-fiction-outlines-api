=============================
Django Fiction Outlines API
=============================

.. image:: https://badge.fury.io/py/django-fiction-outlines-api.svg
    :target: https://badge.fury.io/py/django-fiction-outlines-api

.. image:: https://github.com/maceoutliner/django-fiction-outlines-api/actions/workflows/tests.yml/badge.svg?branch=master
    :target: https://github.com/maceoutliner/django-fiction-outlines-api/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/maceoutliner/django-fiction-outlines-api/badge.svg?branch=master
    :target: https://coveralls.io/github/maceoutliner/django-fiction-outlines-api?branch=master

.. image:: https://readthedocs.org/projects/django-fiction-outlines-api/badge/?version=latest
    :target: http://django-fiction-outlines-api.readthedocs.io/en/latest/?badge=latest
    :alt: Documenatation Status

A RESTful JSON API for django-fiction-outlines.

Documentation
-------------

The full documentation is at https://django-fiction-outlines-api.readthedocs.io. The source code can be found at https://github.com/maceoutliner/django-fiction-outlines-api/.

Quickstart
----------

Install Django Fiction Outlines API::

    pip install django-fiction-outlines-api

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

Features
--------

* Provides a RESTful API for `django-fiction-outlines`_ using the `Django REST Framework`_, suitable for JSON, XML, or browsable HTML serialization.

**NOTE**: As with ``fiction_outlines``, this app makes use of the excellent object permissions library `django-rules`_.

.. _`django-fiction-outlines`: https://github.com/maceoutliner/django-fiction-outlines/

.. _`Django REST Framework`: http://www.django-rest-framework.org


Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r test_requirements.txt
    (myenv) $ pytest
    (myenv) $ flake8 setup.py fiction_outlines_api tests

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
