from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions import models


def create_user(username='test', **kwargs):
    return User.objects.create_user(username, **kwargs)


def add_field_permission(user, app_label, model_name, field_name):
    ct = ContentType.objects.get_by_natural_key(app_label, model_name)
    fp = models.FieldPermission.objects.create(content_type=ct,
                                               name=field_name)
    ufp = models.UserFieldPermissions.objects.get_or_create(user=user)[0]
    ufp.permissions.add(fp)
