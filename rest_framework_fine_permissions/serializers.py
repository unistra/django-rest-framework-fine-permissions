# -*- coding: utf-8 -*-

"""
"""

import base64
from collections import OrderedDict
from datetime import datetime, date
import json
import time

from django.core.serializers.base import SerializationError
from django.db.models import Q
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_relation_kwargs

from .models import FieldPermission


class ModelPermissionsSerializer(serializers.ModelSerializer):

    """ Permission on serializer's fields for an authenticated user. """

    def __init__(self, *args, **kwargs):
        """ Check context to retrive authenticated user. """

        self.cached_allowed_fields = kwargs.pop('cached_allowed_fields', {})
        super(ModelPermissionsSerializer, self).__init__(*args, **kwargs)

        # in case of a nested relation, we check context in meta options
        # of the nested class and set this for context
        # otherwise, the context is defined by the inherited serializer class.
        if not self.context:
            # Force to re-compute the context cached_property for drf<3.6
            try:
                del self.context
            except Exception:
                pass

            self._context = getattr(self.Meta, 'nested_context', {})
        try:
            self.user = self.context['request'].user
        except KeyError:
            self.user = self.context.get('user', None)

    def _get_user_allowed_fields(self):
        """ Retrieve all allowed field names ofr authenticated user. """
        model_name = self.Meta.model.__name__.lower()
        app_label = self.Meta.model._meta.app_label
        full_model_name = '%s.%s' % (app_label, model_name)
        permissions = self.cached_allowed_fields.get(full_model_name)

        if not permissions:
            permissions = FieldPermission.objects.filter(
                user_field_permissions__user=self.user,
                content_type__model=model_name,
                content_type__app_label=app_label
            )
            self.cached_allowed_fields[full_model_name] = permissions
        return permissions

    def get_fields(self):
        """ Calculate fields that can be accessed by authenticated user. """
        ret = OrderedDict()

        # no rights to see anything
        if not self.user:
            return ret

        # all fields that can be accessed through serializer
        fields = super(ModelPermissionsSerializer, self).get_fields()

        # superuser can see all the fields
        if self.user.is_superuser:
            return fields

        # fields that can be accessed by auhtenticated user
        allowed_fields = self._get_user_allowed_fields()
        for allowed_field in allowed_fields:
            field = fields[allowed_field.name]

            # subfields are NestedModelSerializer
            if isinstance(field, ModelPermissionsSerializer):
                # no rights on subfield's fields
                # calculate how the relation should be retrieved
                if not field.get_fields():
                    field_cls = field._related_class
                    kwargs = get_relation_kwargs(allowed_field.name,
                                                 field.info)
                    if not issubclass(field_cls,
                                      serializers.HyperlinkedRelatedField):
                        kwargs.pop('view_name', None)
                    field = field_cls(**kwargs)

            ret[allowed_field.name] = field
        return ret

    def _get_default_field_names(self, declared_fields, model_info):
        """ Return default field names for serializer. """
        return (
            [model_info.pk.name] +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.relations.keys())
        )

    def _get_nested_class(self, nested_depth, relation_info):
        """ Define the serializer class for a relational field. """
        class NestedModelPermissionSerializer(ModelPermissionsSerializer):

            """ Default nested class for relation. """

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                nested_context = self.context
                fields = '__all__'

        return NestedModelPermissionSerializer


class QSerializer():
    """
    A Q object serializer base class. Use json.
    """
    b64_enabled = False

    def __init__(self, base64=False):
        if base64:
            self.b64_enabled = True
        try:
            self.min_ts = time.mktime(datetime.min.timetuple())
        except OverflowError:
            # This Exception is thrown by some PC / MAC architectures which
            # can't work with dates before Epoch (01-01-1970). That's why, in
            # this case we take as minimal value the EPOCH (gmtime(0)).
            self.min_ts = time.mktime(time.gmtime(0))
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
        serialized = q.__dict__
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
