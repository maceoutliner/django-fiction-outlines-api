==============
Introduction
==============

Welcome to Django Fiction Outlines API!

Being a reusable Django app for managing fiction outlines. Part of the broader `maceoutliner`_ project.

.. _maceoutliner: https://github.com/maceoutliner/

Documentation
-------------

The full documentation is at https://django-fiction-outlines-api.readthedocs.io.

Code Repo and Issue Tracker
---------------------------

The code repository and issue list for this project can be found at `Github`_.

.. _Github: https://github.com/maceoutliner/django-fiction-outlines-api/

License
-------

:ref:`BSD` for your convenience.


Features
--------

  * Provides a RESTful API for `django-fiction-outlines`_ suitable for serialization via JSON, XML, or `DRF's`_ browsable API.

  * NOTE: Django Fiction Outlines API uses an object permission manager called `django-rules`_. This allows extremely flexible permission schemes without crufting up your database or model logic. By default, `fiction_outlines` will restrict any view or editing to the owner of the object.

.. _django-rules: https://github.com/dfunckt/django-rules

.. _`django-fiction-outlines`: https://github.com/maceoutliner/django-fiction-outlines

.. _`DRF's`: http://www.django-rest-framework.org
