
from django.contrib.auth.models import User
from rest_framework_fine_permissions import serializers
from rest_framework import serializers as drf_serializers

class UserSerializer(serializers.ModelPermissionsSerializer):
    
    is_authenticated = drf_serializers.ModelField('is_authenticated')

    class Meta:
        depth = 1
        model = User

class TestNormalSerializer(drf_serializers.ModelSerializer):
    pass
