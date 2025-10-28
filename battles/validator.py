from .blockchain.hedera_service import verify_nft_ownership


def validate_player_access(player, club):
    if club.is_public:
        return True

    if not player.nft_token_id:
        raise ValueError("Player does not have an access NFT.")

    if not verify_nft_ownership(player):
        raise PermissionError("NFT verification failed.")

    if club.required_nft and player.nft_token_id != club.required_nft:
        raise PermissionError("NFT does not match club requirement.")

    return True
