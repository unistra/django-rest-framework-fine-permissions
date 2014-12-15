# -*- coding: utf-8 -*-

"""
"""

from collections import OrderedDict
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_relation_kwargs
from .models import FieldPermission
from .fields import ModelPermissionsField


class ModelPermissionsSerializer(serializers.ModelSerializer):

    """ Permission on serializer's fields for an authenticated user. """

    def __init__(self, *args, **kwargs):
        """ Check context to retrive authenticated user. """
        super(ModelPermissionsSerializer, self).__init__(*args, **kwargs)
        # in case of a nested relation, we check context in meta options
        # of the nested class and set this for context
        # otherwise, the context is defined by the inherited serializer class.
        if not self.context:
            self._context = getattr(self.Meta, 'nested_context', {})
        try:
            self.user = self.context['request'].user
        except KeyError:
            self.user = None

    def _get_user_allowed_fields(self):
        """ Retrieve all allowed field names ofr authenticated user. """
        model_name = self.Meta.model.__name__.lower()
        return FieldPermission.objects.filter(
            user_field_permissions__user=self.user,
            content_type__model=model_name
        )

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

            if isinstance(field, ModelPermissionsField):
                field.bind(allowed_field.name, self)

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

            is_nested = True
            info = relation_info

            class Meta:
                model = relation_info.related
                depth = nested_depth - 1
                nested_context = self.context

        return NestedModelPermissionSerializer
