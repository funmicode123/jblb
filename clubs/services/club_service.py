from blockchain.services.hedera_service import publish_intent, validate_token_balance
from clubs.models import Club
import os

JBLB_TOKEN_ID = os.getenv("JBLB_TOKEN_ID", "0.0.999999")
MIN_JBLB_BALANCE = int(os.getenv("JBLB_MIN_BALANCE", 10))

def create_club(name, user, description, owner, owner_wallet, category="common", tier="COMMON", access_type="Free", privileges=""):
    """
    Creates a Club record in Django + publishes a blockchain mint intent.
    Requires the user to hold a minimum amount of JBLB tokens.
    """

    club = Club.objects.create(
        owner=user,
        name=name,
        description=description
    )

    # 🔐 Step 1: Validate token ownership (must hold >= 10 JBLB tokens)
    has_tokens = validate_token_balance(owner_wallet, JBLB_TOKEN_ID, min_balance=10)
    if not has_tokens:
        return {
            "status": "failed",
            "message": f"Insufficient JBLB balance. You must hold at least 10 $JBLB tokens to create a club."
        }

    # 🧩 Step 2: Construct blockchain mint intent
    intent = {
        "type": "mint_club_nft",
        "name": name,
        "owner_wallet": owner_wallet,
        "tier": tier,
        "category": category,
    }

    # 🪙 Step 3: Publish to blockchain or mock network
    result = publish_intent(intent)

    # 🧱 Step 4: Save club in Django DB
    club = Club.objects.create(
        name=name,
        owner=owner,
        category=category,
        owner_wallet=owner_wallet,
        tier=tier,
        access_type=access_type,
        privileges=privileges,
        nft_id=result.get("nft_id"),
    )

    return {
        "status": "created",
        "club": {
            "id": str(club.id),
            "name": club.name,
            "owner_wallet": club.owner_wallet,
            "nft_id": club.nft_id,
            "tx_hash": result.get("tx_hash"),
        },
    }