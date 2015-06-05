from django.contrib.auth.models import User
from django.test import TestCase
from django.http import HttpRequest
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

    def test_field_permissions(self):
        """ Test retrieving permissions by application. """
        user = User.objects.create_superuser('test', first_name='Beta',
                                             last_name='Tester',
                                             email='beta.tester@fail.org',
                                             password='failures!')
        request = HttpRequest()
        request.user = user
        permissions = utils.get_field_permissions(request)
        self.assertTrue('tests.account' in permissions)
        self.assertEqual(set(permissions['tests.account']),
                         {'id', 'user', 'expired_date', 'upper_full_name',
                          'is_expired', 'is_expired', 'full_name', 'wifi_group',
                          'vpn_group', 'profile'})
