from rest_framework import serializers
from apps.core.models import User, Role
import random

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'name', 'password', 'is_active', 'is_blocked', 'is_deleted']

    def create(self, validated_data):
        password = validated_data.pop('password')

        if not password:
            raise serializers.ValidationError({'password': 'Password is required'})

        name = validated_data['name']
        username = name.replace(" ", "_").lower()

        original_username = username
        while User.objects.filter(username=username).exists():
            suffix = str(random.randint(1000, 9999))
            username = f"{original_username}_{suffix}"

        role_name = validated_data.pop('role', None)

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=password,
            is_active=False,
            is_blocked=False,
            name=name,
        )

        if role_name:
            try:
                role = Role.objects.get(name=role_name)
                user.role = role
                user.save()
            except Role.DoesNotExist:
                pass

        return user
def delete(self, instance):
    instance.is_active = False
    instance.save()
    return instance

def update(self, instance, validated_data):
    instance.email = validated_data.get('email', instance.email)
    instance.name = validated_data.get('name', instance.name)

    if 'is_active' in validated_data:
        instance.is_active = validated_data['is_active']

    if 'is_blocked' in validated_data:
        instance.is_blocked = validated_data['is_blocked']

    if 'role' in validated_data:
        try:
            role_obj = Role.objects.get(name=validated_data['role'])
            instance.role = role_obj
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role": "Role not found"})

    instance.save()
    return instance