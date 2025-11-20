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
            "id", "club", "creator", "creator_wallet", "name",
            "tokens", "total_weight", "initial_value", "current_value", "created_at"
        ]
        read_only_fields = [
            "id", "creator", "creator_wallet", "total_weight",
            "initial_value", "current_value", "created_at"
        ]


class CreateBasketSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tokens = serializers.JSONField()

    def validate_tokens(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Tokens must be a non-empty list.")
        total = sum(item.get("weight", 0) for item in value)
        if abs(total - 100) > 0.01:
            raise serializers.ValidationError("Total weight must be exactly 100.")
        return value

    def validate_club_id(self, value):
        if value:
            from clubs.models import Club
            if not Club.objects.filter(id=value).exists():
                raise serializers.ValidationError("Invalid club ID.")
        return value

    def create(self, validated_data):
        # AUTO SET initial_value = 100.0
        # AUTO SET current_value = 100.0
        basket = Basket.objects.create(
            name=validated_data["name"],
            tokens=validated_data["tokens"],
            club_id=validated_data.get("club_id"),
            creator=self.context["request"].user,
            creator_wallet=getattr(self.context["request"].user, "hedera_account_id", None),
            initial_value=100.0,
            current_value=100.0,
            total_weight=100.0,
        )
        return basket


class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle; fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player; fields = '__all__'
