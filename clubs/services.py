from blockchain.services.hedera_service import publish_intent
from clubs.constant import CLUB_TIERS


def create_club(name, owner_wallet, tier="COMMON"):
    """
    Mint a JBLB Club NFT on-chain and register its tier, owner, and privileges.
    """

    if tier not in CLUB_TIERS:
        raise ValueError(f"Invalid club tier. Choose from: {', '.join(CLUB_TIERS.keys())}")

    tier_data = CLUB_TIERS[tier]

    intent = {
        "type": "mint_club_nft",
        "name": name,
        "owner": owner_wallet,
        "tier": tier,
        "access_type": tier_data["access_type"],
        "privileges": tier_data["privileges"]
    }

    return publish_intent(intent)
