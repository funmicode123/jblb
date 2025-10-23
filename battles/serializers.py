from rest_framework import serializers
from .models import Basket, Battle, Participant
class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket; fields = '__all__'
class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle; fields = '__all__'
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant; fields = '__all__'
