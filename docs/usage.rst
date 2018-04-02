=====
Usage
=====

To use Django Fiction Outlines API in a project, add it to your `INSTALLED_APPS`:

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
