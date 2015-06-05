
from rest_framework_fine_permissions import serializers
from rest_framework_fine_permissions import fields
from rest_framework import serializers as drf_serializers

from .models import Account, Card, Service


class AccountSerializer(serializers.ModelPermissionsSerializer):

    """ Base serializer for tests. """

    is_expired = drf_serializers.BooleanField(read_only=True)
    full_name = drf_serializers.CharField(read_only=True)
    upper_full_name = drf_serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = Account

    def get_upper_full_name(self, obj):
        return obj.full_name.upper()


class AccountWithFieldsSerializer(AccountSerializer):

    """ Inherit AccountSerializer and define the fields Meta option. """

    class Meta(AccountSerializer.Meta):
        fields = ('id', 'full_name', 'is_expired', 'profile', 'user')


class AccountWithExcludeSerializer(AccountSerializer):

    """ Inherit AccountSerializer and define the fields Meta option. """

    class Meta(AccountSerializer.Meta):
        exclude = ('expired_date', 'upper_full_name')


class AccountWithModelPermissionsField(AccountSerializer):

    """ Inherit AccountSerializer and define a reverse relation. """

    cards = fields.ModelPermissionsField('tests.CardWithModelPermissionsField')

    class Meta:
        model = Account


class ServiceSerializer(serializers.ModelPermissionsSerializer):

    class Meta:
        model = Service



class CardSerializer(serializers.ModelPermissionsSerializer):

    account = fields.ModelPermissionsField(AccountSerializer)
    service_names = fields.ModelPermissionsField(ServiceSerializer, source='services')

    class Meta:
        model = Card

class CardWithModelPermissionsField(serializers.ModelPermissionsSerializer):

    account = fields.ModelPermissionsField(AccountWithModelPermissionsField)

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
