from django.test import TestCase
from rest_framework_fine_permissions import utils
from . import serializers as test_serializers
from .models import Account


class TestUtilities(TestCase):

    """ Test utility functions. """

    def setUp(self):
        self.account_ser = test_serializers.AccountSerializer
        self.normal_ser = test_serializers.TestNormalSerializer

    def test_inherits(self):
        """ Test inherits from ModelPermissionsSerializer. """
        self.assertTrue(
            utils.inherits_modelpermissions_serializer(self.account_ser)
        )

    def test_not_inherits(self):
        """ Test don't inherit from ModelPermissionsSerializer. """
        self.assertFalse(
            utils.inherits_modelpermissions_serializer(self.normal_ser)
        )

    def test_model_retrieving_model_fields(self):
        """ Test field names extracted from the model. """
        model_fields = ('id', 'user', 'expired_date', 'cards')
        self.assertEqual(set(utils.get_model_fields(Account)),
                         set(model_fields))

    def test_permitted_fields(self):
        """ Test list of fields displayed in admin interface. """
        permit_fields = utils.get_permitted_fields(Account, self.account_ser)
        model_fields = ('id', 'user', 'expired_date', 'cards')
        serializer_fields = ('is_expired', 'full_name')
        self.assertEqual(
            set(permit_fields.keys()), set(model_fields + serializer_fields))

    def test_field_permissions(self):
        """ Test retrieving permissions by application. """
        permissions = utils.get_field_permissions()
        self.assertTrue('tests.account' in permissions)
        self.assertEqual(
            set(permissions['tests.account'][0].keys()),
            {
                'id', 'user', 'expired_date', 'cards', 'is_expired',
                'expired_date', 'full_name'
            })
