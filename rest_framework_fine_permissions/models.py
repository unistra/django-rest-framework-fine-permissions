# -*- coding: utf-8 -*-

"""
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class FieldPermission(models.Model):
    name = models.CharField(_('name'), max_length=100)
    content_type = models.ForeignKey(ContentType)

    class Meta:
        verbose_name = _('field permission')
        verbose_name_plural = _('fields permissions')

    def __unicode__(self):
        return '{0.content_type.app_label} | {0.content_type.model} | {0.name}'\
            .format(self)


class UserFieldPermissions(models.Model):
    user = models.OneToOneField(User)
    permissions = models.ManyToManyField(FieldPermission,
        related_name='user_field_permissions')

    class Meta:
        verbose_name = _('user field permission')
        verbose_name_plural = _('user fields permissions')

    def __unicode__(self):
        return self.user.username
