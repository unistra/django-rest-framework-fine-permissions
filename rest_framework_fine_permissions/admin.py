# -*- coding: utf-8 -*-

"""
"""

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import FieldPermission, UserFieldPermissions


class UserFieldPermissionsAdmin(admin.ModelAdmin):
    filter_horizontal = ['permissions']

admin.site.register(UserFieldPermissions, UserFieldPermissionsAdmin)


class FieldPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_content_type')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(FieldPermissionAdmin, self)\
            .formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.rel.to == ContentType:
            field.label_from_instance = self.full_content_type
        return field

    def full_content_type(self, obj):
        ctype = obj if isinstance(obj, ContentType) else obj.content_type
        return '{0.app_label} | {0.name}'.format(ctype)

admin.site.register(FieldPermission, FieldPermissionAdmin)
