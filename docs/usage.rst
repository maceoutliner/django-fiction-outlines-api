=====
Usage
=====

It is expected that this API will be embedded into your project's overall `DRF`_-based API. Simply include this app's URLs as documented in the :ref:`installation` instructions, and follow the configuration documentation for `DRF`_. You can generate full documentation for your resulting API either through DRF's `native generation tool`_ or you can use a third-party library such as `drf-yasg`_.

.. _`DRF`: http://www.django-rest-framework.org/

.. _`native generation tool`: http://www.django-rest-framework.org/topics/documenting-your-api/

.. _`drf-yasg`: https://github.com/axnsan12/drf-yasg/

.. warning::
   The same `known caveats`_ of django-fiction-outlines also apply here.

   - Do **NOT** attempt to create a new node using the Django-provided construction method. Use dedicated methods such as ``add_root``, ``add_child``, and ``add_sibling`` instead.
   - Do **NOT** attempt to directly edit ``path``, ``step``, ``depth``, ``num_child``, etc. Use the provided `move` method.
   - ``MP_Node`` uses a lot of raw SQL, so always retrieve the node from the db again after tree manipulation before calling it to do anything else.
   - Object permissions come from `django-rules`_, and the permission logic lies in the view layer. If you want to introduce your own custom logic, you should subclass the provided views in order to reduce the risk of security breaches.
   - For the same reason, if you must define a custom manager, you **NEED** to subclass ``treebeard``'s base ``MP_Node`` manager.

.. _`django-rules`: https://github.com/dfunckt/django-rules

.. _`known caveats`: http://django-fiction-outlines.readthedocs.io/en/latest/caveats.html
