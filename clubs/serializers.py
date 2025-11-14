from rest_framework import serializers
from .constant import CLUB_TIERS
from .models import Club
from clubs.services.club_service import create_club


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            "id", "name", "category", "owner", "owner_wallet",
            "nft_id", "tier", "access_type", "privileges", "created_at"
        ]
        read_only_fields = ["owner", "access_type", "privileges", "nft_id", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        # 🪙 Auto-fill tier defaults
        tier = validated_data.get("tier", "COMMON")
        tier_info = CLUB_TIERS.get(tier.upper(), CLUB_TIERS["COMMON"])

        validated_data["access_type"] = tier_info.get("access_type", "Free")
        validated_data["privileges"] = tier_info.get("privileges", "Basic yield farms")
        validated_data["owner_wallet"] = getattr(user, "hedera_account_id", "0.0.0000")

        club = Club.objects.create(owner=user, **validated_data)

        blockchain_result = create_club(
            name=club.name,
            owner=user,
            owner_wallet=club.owner_wallet,
            category=club.category,
            tier=club.tier,
            access_type=club.access_type,
            privileges=club.privileges,
        )

        if blockchain_result.get("status") == "success":
            club.nft_id = blockchain_result["nft_id"]

        club.save()
        return club


class JoinClubSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate(self, attrs):
        club = self.context.get("club")
        user = self.context.get("user")

        if club.members.filter(id=user.id).exists():
            raise serializers.ValidationError("User already joined this club.")
        return attrs


class ClubListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["id", "name", "description", "created_at"]


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "description"]
