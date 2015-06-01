# -*- coding: utf-8 -*-

"""
"""

import logging
import collections

from django.db import models
from rest_framework import serializers
from rest_framework import fields

from .utils import get_serializer

logger = logging.getLogger(__name__)





class ModelPermissionsField(fields.Field):

    """ Field that acts as a ModelPermissionsSerializer for relations. """

    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
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


        class NestedModelPermissionsSerializer(serializer_cls):
            class Meta:
                model = serializer_cls.Meta.model
                depth = 0 if not hasattr(self.parent.Meta, 'depth') \
                        else self.parent.Meta.depth - 1

        options = self.parent.Meta
        if hasattr(options, 'depth') and options.depth == 0:
            ser = serializers.PrimaryKeyRelatedField(read_only=True)
        else:
            ser = NestedModelPermissionsSerializer(context=self.context,
                                                   many=many)

        return ser.to_representation(obj)


