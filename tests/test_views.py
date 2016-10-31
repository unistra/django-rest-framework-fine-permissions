import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from django.test import TestCase

from rest_framework_fine_permissions.models import UserFieldPermissions
from . import utils


class TestViews(TestCase):

    """ Test views. """

    def setUp(self):
        self.request = HttpRequest()
        self.superuser = utils.create_superuser()
        self.user = utils.create_user()

    def _add_field_perms(self, app, model, *field_names):
        for field_name in field_names:
            utils.add_field_permission(self.user, app,
                                       model, field_name)

    def test_permissions_export_json_unauthorized(self):
        self._add_field_perms('tests', 'account', 'id', 'user')
        self.client.login(username='test', password='pass')
        ufp = UserFieldPermissions.objects.get(user=self.user)

        response = self.client.get('/drffp/export/%s/' % ufp.pk)
        self.assertEqual(response.status_code, 302)

    def test_permissions_export_json_without_permissions(self):
        self.client.login(username='supertest', password='pass')

        response = self.client.get('/drffp/export/%s/' % 1000)
        self.assertEqual(response.status_code, 404)

    def test_permissions_export_json(self):
        self._add_field_perms('tests', 'account', 'id', 'user')
        self.client.login(username='supertest', password='pass')
        ufp = UserFieldPermissions.objects.get(user=self.user)

        response = self.client.get('/drffp/export/%s/' % ufp.pk)
        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['username'], 'test')
        self.assertListEqual(
            json_response['fields_permissions'],
            [
                {'app_label': 'tests', 'model': 'account', 'name': 'id'},
                {'app_label': 'tests', 'model': 'account', 'name': 'user'},
            ]
        )

    def test_permissions_import_json_missing_file(self):
        self.client.login(username='supertest', password='pass')
        self._add_field_perms('tests', 'account', 'expired_date')
        ufp = UserFieldPermissions.objects.get(user=self.user)

        response = self.client.post('/drffp/import/%s/' % ufp.pk)
        self.assertTrue(
            'Missing imported file' in format(response.cookies['messages']))
        self.assertEqual(response.status_code, 302)

    def test_permissions_import_json_wrong_user(self):
        self.client.login(username='supertest', password='pass')
        self._add_field_perms('tests', 'account', 'expired_date')
        ufp = UserFieldPermissions.objects.get(user=self.user)
        permissions_str = """
        {
            "username": "supertest",
            "fields_permissions": [
                {"app_label": "tests", "model": "account", "name": "id"},
                {"app_label": "tests", "model": "account", "name": "user"}
            ]
        }"""

        f = SimpleUploadedFile('file.txt', permissions_str.encode('utf-8'),
                               content_type='application/json')
        response = self.client.post('/drffp/import/%s/' % ufp.pk,
                                    {'perms_upload': f})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            'The wrong user is defined in the imported file' in\
                format(response.cookies['messages']))

    def test_permissions_import_json_exception(self):
        self.client.login(username='supertest', password='pass')
        self._add_field_perms('tests', 'account', 'expired_date')
        ufp = UserFieldPermissions.objects.get(user=self.user)
        permissions_str = 'empty'

        f = SimpleUploadedFile('file.txt', permissions_str.encode('utf-8'),
                               content_type='application/json')
        response = self.client.post('/drffp/import/%s/' % ufp.pk,
                                    {'perms_upload': f})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            'Error in the import' in format(response.cookies['messages']))

    def test_permissions_import_json_with_user_field_permissions(self):
        self.client.login(username='supertest', password='pass')
        self._add_field_perms('tests', 'account', 'expired_date')
        ufp = UserFieldPermissions.objects.get(user=self.user)
        permissions_str = """
        {
            "username": "test",
            "fields_permissions": [
                {"app_label": "tests", "model": "account", "name": "id"},
                {"app_label": "tests", "model": "account", "name": "user"}
            ]
        }"""

        f = SimpleUploadedFile('file.txt', permissions_str.encode('utf-8'),
                               content_type='application/json')
        response = self.client.post('/drffp/import/%s/' % ufp.pk,
                                    {'perms_upload': f})
        ufp = UserFieldPermissions.objects.get(user=self.user)
        permissions = ufp.permissions.all()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            'Permissions imported' in format(response.cookies['messages']))
        self.assertEqual(len(permissions), 2)
        self.assertListEqual(
            [str(p) for p in permissions],
            ['tests | account | id', 'tests | account | user']
        )

    def test_permissions_import_json_without_user_field_permissions(self):
        self.client.login(username='supertest', password='pass')
        permissions_str = """
        {
            "username": "test",
            "fields_permissions": [
                {"app_label": "tests", "model": "account", "name": "id"},
                {"app_label": "tests", "model": "account", "name": "user"}
            ]
        }"""
        f = SimpleUploadedFile('file.txt', permissions_str.encode('utf-8'),
                               content_type='application/json')
        response = self.client.post('/drffp/import/', {'perms_upload': f})
        ufp = UserFieldPermissions.objects.get(user=self.user)
        permissions = ufp.permissions.all()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            'Permissions imported' in format(response.cookies['messages']))
        self.assertEqual(len(permissions), 2)
        self.assertListEqual(
            [str(p) for p in permissions],
            ['tests | account | id', 'tests | account | user']
        )
