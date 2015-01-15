
from rest_framework_fine_permissions import serializers
from rest_framework_fine_permissions import fields
from rest_framework import serializers as drf_serializers

from .models import Account, Card, Service


class ServiceSerializer(serializers.ModelPermissionsSerializer):

    class Meta:
        model = Service


class AccountSerializer(serializers.ModelPermissionsSerializer):

    is_expired = drf_serializers.BooleanField(source='is_expired',
                                              read_only=True)
    full_name = drf_serializers.CharField(source='full_name', read_only=True)

    class Meta:
        depth = 1
        model = Account


class CardSerializer(serializers.ModelPermissionsSerializer):

    account = fields.ModelPermissionsField(AccountSerializer)
    service_names = fields.ModelPermissionsField(ServiceSerializer, source='services')

    class Meta:
        model = Card

class AnotherCardSerializer(serializers.ModelPermissionsSerializer):

    account = fields.ModelPermissionsField(AccountSerializer)
    service_names = fields.ModelPermissionsField('tests.ServiceSerializer', source='services')

    class Meta:
        model = Card

class BadCardSerializer(serializers.ModelPermissionsSerializer):

    account_name = fields.ModelPermissionsField(AccountSerializer)

    class Meta:
        model = Card


class TestNormalSerializer(drf_serializers.ModelSerializer):
    pass
