import collections
from django.test import TestCase
from django.http import HttpRequest
from rest_framework.utils.model_meta import get_field_info

from rest_framework_fine_permissions import fields

from . import utils
from . import serializers


class ModelSerializerTestMixin(object):

    """ Mixin for testing Serializer. """

    def _auth_user(self):
        self.request.user = self.user

    def _add_field_perms(self, app, model, *field_names):
        for field_name in field_names:
            utils.add_field_permission(self.user, app,
                                       model, field_name)

    def _get_model_info(self):
        return get_field_info(self.Serializer.Meta.model)

    def _get_relation_info(self, relation_field_name):
        return self._get_model_info().relations[relation_field_name]

    def _get_serializer_instance(self, anonymous=False):
        if anonymous:
            self.Serializer(context={})
        self._auth_user()
        return self.Serializer(context={'request': self.request})


class TestModelSerializer(TestCase, ModelSerializerTestMixin):

    """ Test ModelPermissionSerializer inheriting. """

    def setUp(self):
        self.Serializer = serializers.AccountSerializer
        self.user = utils.create_user('test')
        self.request = HttpRequest()

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def test_no_request_to_instantiate(self):
        """ Test instantiation without request in context. """
        ser = self.Serializer()
        self.assertIsNone(ser.user)

    def test_default_field_names(self):
        """ Test default field names that can be accessed. """
        ser = self._get_serializer_instance()
        self.assertEqual(set(ser._get_default_field_names(ser._declared_fields,
                             self._get_model_info())),
                         {'id', 'expired_date', 'is_expired', 'cards', 'user',
                          'full_name'})

    def test_nested_class(self):
        """ Test retrieving nested relation. """
        ser = self._get_serializer_instance()
        user_relation = self._get_relation_info('user')
        user_nested_class = ser._get_nested_class(1, user_relation)
        self.assertEqual(user_nested_class.__name__,
                         'NestedModelPermissionSerializer')

    def test_depth_in_nested_class(self):
        """ Test value of depth in nested class' Meta options . """
        ser = self._get_serializer_instance()
        depth = 2
        user_relation = self._get_relation_info('user')
        user_nested_class = ser._get_nested_class(depth, user_relation)
        self.assertEqual(user_nested_class.Meta.depth, 1)

    def test_model_in_nested_class(self):
        """ Test value of model in nested class' Meta options . """
        ser = self._get_serializer_instance()
        user_relation = self._get_relation_info('user')
        user_nested_class = ser._get_nested_class(1, user_relation)

        from django.contrib.auth.models import User
        self.assertEqual(user_nested_class.Meta.model, User)

    def test_rights_on_nested_field_but_no_subfields(self):
        """ Test default building of relations with no rights on subfields. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        ser = self._get_serializer_instance()
        fields = ser.get_fields()
        self.assertEqual(fields['user'].__class__.__name__, 'NestedSerializer')

    def test_allowed_fields_with_no_rights(self):
        """ Test allowed fields with no rights defined for user. """
        ser = self._get_serializer_instance()
        fields = ser._get_user_allowed_fields()
        self.assertEqual(set(fields), set())

    def test_allowed_fields_with_some_field_rights(self):
        """ Test allowed fields with rights defined for user. """
        self._add_field_perms('tests', 'account', 'id', 'user', 'is_expired',
                              'cards')
        ser = self._get_serializer_instance()
        fields = [field.name for field in ser._get_user_allowed_fields()]
        self.assertEqual(set(fields), {'user', 'is_expired', 'id', 'cards'})

    def test_get_field_for_superuser(self):
        """ Test getting all fields for a superuser. """
        self.user.is_superuser = True
        self.user.save()
        ser = self._get_serializer_instance()
        fields = ser.get_fields()
        self.assertIsInstance(fields, collections.OrderedDict)
        self.assertEqual(set(fields), {'user', 'is_expired', 'id', 'cards',
                                       'full_name', 'expired_date'})

    def test_get_field_for_anonymous_user(self):
        """ Test getting all fields for an anonymous user. """
        ser = self._get_serializer_instance(anonymous=True)
        fields = ser.get_fields()
        self.assertIsInstance(fields, collections.OrderedDict)
        self.assertEqual(set(fields), set())

    def test_get_field_for_authenticated_user(self):
        """ Test getting fields for an authenticated user. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        ser = self._get_serializer_instance()
        fields = ser.get_fields()
        self.assertIsInstance(fields, collections.OrderedDict)
        self.assertEqual(set(fields), {'user', 'id'})


class TestNestedRelations(TestCase, ModelSerializerTestMixin):

    """ Test inner relations representation. """

    def setUp(self):
        self.Serializer = serializers.AccountSerializer
        self.user = utils.create_user('test')
        self.request = HttpRequest()

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def _get_nested_field(self, serializer, field_name):
        relation = self._get_relation_info(field_name)
        nested_class = serializer._get_nested_class(1, relation)
        return nested_class()

    def test_context_initialisation(self):
        """ Test that context is set in a good way. """
        ser = self._get_serializer_instance()
        user_nested_field = self._get_nested_field(ser, 'user')
        self.assertEqual(user_nested_field.context, ser.context)

    def test_no_rights_on_nested_subfields(self):
        """ Test with no rights on subfields. """
        ser = self._get_serializer_instance()
        user_nested_field = self._get_nested_field(ser, 'user')
        fields = user_nested_field.get_fields()
        self.assertEqual(set(fields), set())

    def test_with_rights_on_nested_subfields(self):
        """ Test with rights on subfields. """
        self._add_field_perms('tests', 'account', 'id', 'user')
        self._add_field_perms('auth', 'user', 'username')
        ser = self._get_serializer_instance()
        user_nested_field = self._get_nested_field(ser, 'user')
        fields = user_nested_field.get_fields()
        self.assertEqual(set(fields), {'username'})


class TestModelPermissionsField(TestCase, ModelSerializerTestMixin):

    """ Test with a declared field that have permissions. """

    def setUp(self):
        self.Serializer = serializers.CardSerializer
        self.user = utils.create_user('test')
        self.request = HttpRequest()

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def test_permissions_field_instance(self):
        """ Test permission field has right instance. """
        self._add_field_perms('tests', 'card', 'id', 'account')
        ser = self._get_serializer_instance()
        account = ser.get_fields()['account']
        self.assertIsInstance(account, fields.ModelPermissionsField)

    def test_permissions_field_names(self):
        """ Test field that can be accessed. """
        self._add_field_perms('tests', 'card', 'id', 'account')
        self._add_field_perms('tests', 'account', 'full_name')
        ser = self._get_serializer_instance()
        account_ser = ser.get_fields()['account'].serializer(
            context={'request': self.request}
        )
        self.assertEqual(set(account_ser.get_fields()), {'full_name'})
