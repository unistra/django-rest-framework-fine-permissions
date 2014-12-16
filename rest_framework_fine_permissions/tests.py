import unittest
from django.db.models import Q
from rest_framework_fine_permissions.serializers import QSerializer
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions.models import FilterPermissionModel

"""

Run this test under a django application, with the following command :

python manage.py test rest_framework_fine_permissions

"""


class TestQSerializer(unittest.TestCase):
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


class TestFilterPermissionModel(unittest.TestCase):
    """
    test the filter permissions model
    """

    def setUp(self):
        self.me = User.objects.create(username="morgan", password='morgan')
        self.user1 = User.objects.create(username="arthur", password='arthur')
        self.user2 = User.objects.create(username="jean", password='jean')
        self.user_ct = ContentType.objects.get_by_natural_key("auth", "user")
        self.q = Q(Q(username='arthur') | Q(username='jean'))
        self.qserializer = QSerializer()
        self.myfilter = self.qserializer.dumps(self.q)

    def test_create(self):
        fp = FilterPermissionModel.objects.create(user=self.me,
                                                  content_type=self.user_ct,
                                                  filter=self.myfilter)
        self.assertEqual(fp.user.username, 'morgan')
        self.assertEqual(fp.content_type.name, 'user')
        self.assertEqual(fp.filter, self.myfilter)

