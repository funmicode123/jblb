from rest_framework import serializers
from .models import Waitlist

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = ['username', 'email']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }