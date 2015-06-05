""" Test serializers. """

from collections import OrderedDict
from datetime import date
from django.test import TestCase
from django.http import HttpRequest
from rest_framework.utils.model_meta import get_field_info

from rest_framework import serializers as drf_serializers
from rest_framework_fine_permissions import fields, serializers

from .serializers import AccountSerializer
from .serializers import AccountWithFieldsSerializer
from .serializers import AccountWithExcludeSerializer
from . import utils
from . import models


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


class TestSimpleModelSerializer(TestCase, ModelSerializerTestMixin):

    """ Test a simple serializer.

    Only tests.serializers.AccountSerializer is used.
    """

    def setUp(self):
        self.Serializer = AccountSerializer
        self.user = utils.create_user('test', first_name='Beta',
                                      last_name='Tester')
        self.request = HttpRequest()
        self.account = models.Account.objects.create(user=self.user,
                                                     expired_date=date.today())

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def test_no_request_to_instantiate(self):
        """ Test instantiation without request in context. """
        ser = self.Serializer()
        self.assertIsNone(ser.user)

    def test_no_right_on_fields(self):
        """ Test default field names that can be accessed. """
        ser = self._get_serializer_instance()
        self.assertEqual(ser.get_fields(), {})
        self.assertEqual(ser.to_representation(self.account), {})

    def test_with_right_on_normal_field(self):
        """ Test rights given on a model field. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'expired_date')
        self.assertEqual(list(ser.get_fields().keys()), ['expired_date'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('expired_date', date.today().strftime('%Y-%m-%d'))])
        )

    def test_with_property_as_a_field(self):
        """ Test rights given on a property field. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'full_name')
        self.assertEqual(list(ser.get_fields().keys()), ['full_name'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('full_name', 'Beta Tester')])
        )

    def test_with_a_method_on_model(self):
        """ Test with the result of a model method as a serializer field. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'is_expired')
        self.assertEqual(list(ser.get_fields().keys()), ['is_expired'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('is_expired', False)])
        )

    def test_with_a_method_on_serializer(self):
        """ Test with a serializer method. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'upper_full_name')
        self.assertEqual(list(ser.get_fields().keys()), ['upper_full_name'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('upper_full_name', 'BETA TESTER')])
        )

    def test_with_a_nested_field_and_no_rights_on_it(self):
        """ Test with a relation on model, no rights on it and depth option. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'user')
        self.assertEqual(list(ser.get_fields().keys()), ['user'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('user', {})])
        )

    def test_with_a_nested_field_and_rights_on_it(self):
        """ Test with a relation on model, rights on it and depth option. """
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'user')
        self._add_field_perms('auth', 'user', 'username')
        self.assertEqual(list(ser.get_fields().keys()), ['user'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('user', OrderedDict([('username', 'test')]))])
        )

    def test_with_a_relational_field_and_no_rights_on_it(self):
        """ Test with a relation on model, no rights on it and depth option. """
        del self.Serializer.Meta.depth
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'user')
        self.assertEqual(list(ser.get_fields().keys()), ['user'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('user', 1)])
        )
        self.Serializer.Meta.depth = 1

    def test_with_a_relational_field_and_rights_on_it(self):
        """ Test with a relation on model, rights on it and depth option. """
        del self.Serializer.Meta.depth
        ser = self._get_serializer_instance()
        self._add_field_perms('tests', 'account', 'user')
        self._add_field_perms('auth', 'user', 'username')
        self.assertEqual(list(ser.get_fields().keys()), ['user'])
        self.assertEqual(
            ser.to_representation(self.account),
            OrderedDict([('user', 1)])
        )
        self.Serializer.Meta.depth = 1


class TestSimpleSerializerWithFieldsOption(TestCase, ModelSerializerTestMixin):

    """ Test with fields defined in Meta options. """

    def setUp(self):
        self.Serializer = AccountWithFieldsSerializer
        self.user = utils.create_user('test', first_name='Beta',
                                      last_name='Tester')
        self.request = HttpRequest()
        self.account = models.Account.objects.create(user=self.user,
                                                     expired_date=date.today())

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def test_with_all_perms_on_authorized_fields(self):
        """ Test with perms on each fields declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'full_name', 'is_expired', 'profile', 'user'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['full_name', 'id', 'is_expired', 'profile', 'user'])

    def test_with_less_perms_on_authorized_fields(self):
        """ Test with perms on less fields declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'is_expired', 'user'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['id', 'is_expired', 'user'])

    def test_with_perms_on_not_authorized_fields(self):
        """ Test with perms on fields not declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'is_expired', 'user', 'upper_full_name'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['id', 'is_expired', 'user'])


class TestSimpleSerializerWithExcludeOption(TestCase, ModelSerializerTestMixin):

    """ Test with fields defined in Meta options. """

    def setUp(self):
        self.Serializer = AccountWithExcludeSerializer
        self.user = utils.create_user('test', first_name='Beta',
                                      last_name='Tester')
        self.request = HttpRequest()
        self.account = models.Account.objects.create(user=self.user,
                                                     expired_date=date.today())

    def tearDown(self):
        utils.remove_all_field_permissions(self.user)
        self.user.delete()
        del self.request

    def test_with_all_perms_on_authorized_fields(self):
        """ Test with perms on each fields declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'full_name', 'is_expired', 'profile', 'user'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['full_name', 'id', 'is_expired', 'profile', 'user'])

    def test_with_less_perms_on_authorized_fields(self):
        """ Test with perms on less fields declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'is_expired', 'user'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['id', 'is_expired', 'user'])

    def test_with_perms_on_not_authorized_fields(self):
        """ Test with perms on fields not declared in Meta options. """
        ser = self._get_serializer_instance()
        for field in ('id', 'is_expired', 'user', 'upper_full_name'):
            self._add_field_perms('tests', 'account', field)
        self.assertEqual(sorted(ser.get_fields().keys()),
                         ['id', 'is_expired', 'user'])

#
# class TestModelSerializer(TestCase, ModelSerializerTestMixin):
#
#     """ Test ModelPermissionSerializer inheriting. """
#
#     def setUp(self):
#         self.Serializer = serializers.AccountSerializer
#         self.user = utils.create_user('test')
#         self.request = HttpRequest()
#
#     def tearDown(self):
#         utils.remove_all_field_permissions(self.user)
#         self.user.delete()
#         del self.request
#
#     def test_no_request_to_instantiate(self):
#         """ Test instantiation without request in context. """
#         ser = self.Serializer()
#         self.assertIsNone(ser.user)
#
#     def test_default_field_names(self):
#         """ Test default field names that can be accessed. """
#         ser = self._get_serializer_instance()
#         self.assertEqual(set(ser._get_default_field_names(ser._declared_fields,
#                              self._get_model_info())),
#                          {'id', 'expired_date', 'is_expired', 'cards', 'user',
#                           'full_name'})
#
#     def test_nested_class(self):
#         """ Test retrieving nested relation. """
#         ser = self._get_serializer_instance()
#         user_relation = self._get_relation_info('user')
#         user_nested_class = ser._get_nested_class(1, user_relation)
#         self.assertEqual(user_nested_class.__name__,
#                          'NestedModelPermissionSerializer')
#
#     def test_depth_in_nested_class(self):
#         """ Test value of depth in nested class' Meta options . """
#         ser = self._get_serializer_instance()
#         depth = 2
#         user_relation = self._get_relation_info('user')
#         user_nested_class = ser._get_nested_class(depth, user_relation)
#         self.assertEqual(user_nested_class.Meta.depth, 1)
#
#     def test_model_in_nested_class(self):
#         """ Test value of model in nested class' Meta options . """
#         ser = self._get_serializer_instance()
#         user_relation = self._get_relation_info('user')
#         user_nested_class = ser._get_nested_class(1, user_relation)
#
#         from django.contrib.auth.models import User
#         self.assertEqual(user_nested_class.Meta.model, User)
#
#     def test_rights_on_nested_field_but_no_subfields(self):
#         """ Test default building of relations with no rights on subfields. """
#         self._add_field_perms('tests', 'account', 'id', 'user')
#         ser = self._get_serializer_instance()
#         fields = ser.get_fields()
#         self.assertIsInstance(fields['user'], ser._related_class)
#
#     def test_allowed_fields_with_no_rights(self):
#         """ Test allowed fields with no rights defined for user. """
#         ser = self._get_serializer_instance()
#         fields = ser._get_user_allowed_fields()
#         self.assertEqual(set(fields), set())
#
#     def test_allowed_fields_with_some_field_rights(self):
#         """ Test allowed fields with rights defined for user. """
#         self._add_field_perms('tests', 'account', 'id', 'user', 'is_expired',
#                               'cards')
#         ser = self._get_serializer_instance()
#         fields = [field.name for field in ser._get_user_allowed_fields()]
#         self.assertEqual(set(fields), {'user', 'is_expired', 'id', 'cards'})
#
#     def test_get_field_for_superuser(self):
#         """ Test getting all fields for a superuser. """
#         self.user.is_superuser = True
#         self.user.save()
#         ser = self._get_serializer_instance()
#         fields = ser.get_fields()
#         self.assertIsInstance(fields, collections.OrderedDict)
#         self.assertEqual(set(fields), {'user', 'is_expired', 'id', 'cards',
#                                        'full_name', 'expired_date'})
#
#     def test_get_field_for_anonymous_user(self):
#         """ Test getting all fields for an anonymous user. """
#         ser = self._get_serializer_instance(anonymous=True)
#         fields = ser.get_fields()
#         self.assertIsInstance(fields, collections.OrderedDict)
#         self.assertEqual(set(fields), set())
#
#     def test_get_field_for_authenticated_user(self):
#         """ Test getting fields for an authenticated user. """
#         self._add_field_perms('tests', 'account', 'id', 'user')
#         ser = self._get_serializer_instance()
#         fields = ser.get_fields()
#         self.assertIsInstance(fields, collections.OrderedDict)
#         self.assertEqual(set(fields), {'user', 'id'})
#
#
# class TestNestedRelations(TestCase, ModelSerializerTestMixin):
#
#     """ Test inner relations representation. """
#
#     def setUp(self):
#         self.Serializer = serializers.AccountSerializer
#         self.user = utils.create_user('test')
#         self.request = HttpRequest()
#
#     def tearDown(self):
#         utils.remove_all_field_permissions(self.user)
#         self.user.delete()
#         del self.request
#
#     def _get_nested_field(self, serializer, field_name):
#         relation = self._get_relation_info(field_name)
#         nested_class = serializer._get_nested_class(1, relation)
#         return nested_class()
#
#     def test_context_initialisation(self):
#         """ Test that context is set in a good way. """
#         ser = self._get_serializer_instance()
#         user_nested_field = self._get_nested_field(ser, 'user')
#         self.assertEqual(user_nested_field.context, ser.context)
#
#     def test_no_rights_on_nested_subfields(self):
#         """ Test with no rights on subfields. """
#         ser = self._get_serializer_instance()
#         user_nested_field = self._get_nested_field(ser, 'user')
#         fields = user_nested_field.get_fields()
#         self.assertEqual(set(fields), set())
#
#     def test_with_rights_on_nested_subfields(self):
#         """ Test with rights on subfields. """
#         self._add_field_perms('tests', 'account', 'id', 'user')
#         self._add_field_perms('auth', 'user', 'username')
#         ser = self._get_serializer_instance()
#         user_nested_field = self._get_nested_field(ser, 'user')
#         fields = user_nested_field.get_fields()
#         self.assertEqual(set(fields), {'username'})
#
#
# class TestModelPermissionsField(TestCase, ModelSerializerTestMixin):
#
#     """ Test with a declared field that have permissions. """
#
#     def setUp(self):
#         self.Serializer = serializers.CardSerializer
#         self.user = utils.create_user('test')
#         self.request = HttpRequest()
#
#     def tearDown(self):
#         utils.remove_all_field_permissions(self.user)
#         self.user.delete()
#         del self.request
#
#     def test_permissions_field_instance(self):
#         """ Test permission field has right instance. """
#         self._add_field_perms('tests', 'card', 'id', 'account')
#         ser = self._get_serializer_instance()
#         account = ser.get_fields()['account']
#         self.assertIsInstance(account, fields.ModelPermissionsField)
#
#     def test_permissions_field_names(self):
#         """ Test field that can be accessed. """
#         self._add_field_perms('tests', 'card', 'id', 'account')
#         self._add_field_perms('tests', 'account', 'full_name')
#         ser = self._get_serializer_instance()
#         account_ser = ser.get_fields()['account'].serializer(
#             context={'request': self.request}
#         )
#         self.assertEqual(set(account_ser.get_fields()), {'full_name'})
