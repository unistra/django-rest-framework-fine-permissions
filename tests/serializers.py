
from rest_framework_fine_permissions import serializers
from rest_framework import serializers as drf_serializers

from .models import Account

class AccountSerializer(serializers.ModelPermissionsSerializer):

    is_expired = drf_serializers.BooleanField(source='is_expired', read_only=True)
    full_name = drf_serializers.CharField(source='full_name', read_only=True)

    class Meta:
        depth = 1
        model = Account

class TestNormalSerializer(drf_serializers.ModelSerializer):
    pass
