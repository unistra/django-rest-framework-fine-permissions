from django.test import TestCase
from django.http import HttpRequest

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

    def _get_serializer_instance(self, anonymous=False):
        if anonymous:
            self.Serializer(context={})
        self._auth_user()
        return self.Serializer(context={'request': self.request})

    def test_simple_data_in_permissions_field(self):
        """ Test with a many to one field. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        self._add_field_perms('tests', 'card', 'account')

        ser = self._get_serializer_instance()
        mpf = ser.get_fields()['account']

        representation = mpf.to_representation(self.card)

        self.assertEqual(sorted(representation), ['id', 'user'])
        self.assertEqual(representation['id'], self.account.id)

    def test_list_data_in_permissions_field(self):
        """ Test with a many to one field. """
        self._add_field_perms('tests', 'card', 'id', 'service_names')
        self._add_field_perms('tests', 'service', 'name', 'id')

        service = utils.create_service('chronos')
        service2 = utils.create_service('moodle')
        self.card.services.add(service)
        self.card.services.add(service2)

        ser = self._get_serializer_instance()
        mpf = ser.get_fields()['service_names']

        representation = mpf.to_representation(self.card)

        self.assertEqual(sorted(representation[0]), ['id', 'name'])
        self.assertEqual(len(representation), 2)
        self.assertEqual(representation[0]['name'], 'chronos')

    def test_bad_configuration(self):
        """ Test bad instantiation of a model permissions field. """
        self._add_field_perms('tests', 'card', 'account_name')
        self.Serializer = serializers.BadCardSerializer

        ser = self._get_serializer_instance()
        mpf = ser.get_fields()['account_name']

        self.assertRaisesRegexp(
            AssertionError,
            "for field account_name, model Card doesn't have a field",
            mpf.to_representation,
            self.card)
