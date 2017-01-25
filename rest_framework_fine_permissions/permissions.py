# -*- coding: utf-8 -*-

""" Provides new permission policies for django-rest-framework
"""

from rest_framework.permissions import DjangoModelPermissions, BasePermission
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions.models import FilterPermissionModel
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_fine_permissions.serializers import QSerializer


class FullDjangoModelPermissions(DjangoModelPermissions):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions

    It ensures that the user is authenticated, and has the appropriate
    `view`/`add`/`change`/`delete` permissions on the model.

    This permission can only be applied against view classes that provide a
    `.model` or `.queryset` attribute.
    """

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class FilterPermission(BasePermission):
    """
    filter permission
    """

    def has_object_permission(self, request, view, obj):
        """
        check filter permissions
        """

        user = request.user

        if not user.is_superuser and not user.is_anonymous():
            valid = False
            try:
                ct = ContentType.objects.get_for_model(obj)
                fpm = FilterPermissionModel.objects.get(user=user,
                                                        content_type=ct)
                myq = QSerializer(base64=True).loads(fpm.filter)
                try:
                    myobj = obj.__class__.objects.filter(myq).distinct().get(pk=obj.pk)
                    if myobj:
                        valid = True
                except ObjectDoesNotExist:
                    valid = False
            except ObjectDoesNotExist:
                valid = True
            finally:
                return valid
        else:
            return True
