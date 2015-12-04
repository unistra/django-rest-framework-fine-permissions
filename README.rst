django-rest-framework-fine-permissions
======================================

New permissions possibilities for rest-framework

Compatibility
-------------

Works with :

  * Python 2.7, 3.3, 3.4
  * Django >= 1.7
  * Django Rest Framework >= 3.0

.. image:: https://travis-ci.org/unistra/django-rest-framework-fine-permissions.svg
    :target: https://travis-ci.org/unistra/django-rest-framework-fine-permissions
    
.. image:: https://coveralls.io/repos/unistra/django-rest-framework-fine-permissions/badge.png
    :target: https://coveralls.io/r/unistra/django-rest-framework-fine-permissions

.. image:: https://landscape.io/github/unistra/django-rest-framework-fine-permissions/master/landscape.svg?style=flat
    :target: https://landscape.io/github/unistra/django-rest-framework-fine-permissions/master
    :alt: Code Health


Installation
------------

Install the package from pypi: ::

    pip install djangorestframework-fine-permissions

Add the application in your django settings: ::

    DJANGO_APPS = ('rest_framework_fine_permissions',)

Sync the django's database: ::

    python manage.py syncdb

Configure your rest framework : ::

    REST_FRAMEWORK = {
        'DEFAULT_FILTER_BACKENDS': (
            # Enable the filter permission backend for all GenericAPIView
            'rest_framework_fine_permissions.filters.FilterPermissionBackend',
        ),

        'DEFAULT_PERMISSION_CLASSES': (
            # Enable the django model permissions (view,create,delete,modify)
            'rest_framework_fine_permissions.permissions.FullDjangoModelPermissions',
            # OPTIONAL if you use FilterPermissionBackend and GenericAPIView. Check filter permissions for objects.
            'rest_framework_fine_permissions.permissions.FilterPermission',
        )
    }

Usage
-----

 * Go to the django admin page
 * Add field's permissions to a user with the "User fields permissions" link
 * Add filter's permissions to a user with the "User filters permissions" link
