# clubs/serializers.py
from rest_framework import serializers
from .models import Club
from blockchain.services.hedera_service import create_fungible_token

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["id", "name", "category", "owner", "hedera_tx_id", "nft_id", "minted_at"]
        read_only_fields = ["hedera_tx_id", "nft_id", "minted_at"]

    def create(self, validated_data):
        club = Club.objects.create(**validated_data)

        # 🔗 Call Hedera blockchain service
        blockchain_result = create_club(
            name=club.name,
            owner_wallet=str(club.owner.wallet_address if hasattr(club.owner, "wallet_address") else "0.0.0000"),
            category=club.category
        )

        # Update club with blockchain data
        club.hedera_tx_id = blockchain_result.get("intent", {}).get("tx_id", "mock-tx")
        club.nft_id = blockchain_result.get("intent", {}).get("nft_id", "mock-nft")
        club.save()

        return club

