# -*- coding: utf-8 -*-

"""
"""

import inspect

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_syncdb
from django.utils.importlib import import_module

from .models import FieldPermission


def _is_seralizer_subclass(cls):
    return type(cls).__name__ == 'SerializerMetaclass'


def create_field_permissions(app, verbosity, **kwargs):
    """look for serializers in serializers.py files
    """
    try:
        mod = import_module('%s.serializers' % app.__package__)
        for obj_name in dir(mod):
            obj = getattr(mod, obj_name)

            # Check if it is a serializer subclass
            if inspect.isclass(obj) and _is_seralizer_subclass(obj):
                try:
                    model = obj.Meta.model
                    field_names = model._meta.get_all_field_names()
                    ctype = ContentType.objects.get_for_model(model)

                    # Get current permissions
                    perms = FieldPermission.objects.filter(content_type=ctype)\
                        .values_list('name', flat=True)

                    # Add new permissions
                    new_names = [name for name in field_names if name not in
                            iter(perms)]
                    for name in new_names:
                        perm = FieldPermission.objects.create(
                            name=name, content_type=ctype)
                        if verbosity >= 2:
                            print("Adding field permission '%s'" % perm)

                except AttributeError:
                    pass
    except ImportError:
        return 'No serializers in "%s"' % app.__package__

post_syncdb.connect(create_field_permissions)
