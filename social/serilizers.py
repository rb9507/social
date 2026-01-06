from rest_framework import serializers

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'email']
        model = 'SuperAdmin'

