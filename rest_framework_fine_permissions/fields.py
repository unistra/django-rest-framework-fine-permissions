# -*- coding: utf-8 -*-

"""
"""

import logging
import six
from rest_framework import serializers
from rest_framework.fields import is_simple_callable
from rest_framework.fields import Field


logger = logging.getLogger(__name__)

APP_NAMES = None


def get_application(app_label):
    """ Get application. """
    try:
        # django >= 1.7
        from django.apps import apps as django_apps
        return django_apps.get_app_package(app_label)
    except ImportError:
        # django < 1.7
        from django.conf import settings
        global APP_NAMES
        if APP_NAMES is None:
            APP_NAMES = {
                app.rsplit('.', 1)[-1]: app for app in settings.INSTALLED_APPS
            }

        return APP_NAMES[app_label]


def get_serializer(serializer):
    """ Load a serializer. """
    if isinstance(serializer, six.string_types):
        try:
            app_label, serializer_name = serializer.split('.')
            app_package = get_application(app_label)
            serializer_module = __import__('%s.serializers' % app_package,
                                           fromlist=['serializers'])
            serializer = getattr(serializer_module, serializer_name)
        except Exception:
            logger.error('Serializer %s not found' % serializer)
            return None

    return serializer




class ModelPermissionsField(Field):
    """
    """

    def __init__(self, serializer, field='', **kwargs):
        self.serializer = get_serializer(serializer)
        assert self.serializer is not None \
            and issubclass(self.serializer, serializers.ModelSerializer), (
                "Bad serializer defined %s" % serializer
            )
        self.field = field
        super(ModelPermissionsField, self).__init__(**kwargs)

    def _get_serializer(self, attr):
        many = hasattr(attr, '__iter__') and not isinstance(attr, dict)
        return self.serializer(attr, context=self.context, many=many)

    def to_representation(self, obj):
        attr = getattr(obj, self.field or self.field_name, None)

        assert attr is not None, (
            "Bad configuration for field %s, "
            "model %s doesn't have a field with this name" %
            (self.field_name, self.parent.Meta.model.__name__))

        if is_simple_callable(getattr(attr, 'all', None)):
            attr = attr.all()

        return self._get_serializer(attr).data
