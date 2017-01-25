# -*- coding: utf-8 -*-

"""
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class FieldPermission(models.Model):
    name = models.CharField(_('name'), max_length=255)
    content_type = models.ForeignKey(ContentType)

    class Meta:
        verbose_name = _('field permission')
        verbose_name_plural = _('fields permissions')
        db_table = 'drf_field_permission'

    def __str__(self):
        return '{0.content_type.app_label} | {0.content_type.model} | {0.name}'\
            .format(self)


@python_2_unicode_compatible
class UserFieldPermissions(models.Model):
    user = models.OneToOneField(User)
    permissions = models.ManyToManyField(
        FieldPermission,
        related_name='user_field_permissions',
        db_table='drf_user_field_permissions_permission')

    class Meta:
        verbose_name = _('user field permission')
        verbose_name_plural = _('user fields permissions')
        db_table = 'drf_user_field_permissions'

    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class FilterPermissionModel(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    filter = models.TextField()

    class Meta:
        verbose_name = _('user filter permission')
        verbose_name_plural = _('user filters permissions')
        db_table = 'drf_user_filter_permissions'
        unique_together = ('user', 'content_type',)

    def __str__(self):
        return '{0.content_type.app_label} | {0.content_type.model} | {0.user.username} | {0.filter}'\
            .format(self)
