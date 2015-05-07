# -*- coding: utf-8 -*-

"""
"""

import inspect

from django.conf import settings
from django.utils.importlib import import_module
from rest_framework.utils.model_meta import get_field_info
from six import iterkeys
from itertools import chain
from rest_framework.compat import OrderedDict


def inherits_modelpermissions_serializer(cls):
    """ Verify that serializer is a :py:class:`~rest_framework_fine_permissions.serializers.ModelPermissionsSerializer`. """
    is_serializer = lambda ser: type(ser).__name__ == 'SerializerMetaclass'
    is_modelperms = lambda ser: 'ModelPermissionsSerializer' in [
        cls.__name__ for cls in ser.__bases__
    ]
    return inspect.isclass(cls) and is_serializer(cls) and is_modelperms(cls)


def merge_fields_and_pk(pk, fields):
    fields_and_pk = OrderedDict()
    fields_and_pk[pk.name] = pk
    fields_and_pk.update(fields)
    return fields_and_pk

def get_model_fields(model):
    fields_info = get_field_info(model)
    return chain(iterkeys(merge_fields_and_pk(fields_info.pk,
                                              fields_info.fields)),
                 iterkeys(fields_info.relations))

def get_permitted_fields(model, serializer):
    fields = get_model_fields(model)
    permissions = iterkeys(serializer._declared_fields)
    return set(chain(fields, permissions))


def get_field_permissions():
    """look for serializers in serializers.py files
    """
    perm_key = lambda m: '{0.app_label}.{0.model_name}'.format(m._meta)
    permissions = {}

    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module('%s.serializers' % app)
            for obj_name in dir(mod):
                obj = getattr(mod, obj_name)

                # Check if it is a serializer subclass
                if inherits_modelpermissions_serializer(obj):
                    try:
                        model = obj.Meta.model
                        fields = get_permitted_fields(model, obj)
                        permissions[perm_key(model)] = fields
                    except AttributeError:
                        pass

        except ImportError:
            continue

    return permissions
