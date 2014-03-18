# -*- coding: utf-8 -*-

"""
"""

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
            context = {'request': self.context.get('request')}
            serialized = self.serializer(attr, context=context)
            data = serialized.data
        except AttributeError:
            pass
        return self.to_native(data)
