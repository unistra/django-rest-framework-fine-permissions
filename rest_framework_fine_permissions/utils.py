# -*- coding: utf-8 -*-

"""
"""

from importlib import import_module
import inspect
from collections import OrderedDict
import logging

from django.apps import apps
from django.conf import settings
from rest_framework.utils.model_meta import get_field_info
from six import iterkeys, string_types
from itertools import chain


logger = logging.getLogger(__name__)
APP_NAMES = None


def get_application(app_label):
    """ Get an application. """
    app_config = apps.get_app_config(app_label)
    return app_config.module.__name__


def get_serializer(serializer):
    """ Load a serializer. """
    if isinstance(serializer, string_types):
        try:
            app_label, serializer_name = serializer.split('.')
            app_package = get_application(app_label)
            serializer_module = import_module('%s.serializers' % app_package)
            serializer = getattr(serializer_module, serializer_name)
        except Exception as e:
            logger.error('Serializer %s not found: %s' % (serializer, e))
            return None
    return serializer


def inherits_modelpermissions_serializer(cls):
    """ Verify that serializer is a :py:class:`~rest_framework_fine_permissions.serializers.ModelPermissionsSerializer`. """
    def is_modelperms():
        return 'ModelPermissionsSerializer' in [
            ser.__name__ for ser in cls.__bases__
        ]
    is_serializer = type(cls).__name__ == 'SerializerMetaclass'

    return inspect.isclass(cls) and is_serializer and is_modelperms()


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
    result = dict.fromkeys(fields, None)
    result.update(serializer._declared_fields)
    return result


def get_field_permissions():
    serializers = {}

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
                        perm_key = '{0.app_label}.{0.model_name}'\
                            .format(model._meta)
                        serializers[perm_key] = (
                            fields, '{0.__module__}.{0.__name__}'.format(obj))
                    except AttributeError:
                        pass

        except ImportError:
            continue

    return serializers
