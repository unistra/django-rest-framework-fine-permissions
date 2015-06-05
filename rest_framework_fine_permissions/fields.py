# -*- coding: utf-8 -*-

"""
"""

import logging
import collections

from django.db import models
from rest_framework.serializers import PrimaryKeyRelatedField, ModelSerializer
from rest_framework import fields
from rest_framework import relations

from .utils import get_serializer

logger = logging.getLogger(__name__)


class ModelPermissionsField(fields.Field):

    """ Field that acts as a ModelPermissionsSerializer for relations. """

    def __init__(self, serializer, default_serializer=None, **kwargs):
        super(ModelPermissionsField, self).__init__(**kwargs)
        self.serializer_cls = get_serializer(serializer)
        self.default_serializer = default_serializer or PrimaryKeyRelatedField
