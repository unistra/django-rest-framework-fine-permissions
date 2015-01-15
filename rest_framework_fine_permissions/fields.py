# -*- coding: utf-8 -*-

"""
"""

import logging
import six
import collections

from django.db import models
from rest_framework import serializers
from rest_framework.fields import Field, empty


logger = logging.getLogger(__name__)

APP_NAMES = None


def get_application(app_label):
    """ Get an application. """
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

    """ Field that acts as a ModelPermissionsSerializer for relations. """

    def __init__(self, serializer, read_only=False, write_only=False,
                 required=None, default=empty, initial=empty, source=None,
                 label=None, help_text=None, style=None,
                 error_messages=None, validators=None, allow_null=False):
        self.serializer = get_serializer(serializer)
        assert self.serializer is not None \
            and issubclass(self.serializer, serializers.ModelSerializer), (
                "Bad serializer defined %s" % serializer
            )
        super(ModelPermissionsField, self).__init__(read_only, write_only,
                                                    required, default, initial,
                                                    source, label, help_text,
                                                    style, error_messages,
                                                    validators, allow_null)

    def to_representation(self, obj):
        """ Represent data for the field. """
        many = isinstance(obj, collections.Iterable) \
            or isinstance(obj, models.Manager) \
            and not isinstance(obj, dict)

        ser = self.serializer(obj, context=self.context, many=many)
        return ser.data
