import unittest
from django.db.models import Q
from rest_framework_fine_permissions.serializers import QSerializer
import datetime


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

if __name__ == '__main__':
    unittest.main()
