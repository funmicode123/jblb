from rest_framework import serializers
from users.models import User
from .models import Basket, Battle, Player
from users.models import decrypt_value

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

    def get_wallet(self, obj):
        if obj.hedera_account_id:
            try:
                return decrypt_value(obj.hedera_account_id)
            except:
                return obj.hedera_account_id
        return None

class BasketSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(read_only=True)

    class Meta:
        model = Basket
        fields = [
            "id",
            "club",
            "creator",
            "creator_wallet",
            "name",
            "tokens",
            "total_weight",
            "created_at",
        ]
        read_only_fields = ["id", "creator", "creator_wallet", "total_weight", "created_at"]


class CreateBasketSerializer(serializers.Serializer):
    # club_id = serializers.UUIDField()
    # creator_wallet = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=100)
    tokens = serializers.JSONField()
    initial_value = serializers.FloatField(default=5)

    def validate_club_id(self, value):
        from clubs.models import Club
        if not Club.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid club ID.")
        return value


class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle; fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player; fields = '__all__'
