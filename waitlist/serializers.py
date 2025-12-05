from rest_framework import serializers
from .models import Waitlist

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = ['custom_id', 'username', 'email', 'is_verified', 'created_at']
        read_only_fields = ['custom_id', 'is_verified', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }