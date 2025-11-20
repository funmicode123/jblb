from rest_framework.exceptions import ValidationError
from rest_framework import serializers


def is_public_club(club):
    return getattr(club, "is_public", False)

def is_member(wallet_address, club):
    return club.players.filter(user__wallet=wallet_address).exists()

def _validate_nft_ownership(player, nft_id):
    from blockchain.services.hedera_service import validate_nft_ownership
    return validate_nft_ownership(player.wallet_address, player.nft_token_id, nft_id)

def _verify_nft_access(wallet_address, club):
    from blockchain.utils.hedera_utils import verify_nft_access
    return verify_nft_access(wallet_address, club.nft_collection_id)

def validate_basket_data(data):
    if "club" not in data or not data["club"]:
        raise ValidationError({"club": "Club ID is required."})
    if "creator_wallet" not in data or not data["creator_wallet"]:
        raise ValidationError({"creator_wallet": "Creator wallet address is required."})
    if "config" not in data or not isinstance(data["config"], dict):
        raise ValidationError({"config": "Config must be a valid JSON object."})
    if "initial_value" in data and data["initial_value"] < 5:
        raise ValidationError({"initial_value": "Initial value must be greater than five."})
    return data

def validate_player_access(player, club):
    wallet_address = player.wallet_address or getattr(player, "wallet", None)
    if not wallet_address:
        raise ValueError("Player wallet address is missing.")

    if club.access_type == "public":
        return True
    if club.players.filter(wallet=wallet_address).exists():
        return True

    nft_token_id = getattr(player, "nft_token_id", None)
    if not nft_token_id:
        raise ValueError("Player does not have an access NFT.")

    if not _validate_nft_ownership(player, club.nft_collection_id):
        raise PermissionError("NFT ownership validation failed.")

    required = getattr(club, "required_nft", None)
    if required and nft_token_id != required:
        raise PermissionError("NFT does not match club access requirement.")

    if not _verify_nft_access(wallet_address, club):
        raise PermissionError("Wallet address does not have valid NFT access.")

    return True

def validate_tokens( tokens):
    if not isinstance(tokens, list) or len(tokens) == 0:
        raise serializers.ValidationError("Tokens must be a non-empty list.")

    for token in tokens:
        if "weight" not in token or "symbol" not in token:
            raise ValidationError("Each token must include 'symbol' and 'weight'.")

    total_weight = 0
    for token in tokens:
        if "symbol" not in token or "weight" not in token:
            raise serializers.ValidationError("Each token must include 'symbol' and 'weight'.")
        if token["weight"] <= 0:
            raise serializers.ValidationError("Token weights must be positive numbers.")
        total_weight += token["weight"]

    if total_weight != 100:
        raise serializers.ValidationError("Total token weight must equal 100%.")

    return tokens