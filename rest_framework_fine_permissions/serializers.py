# -*- coding: utf-8 -*-

"""
"""

from rest_framework import serializers
from .models import FieldPermission
from datetime import datetime, date
import base64
import time
from django.db.models import Q
from django.core.serializers.base import SerializationError
import msgpack


class NestedModelPermissionsSerializerOptions(serializers.ModelSerializerOptions):
    """
    """

    def __init__(self, meta):
        super(NestedModelPermissionsSerializerOptions, self).__init__(meta)
        try:
            self.nested_fields_default = getattr(meta, 'nested_fields_default')
        except AttributeError:
            self.nested_fields_default = []


class ModelPermissionsSerializer(serializers.ModelSerializer):
    """
    """

    _options_class = NestedModelPermissionsSerializerOptions

    def __init__(self, *args, **kwargs):
        super(ModelPermissionsSerializer, self).__init__(*args, **kwargs)

        user = self.context['request'].user
        model_name = self.opts.model.__name__.lower()

        if user.is_anonymous():
            allowed = set()
        elif user.is_superuser:
            allowed = FieldPermission.objects.filter(
                content_type__model=model_name)
        else:
            allowed = FieldPermission.objects.filter(
                user_field_permissions__user=user,
                content_type__model=model_name)
        allowed = set(allowed.values_list('name', flat=True))
        existing = set(self.fields.keys())

        for field_name in existing - allowed:
            self.fields.pop(field_name)

    def get_nested_field(self, model_field, related_model, to_many):
        """
        """

        class NestedModelPermissionsSerializer(ModelPermissionsSerializer):
            class Meta:
                model = related_model
                depth = self.opts.depth - 1
                nested_fields_default = self.opts.nested_fields_default

        serializer = NestedModelPermissionsSerializer(many=to_many,
            context=self.context)

        if not serializer.fields:
            for field_name, rel_type in self.opts.nested_fields_default:
                if field_name == model_field.name:
                    return rel_type(many=to_many)

            return serializers.RelatedField(many=to_many)

        return serializer


class QSerializer(object):
    """
    A Q object serializer base class. Use msgpack.
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

    def get_field_values_list(self, d):
        """
        Iterate over a (possibly nested) dict, and return a list
        of all children queries, as a dict of the following structure:
        {
            'field': 'some_field__iexact',
            'value': 'some_value',
            'value_from': 'optional_range_val1',
            'value_to': 'optional_range_val2',
            'negate': True,
        }

        OR relations are expressed as an extra "line" between queries.
        """
        fields = []
        children = d.get('children', [])
        for child in children:
            if isinstance(child, dict):
                fields.extend(self.get_field_values_list(child))
            else:
                f = {'field': child[0], 'value': child[1]}
                if self._is_range(child):
                    f['value_from'] = child[1][0]
                    f['value_to'] = child[1][1]
                f['negate'] = d.get('negated', False)
                fields.append(f)

            # add _OR line
            if d['connector'] == 'OR' and children[-1] != child:
                fields.append({'field': '_OR', 'value': 'null'})
        return fields

    def dumps(self, obj):
        if not isinstance(obj, Q):
            raise SerializationError
        string = msgpack.dumps(self.serialize(obj), default=self.dt2ts)
        if self.b64_enabled:
            return base64.b64encode(string)
        return string

    def loads(self, string, raw=False):
        encoding = 'utf-8'
        if isinstance(string, str):
            encoding = None
        if self.b64_enabled:
            d = msgpack.loads(base64.b64decode(string), encoding=encoding)
        else:
            d = msgpack.loads(string, encoding=encoding)
        if raw:
            return d
        return self.deserialize(d)

