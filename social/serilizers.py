from rest_framework import serializers
from social.models import SuperAdmin

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'email', 'password']
        model = SuperAdmin

