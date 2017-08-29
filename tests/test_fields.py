from django.test import TestCase
from django.http import HttpRequest
from rest_framework.exceptions import ValidationError
from rest_framework_fine_permissions.fields import (
    get_serializer, ModelPermissionsField)

from . import models
from . import serializers
from . import utils


class TestModelFieldPermissions(TestCase):

    """ Test a declared field that have permissions on subfields. """

    def setUp(self):
        self.Serializer = serializers.CardSerializer
        self.request = HttpRequest()
        self.user = utils.create_user()

        self.test_user = utils.create_user('test_data')
        self.account = utils.create_account(self.test_user)
        self.card = utils.create_card(self.account)

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()

        self.test_user.delete()
        self.account.delete()
        self.card.delete()

        del self.request

    def _add_field_perms(self, app, model, *field_names):
        for field_name in field_names:
            utils.add_field_permission(self.user, app,
                                       model, field_name)

    def _auth_user(self):
        self.request.user = self.user

    def _get_serializer_instance(self, instance=None, anonymous=False):
        if anonymous:
            self.Serializer(instance=instance, context={})
        self._auth_user()
        return self.Serializer(instance=instance,
                               context={'request': self.request})

    def test_simple_data_in_permissions_field(self):
        """ Test with a many to one field. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        self._add_field_perms('tests', 'card', 'account')

        ser = self._get_serializer_instance(instance=self.card)

        data = ser.data

        self.assertEqual(sorted(data['account']), ['id', 'user'])
        self.assertEqual(data['account']['id'], self.account.id)

    def test_list_data_in_permissions_field(self):
        """ Test with a many to one field. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        self._add_field_perms('tests', 'card', 'id', 'service_names')
        self._add_field_perms('tests', 'service', 'name', 'id')

        service = utils.create_service('chronos')
        service2 = utils.create_service('moodle')
        self.card.services.add(service)
        self.card.services.add(service2)

        ser = self._get_serializer_instance(instance=self.card)
        data = ser.data

        self.assertEqual(sorted(data['service_names'][0]), ['id', 'name'])
        self.assertEqual(len(data['service_names']), 2)
        self.assertEqual(data['service_names'][0]['name'], 'chronos')

    def test_defined_with_no_dependency(self):
        """ Test with serializer passed as a string. """
        self._add_field_perms('tests', 'card', 'account', 'service_names')
        self.Serializer = serializers.AnotherCardSerializer

        ser = self._get_serializer_instance()
        service_names = ser.get_fields()['service_names']
        self.assertEqual(service_names.serializer,
                         serializers.ServiceSerializer)

    def test_to_internal_value(self):
        field = ModelPermissionsField(
            serializers.AccountSerializer,
            queryset=models.Account.objects.all()
        )
        instance = field.to_internal_value(self.account.pk)
        self.assertEqual(instance.pk, self.account.pk)

    def test_to_internal_value_does_not_exist(self):
        field = ModelPermissionsField(
            serializers.AccountSerializer,
            queryset=models.Account.objects.all()
        )
        with self.assertRaises(ValidationError) as ve:
            field.to_internal_value(0)
        msg = ve.exception.detail[0]

        self.assertEqual('Object with pk=0 does not exist.', msg)


class TestLoadSerializer(TestCase):

    """ Test loading serializer from string. """

    def test_direct_to_serializer(self):
        """ Test with no operation to do. """
        ser = get_serializer(serializers.AccountSerializer)
        self.assertEqual(ser, serializers.AccountSerializer)

    def test_serializer_found(self):
        """ Test founding a serializer from an app label and his name. """
        ser = get_serializer('tests.AccountSerializer')
        self.assertEqual(ser, serializers.AccountSerializer)

    def test_serializer_not_found(self):
        """ Test not founding a serializer from an app label and his name. """
        ser = get_serializer('notests.AccountSerializer')
        self.assertIsNone(ser)
