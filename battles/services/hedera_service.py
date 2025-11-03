import requests
import os

from ..models import Battle, Player, Basket
from ..validator import validate_player_access
from clubs.models import Club
from blockchain.utils.hedera_utils import verify_nft_access  # example helper
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

HEDERA_MIRROR_NODE = "https://mainnet-public.mirrornode.hedera.com/api/v1"  # or testnet

def get_account_balance(account_id):
    """Fetch account balance from Hedera mirror node."""
    url = f"{HEDERA_MIRROR_NODE}/accounts/{account_id}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(f"Failed to fetch balance: {res.text}")

def get_token_info(token_id):
    """Fetch token (or NFT) details from Hedera."""
    url = f"{HEDERA_MIRROR_NODE}/tokens/{token_id}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def list_account_tokens(account_id):
    """List all tokens (fungible or NFT) linked to an account."""
    url = f"{HEDERA_MIRROR_NODE}/accounts/{account_id}/tokens"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def join_battle(battle_id, data):
    battle = get_object_or_404(Battle, id=battle_id)
    user_wallet = data.get('user_wallet')
    club_id = data.get('club_id')
    basket_id = data.get('basket_id')

    if not user_wallet:
        raise ValidationError("User wallet address is required.")

    basket = Basket.objects.filter(id=basket_id).first() if basket_id else None

    club = get_object_or_404(Club, id=club_id)
    if not validate_player_access(user_wallet, club):
        raise ValidationError("Access denied: You are not a verified NFT holder for this club.")

    if Player.objects.filter(active_battle=battle, user__wallet=user_wallet).exists():
        raise ValidationError("You have already joined this battle.")

    nft_valid = verify_nft_access(user_wallet, club)
    if not nft_valid:
        raise ValidationError("NFT validation failed — club membership token not found.")

    player = Player.objects.create(
        user_wallet=user_wallet,
        club=club,
        active_battle=battle,
        basket=basket,
    )

    if battle.participants.count() >= battle.velocity:
        battle.status = "active"
        battle.start_time = datetime.utcnow()
        battle.end_time = battle.start_time + timedelta(seconds=battle.duration_seconds)
        battle.save()

    return player