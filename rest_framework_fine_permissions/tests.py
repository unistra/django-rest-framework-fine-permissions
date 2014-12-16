from django.test import TestCase
from django.db.models import Q
from rest_framework_fine_permissions.serializers import QSerializer
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions.models import FilterPermissionModel
from rest_framework_fine_permissions.permissions import FilterPermission
from django.http import HttpRequest
from rest_framework_fine_permissions.managers import FilterPermissionManager

"""

Run this test under a django application, with the following command :

python manage.py test rest_framework_fine_permissions

"""


class TestQSerializer(TestCase):
    """
    test the q serializer
    """

    def setUp(self):
        self.q1 = Q(Q(field1__contains="test") |
                    Q(rel1__field2__exact="test2") &
                    Q(Q(field3="test3") |
                      Q(field3__range=(datetime.datetime(2005, 1, 1),
                                       datetime.datetime(2005, 3, 31)))))
        self.qserializer = QSerializer()
        self.dumps = self.qserializer.dumps(self.q1)

    def test_dumps(self):
        dumps = self.qserializer.dumps(self.q1)
        self.assertEqual(dumps, self.dumps)

    def test_loads(self):
        loads = self.qserializer.loads(self.dumps)
        self.assertEqual(loads.__str__(), self.q1.__str__())

    def test_dumps_and_loads_with_other_instance(self):
        dumps = self.qserializer.dumps(self.q1)
        self.assertEqual(dumps, self.dumps)
        qserializer2 = QSerializer()
        loads = qserializer2.loads(dumps)
        self.assertEqual(loads.__str__(), self.q1.__str__())


class TestFilterPermissionModel(TestCase):
    """
    test the filter permissions model
    """

    def setUp(self):
        self.me = User.objects.create(username="morgan", password='morgan')        
        self.q = Q(Q(username='arthur') | Q(username='jean'))
        self.qserializer = QSerializer()
        self.myfilter = self.qserializer.dumps(self.q)
        self.user_ct = ContentType.objects.get_by_natural_key("auth", "user")

    def test_create(self):
        fp = FilterPermissionModel.objects.create(user=self.me,
                                                  content_type=self.user_ct,
                                                  filter=self.myfilter)
        self.assertEqual(fp.user.username, 'morgan')
        self.assertEqual(fp.content_type.name, 'user')
        self.assertEqual(fp.filter, self.myfilter)


class TestFilterPermission(TestCase):
    """
    test filter permission
    """

    def setUp(self):
        self.filterperm = FilterPermission()
        self.request = HttpRequest()
        self.me = User.objects.create(username="morgan", password='morgan')
        self.userok = User.objects.create(username="arthur", password='arthur')
        self.not_admin = User.objects.create(username="jean", password='jean')
        self.wrong = User.objects.create(username="jojo", password='jojo')
        self.admin = User.objects.create_superuser(username="admin", password="admin", email="")
        self.user_ct = ContentType.objects.get_by_natural_key("auth", "user")
        self.q = Q(Q(username='arthur') | Q(username='jean'))
        self.qserializer = QSerializer()
        self.myfilter = self.qserializer.dumps(self.q)
        self.fpm = FilterPermissionModel.objects.create(user=self.me,
                                                        content_type=self.user_ct,
                                                        filter=self.myfilter)
        self.request.user = self.me

    def test_superuser(self):
        self.request.user = self.admin
        res = self.filterperm.has_object_permission(self.request, None, None)
        self.assertTrue(res)

    def test_no_filter(self):
        self.request.user = self.not_admin
        res = self.filterperm.has_object_permission(self.request, None, self.userok)
        self.assertTrue(res)
        res = self.filterperm.has_object_permission(self.request, None, self.wrong)
        self.assertTrue(res)

    def test_obj_valid(self):
        res = self.filterperm.has_object_permission(self.request, None, self.userok)
        self.assertTrue(res)

    def test_obj_not_valid(self):
        res = self.filterperm.has_object_permission(self.request, None, self.wrong)
        self.assertFalse(res)


class TestFilterPermissionManager(TestCase):
    """
    test manager
    """

    def setUp(self):
        self.filterperm = FilterPermission()
        self.me = User.objects.create(username="morgan", password='morgan')
        self.userok = User.objects.create(username="arthur", password='arthur')
        self.not_admin = User.objects.create(username="jean", password='jean')
        self.wrong = User.objects.create(username="jojo", password='jojo')
        self.admin = User.objects.create_superuser(username="admin", password="admin", email="")
        self.user_ct = ContentType.objects.get_by_natural_key("auth", "user")
        self.q = Q(Q(username='arthur') | Q(username='jean'))
        self.qserializer = QSerializer()
        self.myfilter = self.qserializer.dumps(self.q)
        self.fpm = FilterPermissionModel.objects.create(user=self.me,
                                                        content_type=self.user_ct,
                                                        filter=self.myfilter)
        self.manager = FilterPermissionManager(user=self.me,model=User)


    def test_manager_valid(self):
        self.assertEqual(len(self.manager.all()), 2)
        self.assertEqual(self.manager.get(username='arthur'), self.userok)

    def test_manager_not_valid(self):
        self.assertEqual(len(self.manager.all()), 2)
        with self.assertRaises(User.DoesNotExist):
            self.manager.get(username='jojo')

    def test_superuser(self):
        self.manager = FilterPermissionManager(user=self.admin,model=User)
        self.assertEqual(len(self.manager.all()), 5)


    def test_no_filter(self):
        self.manager = FilterPermissionManager(user=self.not_admin,model=User)
        self.assertEqual(len(self.manager.all()), 5)

