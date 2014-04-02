# -*- coding: utf-8 -*-

"""
"""

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import RelatedField

from .models import FieldPermission


class ModelPermissionsSerializer(ModelSerializer):
    """
    """

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

        serializer = NestedModelPermissionsSerializer(many=to_many,
            context=self.context)

        if not serializer.fields:
            return RelatedField(many=to_many)

        return serializer
