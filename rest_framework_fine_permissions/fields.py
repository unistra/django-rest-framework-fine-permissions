# -*- coding: utf-8 -*-

"""
"""

import logging
import six
import collections

from django.db import models
from rest_framework import serializers
from rest_framework.fields import Field, empty

from .utils import get_serializer

logger = logging.getLogger(__name__)


class ModelPermissionsField(Field):

    """ Field that acts as a ModelPermissionsSerializer for relations. """

    def __init__(self, serializer, **kwargs):
        self.serializer = get_serializer(serializer)
        super(ModelPermissionsField, self).__init__(**kwargs)

    def to_representation(self, obj):
        """ Represent data for the field. """
        many = isinstance(obj, collections.Iterable) \
            or isinstance(obj, models.Manager) \
            and not isinstance(obj, dict)

        serializer_cls = get_serializer(self.serializer)

        assert serializer_cls is not None \
            and issubclass(serializer_cls, serializers.ModelSerializer), (
                "Bad serializer defined %s" % serializer_cls
            )

        ser = self.serializer(obj, context=self.context, many=many)
        return ser.data
