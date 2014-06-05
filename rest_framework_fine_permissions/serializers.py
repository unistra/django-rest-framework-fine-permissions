# -*- coding: utf-8 -*-

"""
"""

from rest_framework import serializers
from .models import FieldPermission


class NestedModelPermissionsSerializerOptions(serializers.ModelSerializerOptions):
    """
    """

    def __init__(self, meta):
        super(NestedModelPermissionsSerializerOptions, self).__init__(meta)
        self.nested_fields_default = getattr(meta, 'nested_fields_default')


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
