from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SuperAdmin

class AdminSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        super_admin = SuperAdmin.objects.create(
            user=user,
            name=validated_data['name']
        )

        return super_admin
