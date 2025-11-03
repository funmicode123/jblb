import os, requests

from hiero_sdk_python import (
    Client, AccountId, PrivateKey, TokenId, TokenNftInfoQuery
)
from django.conf import settings

HEDERA_API_URL = "https://testnet.mirrornode.hedera.com/api/v1"

def get_hedera_client():
    network = os.getenv("HEDERA_NETWORK", "testnet")
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")

    if not operator_id or not operator_key:
        raise ValueError("Missing HEDERA_OPERATOR_ID or HEDERA_OPERATOR_KEY in environment.")

    client = Client() if network == "testnet" else network == "mainnet"
    client.set_operator(AccountId.from_string(operator_id), PrivateKey.from_string(operator_key))
    return client


def verify_nft_access(wallet_address: str, club) -> bool:
    """
    Check if a user's Hedera wallet owns at least one NFT from the club's token.
    Returns True if access is valid, False otherwise.
    """
    try:
        token_id = club.nft_id  # e.g., "0.0.123456"
        # Query the Mirror Node for NFTs owned by the wallet
        url = f"{HEDERA_API_URL}/accounts/{wallet_address}/nfts?limit=100"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        nfts = data.get("nfts", [])

        # Check if any NFT matches the club's token_id
        has_nft = any(nft.get("token_id") == token_id for nft in nfts)

        if has_nft:
            print(f"✅ Access granted: Wallet {wallet_address} holds at least one NFT for club {club.name}")
            return True
        else:
            print(f"Access denied: Wallet {wallet_address} holds 0 NFTs for club {club.name}")
            return False

    except Exception as e:
        print(f"⚠️ Error verifying NFT access for wallet {wallet_address}: {e}")
        return False
