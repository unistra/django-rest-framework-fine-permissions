# -*- coding: utf-8 -*-

"""
"""

import logging
import collections

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.encoding import smart_text
from rest_framework import serializers
from rest_framework.fields import Field

from .serializers import ModelPermissionsSerializer
from .utils import get_serializer

logger = logging.getLogger(__name__)


class ModelPermissionsField(Field):
    """Field that acts as a ModelPermissionsSerializer for relations. """
    default_error_messages = {
        'does_not_exist': 'Object with pk={value} does not exist.',
    }

    def __init__(self, serializer, **kwargs):
        self.queryset = kwargs.pop('queryset', None)

        super(ModelPermissionsField, self).__init__(**kwargs)
        self._serializer = serializer
        self._serializer_cls = None
        self.read_only = kwargs.get('read_only', None)

    @property
    def serializer(self):
        if not self._serializer_cls:
            self._serializer_cls = get_serializer(self._serializer)
        return self._serializer_cls

    def to_internal_value(self, data):
        assert self.queryset is not None or self.read_only, (
            'ModelPermissionsField field must provide a `queryset` argument, '
            'override `get_queryset`, or set read_only=`True`.'
        )

        if data is not None:
            try:
                return self.queryset.get(pk=data)
            except ObjectDoesNotExist:
                self.fail('does_not_exist', value=smart_text(data))

    def to_representation(self, obj):
        """ Represent data for the field. """
        many = isinstance(obj, collections.Iterable) \
            or isinstance(obj, models.Manager) \
            and not isinstance(obj, dict)

        assert self.serializer is not None \
            and issubclass(self.serializer, serializers.ModelSerializer), (
                "Bad serializer defined %s" % self.serializer
            )

        extra_params = {}
        if issubclass(self.serializer, ModelPermissionsSerializer):
            extra_params['cached_allowed_fields'] =\
                self.parent.cached_allowed_fields

        ser = self.serializer(obj, context=self.context, many=many,
                              **extra_params)
        return ser.data
