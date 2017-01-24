# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework_fine_permissions.admin import UserFieldPermissionsForm
from rest_framework_fine_permissions.models import UserFieldPermissions


class TestUserFieldPermissionsForm(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test_user')

    def test_user_field_permissions_form_save(self):
        data = {
            'user': self.user.pk,
            'permissions': ['tests.account.cards', 'tests.service.name']
        }
        form = UserFieldPermissionsForm(data=data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertIsNotNone(
            UserFieldPermissions.objects.get(pk=form.instance.pk))

    def test_user_field_permissions_form_with_conflicts(self):
        data = {
            'user': self.user.pk,
            'permissions': ['tests.account.cards', 'tests.card.account']
        }
        form = UserFieldPermissionsForm(data=data)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())

        error = str(form.errors.get('__all__')[0])
        self.assertIn('Recursive ModelPermissionsField call between', error)
        self.assertIn('tests.account.cards', error)
        self.assertIn('tests.card.account', error)
