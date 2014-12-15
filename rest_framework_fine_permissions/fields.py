# -*- coding: utf-8 -*-

"""
"""

from rest_framework.fields import is_simple_callable
from rest_framework.fields import Field


class ModelPermissionsField(Field):
    """
    """

    def __init__(self, serializer, field='', **kwargs):
        self.serializer = serializer
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
