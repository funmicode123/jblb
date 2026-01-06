import requests
import os

from clubs.services.hedera_service import upload_to_ipfs
from ..models import Battle, Player, Basket
from ..validator import validate_player_access
from clubs.models import Club
from blockchain.utils.hedera_utils import verify_nft_access
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from hiero_sdk_python import(
    Client, TokenMintTransaction, PrivateKey, AccountId, TokenId
)
from hiero_sdk_python.transaction.transfer_transaction import TransferTransaction


HEDERA_MIRROR_NODE = "https://mainnet-public.mirrornode.hedera.com/api/v1"

def get_account_balance(account_id):
    url = f"{HEDERA_MIRROR_NODE}/accounts/{account_id}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(f"Failed to fetch balance: {res.text}")


def get_token_info(token_id):
    url = f"{HEDERA_MIRROR_NODE}/tokens/{token_id}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def list_account_tokens(account_id):
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


def mint_rank_nft(user, battle_title: str, rank: int):
    rank_images = {
        1: "ipfs://bafkreifdmjpg2jlkuimlk24vzd5t7zvoxw66jkczvbgquyf2qqcnw3jhv4",
        2: "ipfs://bafkreicqjawx3eigptbrsskerdbmrumse7oiknvysbefl554gwjzccyhze",
        3: "ipfs://bafkreid7q5nblasnwk3dpa52pptjmdpjd7m24qz55d26tpfy7oq2jccslq",
    }

    rank_names = {1: "1st Place Champion", 2: "2nd Place Runner-Up", 3: "3rd Place Legend"}
    colors = {1: "Gold", 2: "Silver", 3: "Bronze"}

    metadata = {
        "name": f"{rank_names[rank]} – {battle_title}",
        "description": f"Top {rank} performer in {battle_title} – Only one minted per battle!",
        "image": rank_images[rank],
        "attributes": [
            {"trait_type": "Rank", "value": rank},
            {"trait_type": "Placement", "value": rank_names[rank]},
            {"trait_type": "Color", "value": colors[rank]},
            {"trait_type": "Battle", "value": battle_title},
            {"trait_type": "Recipient", "value": user.username},
        ]
    }

    cid = upload_to_ipfs(metadata)
    metadata_uri = f"ipfs://{cid}"

    client = Client()
    client.set_operator(
        AccountId.from_string(os.getenv("HEDERA_OPERATOR_ID")),
        PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))
    )

    COLLECTION_ID = TokenId.from_string(os.getenv("JBLB_RANK_NFT_COLLECTION_ID"))
    SUPPLY_KEY = PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))

    mint_tx = (
        TokenMintTransaction()
        .set_token_id(COLLECTION_ID)
        .set_metadata([metadata_uri.encode("utf-8")])
        .freeze_with(client)
        .sign(SUPPLY_KEY)
    )

    receipt = mint_tx.execute(client)
    serial = receipt.serial_numbers[0]

    print(f"Minted Rank #{rank} NFT to {user.username} | Serial: {serial} | CID: {cid}")

    return serial


def transfer_jsparks(user, amount):
    """
    Transfer JSparks tokens to a user's account.
    
    Args:
        user: User object with hedera_account_id
        amount: Amount of JSparks to transfer (as integer, e.g., 10 for 10 JSparks)
    """
    if not user.hedera_account_id:
        raise ValidationError("User does not have a Hedera account ID")
    
    # Get JSparks token ID from environment variables
    jsparks_token_id = os.getenv("JSPARKS_TOKEN_ID")
    if not jsparks_token_id:
        raise ValidationError("JSPARKS_TOKEN_ID not configured in environment variables")
    
    # Get operator credentials
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")
    
    if not operator_id or not operator_key:
        raise ValidationError("Hedera operator credentials not configured")
    
    # Create client
    client = Client()
    client.set_operator(
        AccountId.from_string(operator_id),
        PrivateKey.from_string(operator_key)
    )
    
    # Create transfer transaction
    transfer_tx = (
        TransferTransaction()
        .add_token_transfer(
            TokenId.from_string(jsparks_token_id),
            AccountId.from_string(operator_id),  # Operator sends tokens
            -amount  # Negative amount for sender
        )
        .add_token_transfer(
            TokenId.from_string(jsparks_token_id),
            AccountId.from_string(user.hedera_account_id),  # Recipient receives tokens
            amount  # Positive amount for recipient
        )
    )
    
    # Freeze and sign transaction
    transfer_tx.freeze_with(client)
    
    # Execute transaction
    receipt = transfer_tx.execute(client)
    
    return receipt
