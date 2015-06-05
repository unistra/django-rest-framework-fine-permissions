# -*- coding: utf-8 -*-

"""
"""

import base64
from datetime import datetime, date
import json
import time
import copy

from django.core.serializers.base import SerializationError
from django.db.models import Q
from rest_framework import serializers
from rest_framework.compat import OrderedDict
from rest_framework.utils import model_meta
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from rest_framework.utils.field_mapping import get_relation_kwargs
from rest_framework.utils.serializer_helpers import BindingDict

from .models import FieldPermission
from .fields import ModelPermissionsField


class ModelPermissionsSerializer(serializers.ModelSerializer):

    """ Permission on serializer's fields for an authenticated user. """

    serializer_permission_field = ModelPermissionsField

    def __init__(self, *args, **kwargs):
        """ Check context to retrive authenticated user. """
        super(ModelPermissionsSerializer, self).__init__(*args, **kwargs)
        # in case of a nested relation, we check context in meta options
        # of the nested class and set this for context
        # otherwise, the context is defined by the inherited serializer class.
        try:
            self.user = self.context['request'].user
        except KeyError:
            self.user = None

    def get_model_permissions_fields(self):
        declared_fields = copy.deepcopy(self._declared_fields)
        if not hasattr(self, '_model_permissions_fields'):
            self._model_permissions_fields = OrderedDict({
                field_name: field
                for field_name, field in declared_fields.items()
                if isinstance(field, self.serializer_permission_field)
            })
        return self._model_permissions_fields

    def get_field_names(self, declared_fields, info):
        fields = super(ModelPermissionsSerializer, self).get_field_names(
            declared_fields, info
        )
        if not self.user:
            fields = []
        elif not self.user.is_superuser:
            allowed = set(
                self._get_user_allowed_fields().values_list('name', flat=True)
            )
            if not allowed:
                fields = []
            else:
                fields = list(set(fields).intersection(allowed))
        permission_fields = self.get_model_permissions_fields()
        return [
            field for field in fields
            if field not in permission_fields.keys()
        ]

    def get_fields(self):
        fields = super(ModelPermissionsSerializer, self).get_fields()

        info = model_meta.get_field_info(getattr(self.Meta, 'model'))
        permissions_fields = self.get_model_permissions_fields()

        for field_name, field in permissions_fields.items():
            source = field.source
            if source is not None and source != field_name:
                relation_info = info.relations[source]
            else:
                relation_info = info.relations[field_name]
            field_cls, field_kwargs = self.build_permissions_fields(
                field_name, field, relation_info
            )

            field_instance = field_cls(**field_kwargs)

            # retrieve the real serializer in fact of many
            if isinstance(field_instance, serializers.ListSerializer):
                serializer_instance = field_instance.child
            else:
                serializer_instance = field_instance

            # avoid cyclic model permissions fields
            if not isinstance(serializer_instance, type(self.root)):
                fields[field_name] = field_instance

        return fields

    def _get_user_allowed_fields(self):
        """ Retrieve all allowed field names for authenticated user. """
        return FieldPermission.objects.get_allowed_fields(self.user,
                                                          self.Meta.model)

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """ Define the serializer class for a relational field. """

        class NestedModelPermissionSerializer(ModelPermissionsSerializer):

            """ Default nested class for relation. """

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1

        field_class = NestedModelPermissionSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        field_kwargs.update({'context': self.context})

        return field_class, field_kwargs


    def build_permissions_fields(self, field_name, field_instance,
                                 relation_info):


        field_kwargs = get_relation_kwargs(field_name, relation_info)

        field_kwargs.pop('view_name', None)
        field_kwargs.pop('queryset', None)
        field_kwargs.update({'context': self.context,
                             'source': field_instance.source})

        return field_instance.serializer_cls, field_kwargs


class QSerializer():
    """
    A Q object serializer base class. Use json.
    """
    b64_enabled = False

    def __init__(self, base64=False):
        if base64:
            self.b64_enabled = True
        self.min_ts = time.mktime(datetime.min.timetuple())
        self.max_ts = time.mktime((3000,) + (0,) * 8)
        self.dt2ts = lambda obj: time.mktime(obj.timetuple()) if isinstance(
            obj, date) else obj

    @staticmethod
    def _is_range(qtuple):
        return qtuple[0].endswith("__range") and len(qtuple[1]) == 2

    def prepare_value(self, qtuple):
        if self._is_range(qtuple):
            qtuple[1][0] = qtuple[1][0] or self.min_ts
            qtuple[1][1] = qtuple[1][1] or self.max_ts
            qtuple[1] = (datetime.fromtimestamp(qtuple[1][0]),
                         datetime.fromtimestamp(qtuple[1][1]))
        return tuple(qtuple)

    def serialize(self, q):
        """
        Serialize a Q object into a (possibly nested) dict.
        """
        children = []
        for child in q.children:
            if isinstance(child, Q):
                children.append(self.serialize(child))
            else:
                children.append(child)
        serialized = q.clone().__dict__
        serialized['children'] = children
        return serialized

    def deserialize(self, d):
        """
        De-serialize a Q object from a (possibly nested) dict.
        """
        children = []
        for child in d.pop('children'):
            if isinstance(child, dict):
                children.append(self.deserialize(child))
            else:
                children.append(self.prepare_value(child))
        query = Q()
        query.children = children
        query.connector = d['connector']
        query.negated = d['negated']
        if 'subtree_parents' in d:
            query.subtree_parents = d['subtree_parents']
        return query

    def dumps(self, obj):
        if not isinstance(obj, Q):
            raise SerializationError
        string = json.dumps(self.serialize(obj), default=self.dt2ts,
                            sort_keys=True,
                            indent=4, separators=(',', ': '))
        if self.b64_enabled:
            return base64.b64encode(string.encode('utf-8')).decode('utf-8')
        return string

    def loads(self, string, raw=False):
        if self.b64_enabled:
            d = json.loads(base64.b64decode(string).decode('utf-8'))
        else:
            d = json.loads(string)
        if raw:
            return d
        return self.deserialize(d)
