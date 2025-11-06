from rest_framework import serializers
from .models import Basket, Battle, Player


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket; fields = '__all__'


class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle; fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player; fields = '__all__'
