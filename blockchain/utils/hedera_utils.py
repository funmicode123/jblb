import os

from hedera_sdk_python import (
    Client, AccountId, PrivateKey, TokenId, TokenNftInfoQuery, AccountBalanceQuery
)
from django.conf import settings

HEDERA_API_URL = "https://testnet.mirrornode.hedera.com/api/v1"
def get_hedera_client():
    """
    Initialize Hedera testnet client using operator credentials.
    """
    operator_id = AccountId.fromString(settings.HEDERA_OPERATOR_ID)
    operator_key = PrivateKey.fromString(settings.HEDERA_OPERATOR_KEY)
    client = Client.for_testnet()
    client.setOperator(operator_id, operator_key)
    return client


def verify_nft_access(wallet_address: str, club) -> bool:
    """
    Check if a user's Hedera wallet owns at least one NFT from the club's token.
    Returns True if access is valid, False otherwise.
    """
    try:
        client = get_hedera_client()
        token_id = TokenId.fromString(club.nft_id)

        # Query account balance for given wallet
        balance = AccountBalanceQuery().setAccountId(wallet_address).execute(client)

        # Check if the wallet has the club's NFT token
        token_balance = balance.token.get(token_id, None)

        if token_balance and token_balance > 0:
            print(f"✅ Access granted: Wallet {wallet_address} holds {token_balance} NFTs for club {club.name}")
            return True
        else:
            print(f"Access denied: Wallet {wallet_address} holds 0 NFTs for club {club.name}")
            return False

    except Exception as e:
        print(f"⚠️ Error verifying NFT access for wallet {wallet_address}: {e}")
        return False
