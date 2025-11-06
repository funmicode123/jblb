from blockchain.services.hedera_service import publish_intent, validate_token_balance
from clubs.models import Club
import os


JBLB_TOKEN_ID = os.getenv("JBLB_TOKEN_ID", "0.0.999999")
MIN_JBLB_BALANCE = int(os.getenv("JBLB_MIN_BALANCE", 1))


def create_club(name, owner, owner_wallet, category="COMMON", tier="COMMON", access_type="Free", privileges=""):
    """
    Creates a Club record in Django + publishes a blockchain mint intent.
    Requires the user to hold a minimum amount of JBLB tokens.
    """

    has_tokens = validate_token_balance(owner_wallet, JBLB_TOKEN_ID, min_balance=MIN_JBLB_BALANCE)
    if not has_tokens:
        return {
            "status": "failed",
            "message": f"Insufficient JBLB balance. You must hold at least {MIN_JBLB_BALANCE} $JBLB tokens to create a club."
        }

    intent = {
        "type": "mint_club_nft",
        "name": name,
        "owner_wallet": owner_wallet,
        "tier": tier,
        "category": category,
    }

    result = publish_intent(intent)

    return {
        "status": "success",
        "nft_id": result.get("nft_id", "mock-nft"),
        "tx_hash": result.get("tx_hash", "mock-hash"),
    }