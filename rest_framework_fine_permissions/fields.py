# -*- coding: utf-8 -*-

"""
"""

from rest_framework.fields import is_simple_callable
from rest_framework.serializers import Field


class ModelPermissionsField(Field):
    """
    """

    def __init__(self, serializer, field=''):
        self.serializer = serializer
        self.field = field
        super(ModelPermissionsField, self).__init__()

    def field_to_native(self, obj, field_name):
        data = ''
        try:
            attr = getattr(obj, self.field or field_name)

            if is_simple_callable(getattr(attr, 'all', None)):
                attr = attr.all()

            many = hasattr(attr, '__iter__') and not isinstance(attr, dict)
            context = {'request': self.context.get('request')}
            serialized = self.serializer(attr, context=context, many=many)
            data = serialized.data
        except AttributeError:
            pass
        return self.to_native(data)
