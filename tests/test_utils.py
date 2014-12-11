from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_fine_permissions import utils
from . import seralizers as test_serializers


class TestUtilities(TestCase):

    """ Test utility functions. """

    def setUp(self):
        self.serializer = test_serializers.UserSerializer
        self.normal_serializer = test_serializers.TestNormalSerializer

    def test_inherits(self):
        """ Test inherits from ModelPermissionsSerializer. """
        self.assertTrue(
            utils.inherits_modelpermissions_serializer(self.serializer)
        )

    def test_not_inherits(self):
        """ Test don't inherit from ModelPermissionsSerializer. """
        self.assertFalse(
            utils.inherits_modelpermissions_serializer(self.normal_serializer)
        )

    def test_permitted_fields(self):
        permit_fields = utils.get_permitted_fields(User, self.serializer)
        self.assertEqual(permit_fields, set(User.fields + 'is_authenticated'))
         
