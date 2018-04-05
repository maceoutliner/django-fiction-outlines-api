=============================
Django Fiction Outlines API
=============================

.. image:: https://badge.fury.io/py/django-fiction-outlines-api.svg
    :target: https://badge.fury.io/py/django-fiction-outlines-api

.. image:: https://circleci.com/gh/maceoutliner/django-fiction-outlines-api.svg?style=svg
    :target: https://circleci.com/gh/maceoutliner/django-fiction-outlines-api

.. image:: https://coveralls.io/repos/github/maceoutliner/django-fiction-outlines-api/badge.svg?branch=master
    :target: https://coveralls.io/github/maceoutliner/django-fiction-outlines-api?branch=master

.. image:: https://readthedocs.org/projects/django-fiction-outlines-api/badge/?version=latest
    :target: http://django-fiction-outlines-api.readthedocs.io/en/latest/?badge=latest
    :alt: Documenatation Status

A RESTful JSON API for django-fiction-outlines.

Documentation
-------------

The full documentation is at https://django-fiction-outlines-api.readthedocs.io.

Quickstart
----------

Install Django Fiction Outlines API::

    pip install django-fiction-outlines-api

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'fiction_outlines_api.apps.FictionOutlinesApiConfig',
        ...
    )

Add Django Fiction Outlines API's URL patterns:

.. code-block:: python

    from fiction_outlines_api import urls as fiction_outlines_api_urls


    urlpatterns = [
        ...
        url(r'^', include(fiction_outlines_api_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
