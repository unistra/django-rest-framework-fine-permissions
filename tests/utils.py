from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions import models

from .models import Card, Account, Service


def create_user(username='test', password='pass', **kwargs):
    """ Create a user for tests. """
    return User.objects.create_user(username, password=password, **kwargs)


def create_superuser(username='supertest', email='supertest@test.com',
                     password='pass', **kwargs):
    """ Create a user for tests. """
    return User.objects.create_superuser(username, email, password, **kwargs)


def create_account(user):
    """ Create an account for tests. """
    from datetime import datetime
    return Account.objects.create(user=user, expired_date=datetime.now())


def create_card(account):
    """ Create a card for tests. """
    return Card.objects.create(account=account)


def create_service(name):
    """ Create a service for tests. """
    return Service.objects.create(name=name)


def add_field_permission(user, app_label, model_name, field_name):
    """ Add permissions for field on an app model. """
    ct = ContentType.objects.get_by_natural_key(app_label, model_name)
    fp = models.FieldPermission.objects.create(content_type=ct,
                                               name=field_name)
    ufp = models.UserFieldPermissions.objects.get_or_create(user=user)[0]
    ufp.permissions.add(fp)


def remove_all_field_permissions(user):
    """ Remove all field permissions for user. """
    ufp = models.UserFieldPermissions.objects.filter(user=user)
    ufp.delete()
