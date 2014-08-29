# -*- coding: utf-8 -*-

"""
"""

import inspect

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.importlib import import_module


def get_permitted_fields(model, serializer):
    fields = [field.name for field in model._meta.fields]
    permissions = list(serializer.base_fields.keys())

    return set(fields + permissions)


def get_field_permissions():
    """look for serializers in serializers.py files
    """
    perm_key = lambda m: '{0.app_label}.{0.model_name}'.format(m._meta)
    is_seralizer = lambda cls: type(cls).__name__ == 'SerializerMetaclass'
    permissions = {}

    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module('%s.serializers' % app)
            for obj_name in dir(mod):
                obj = getattr(mod, obj_name)

                # Check if it is a serializer subclass
                if inspect.isclass(obj) and is_seralizer(obj):
                    try:
                        model = obj.Meta.model
                        fields = get_permitted_fields(model, obj)
                        permissions[perm_key(model)] = fields
                    except AttributeError:
                        pass

        except ImportError:
            continue

    return permissions
