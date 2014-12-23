django-rest-framework-fine-permissions
======================================

New permissions possibilities for rest-framework

Compatibility
-------------

work with :
 * Python 2.7 / Python 3.4
 * Dango 1.6
 * Django Rest Framework < 2.4

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

 
