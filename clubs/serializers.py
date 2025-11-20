from rest_framework import serializers
from .constant import CLUB_TIERS
from .models import Club
from clubs.services.club_service import create_club


class ClubSerializer(serializers.ModelSerializer):
    nft_metadata_url = serializers.SerializerMethodField()
    class Meta:
        model = Club
        fields = [
            "id", "name", "description", "category",  "tier", "owner_wallet",
            "nft_id", "nft_serial", "metadata_cid", "nft_metadata_url",
            "access_type", "privileges", "created_at"
        ]
        read_only_fields = ["owner_wallet", "nft_id", "nft_serial",
                            "metadata_cid", "created_at"]

    def get_nft_metadata_url(self, obj):
        if obj.metadata_cid and not obj.metadata_cid.startswith("premint"):
            return f"https://gateway.pinata.cloud/ipfs/{obj.metadata_cid}"
        return None

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        tier = validated_data.get("tier", "COMMON").upper()
        tier_info = CLUB_TIERS.get(tier, CLUB_TIERS["COMMON"])

        validated_data.update({
            "access_type": tier_info["access_type"],
            "privileges": tier_info["privileges"],
            "owner_wallet": getattr(user, "hedera_account_id", "0.0.0000")
        })

        club = create_club(
            name=validated_data["name"],
            owner=user,
            owner_wallet=validated_data["owner_wallet"],
            category=validated_data.get("category", "COMMON"),
            tier=tier,
            description=validated_data.get("description")
        )
        return club

    @staticmethod
    def get_nft_metadata_url(obj):
        if obj.metadata_cid and not obj.metadata_cid.startswith("premint"):
            return f"https://gateway.pinata.cloud/ipfs/{obj.metadata_cid}"
        return None

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
