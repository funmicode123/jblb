import requests
from hiero_sdk_python import (
    Client,
    PrivateKey,
    AccountCreateTransaction,
    Hbar, AccountId, TransactionReceipt
)
import os
from hiero_sdk_python.utils.crypto_utils import keccak256


HEDERA_MIRROR_NODE = "https://testnet.mirrornode.hedera.com/api/v1"
HEDERA_OPERATOR_ID = os.getenv("HEDERA_OPERATOR_ID") # Your testnet ID
HEDERA_OPERATOR_KEY = os.getenv("HEDERA_OPERATOR_KEY")  # Your testnet private key

if not HEDERA_OPERATOR_ID or not HEDERA_OPERATOR_KEY:
    raise EnvironmentError("Missing HEDERA_OPERATOR_ID or HEDERA_OPERATOR_KEY in environment variables")

client = Client()
client.set_operator(AccountId.from_string(HEDERA_OPERATOR_ID), PrivateKey.from_string(HEDERA_OPERATOR_KEY))


def create_hedera_account():
    """Create a new Hedera account with a new key pair
    Returns Hedera account details and EVM-compatible address.
    """
    # Generate a new private/public key pair
    new_private_key = PrivateKey.generate_ecdsa()
    new_public_key = new_private_key.public_key()

    tx_response = (
        AccountCreateTransaction()
        .set_key(new_public_key)
        .set_initial_balance(Hbar(10))

    )

    receipt = tx_response.execute(client)
    new_account_id = receipt.account_id

    evm_address = keccak256(new_public_key.to_bytes_ecdsa(compressed=False)[1:])[-20:].hex()

    return {
        "hedera_account_id": str(new_account_id),
        "hedera_public_key": str(new_public_key),
        "hedera_private_key": str(new_private_key),
        "evm_address": f"0x{evm_address}",
    }


def validate_token(token_id: str):
    """
    Validate whether a token exists on the Hedera testnet.
    Returns the token info if found, otherwise None.
    """
    url = f"{HEDERA_MIRROR_NODE}/tokens/{token_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error validating token: {e}")
        return None


def validate_nft(token_id: str, serial_number: str):
    """
    Validate NFT existence by token ID and serial number.
    Returns NFT details if exists, otherwise None.
    """
    url = f"{HEDERA_MIRROR_NODE}/tokens/{token_id}/nfts/{serial_number}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error validating NFT: {e}")
        return None
