from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import Departments, Position, AccessUrl

User = get_user_model()


class AccessUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessUrl
        fields = '__all__'


class UserSerializer(UserCreateSerializer):
    access_url = AccessUrlSerializer(many=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'slug', 'first_name', 'last_name', 'is_active', 'is_online', 'is_staff',
                  'is_superuser', 'get_full_name', 'access_url']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class HelperSerializer(serializers.ModelSerializer):
    salary = serializers.CharField(source='position.salary', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'get_full_name', 'get_signature_url', 'first_name', 'last_name', 'salary',)


class DepartmentWithChildrenSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Departments
        fields = '__all__'

    def get_children(self, obj):
        return obj.get_staff()
