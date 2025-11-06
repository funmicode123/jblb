from blockchain.services.hedera_service import validate_nft_ownership
from blockchain.utils.hedera_utils import verify_nft_access
from django.core.exceptions import PermissionDenied


# ✅ 1. Public club — anyone can access
def is_public_club(club):
    return getattr(club, "is_public", False)


    # ✅ 2. Check if player is already in the club’s player list
def is_member(wallet_address, club):
    return club.players.filter(user__wallet=wallet_address).exists()

def _validate_nft_ownership(player, nft_id):
    from blockchain.services.hedera_service import validate_nft_ownership
    return validate_nft_ownership(player.wallet_address, player.nft_token_id, nft_id)


def _verify_nft_access(wallet_address, club):
    from blockchain.utils.hedera_utils import verify_nft_access
    return verify_nft_access(wallet_address, club.nft_collection_id)


def validate_player_access(player, club):
    """
    Returns True → access granted
    Raises ValueError / PermissionError → blocked
    """
    # 1. Grab wallet (your mock has both names)
    wallet_address = player.wallet_address or getattr(player, "wallet", None)
    if not wallet_address:
        raise ValueError("Player wallet address is missing.")

    # 2. Public club OR already a member
    if club.access_type == "public":
        return True
    if club.players.filter(wallet=wallet_address).exists():
        return True

    # 3. NFT required
    nft_token_id = getattr(player, "nft_token_id", None)
    if not nft_token_id:
        raise ValueError("Player does not have an access NFT.")

    # 4. On-chain ownership
    if not _validate_nft_ownership(player, club.nft_collection_id):
        raise PermissionError("NFT ownership validation failed.")

    # 5. Optional club-specific NFT match
    required = getattr(club, "required_nft", None)
    if required and nft_token_id != required:
        raise PermissionError("NFT does not match club access requirement.")

    # 6. Final mirror-node check
    if not _verify_nft_access(wallet_address, club):
        raise PermissionError("Wallet address does not have valid NFT access.")

    return True
