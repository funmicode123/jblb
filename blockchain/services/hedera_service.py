import os, json, datetime, requests
from hiero_sdk_python import PrivateKey, TopicCreateTransaction, TopicMessageSubmitTransaction, CryptoGetAccountBalanceQuery, Hbar
#from anoma_sdk import WallectClient
from blockchain.utils.hedera_utils import get_hedera_client, verify_nft_access
from users.services.hedera_service import client


HEDERA_OPERATOR_ID = os.getenv('HEDERA_OPERATOR_ID')
HEDERA_OPERATOR_KEY = os.getenv('HEDERA_OPERATOR_KEY')
# NETWORK = os.getenv("HEDERA_NETWORK", "testnet")
#
# client = Client() if NETWORK == "testnet" else NETWORK == "mainnet"
# client.set_operator(AccountId.from_string(HEDERA_OPERATOR_ID), PrivateKey.from_string(HEDERA_OPERATOR_KEY))
#
MIRROR_NODE = "https://testnet.mirrornode.hedera.com/api/v1"

def publish_intent(intent, topic_id=None):
    """
    Publishes an intent (e.g. club mint request) to Hedera Consensus Service (HCS).
    If no topic exists, creates a temporary one first.
    """
    try:
        # Step 1: Ensure client and operator
        if not client:
            raise Exception("Hedera client not initialized")

        operator_key_str = os.getenv("HEDERA_OPERATOR_KEY")
        operator_key = PrivateKey.from_string(operator_key_str)

        # Step 2: Create topic if not provided
        if not topic_id:
            topic_tx = TopicCreateTransaction().execute(client)
            topic_receipt = topic_tx.get_receipt(client)
            topic_id = str(topic_receipt.topic_id)
            print(f"✅ Created new topic: {topic_id}")

        # Step 3: Prepare the message
        message_str = json.dumps(intent)

        # Step 4: Submit transaction
        submit_tx = (
            TopicMessageSubmitTransaction()
            .set_topic_id(topic_id)
            .set_message(message_str)
            .freeze_with(client)
            .sign(operator_key)
        )

        submit_response = submit_tx.execute(client)
        receipt = submit_response.get_receipt(client)

        return {
            "status": "success",
            "topic_id": topic_id,
            "consensus_timestamp": str(receipt.consensus_timestamp),
            "intent": intent
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# def create_user_account(initial_hbar=5):
#     """
#     Create a new testnet account with initial HBAR balance.
#     Returns {account_id, private_key, public_key}.
#     """
#     new_key = PrivateKey.generate()
#     tx_response = (
#         AccountCreateTransaction()
#         .set_key(new_key.get_public_key())
#         .set_initial_balance(Hbar(initial_hbar))
#         .execute(client)
#     )
#     receipt = tx_response.get_receipt(client)
#     account_id = str(receipt.account_id)
#     return {
#         "account_id": account_id,
#         "private_key": new_key.to_string(),
#         "public_key": new_key.get_public_key().to_string_raw(),
#     }
#
#
# # -------------------------
# # 2. Fetch token + HBAR balance
# # -------------------------

def get_account_balance(account_id):
    try:
        balance = CryptoGetAccountBalanceQuery().set_account_id(account_id).execute(client)
        url = f"{MIRROR_NODE}/accounts/{account_id}/tokens"
        response = requests.get(url)
        tokens = response.json().get("tokens", [])
        return {
            "hbar": float(balance.hbars.to(Hbar.Unit.Hbar)),
            "tokens": {str(k): int(v) for k, v in balance.token.values.items()},
        }
    except Exception as e:
        return {"error": str(e)}


# -------------------------
# 3. Validate NFT club access
# -------------------------
def validate_nft_ownership(account_id, nft_id):
    """
    nft_id format: <token_id>/<serial_number>
    Example: 0.0.123456/1
    """
    url = f"{MIRROR_NODE}/accounts/{account_id}/nfts"
    response = requests.get(url)
    if response.status_code != 200:
        return False

    nfts = response.json().get("nfts", [])
    for nft in nfts:
        if nft.get("token_id") == nft_id.split("/")[0]:
            return True
    return False


# -------------------------
# 4. Validate fungible token ownership (e.g. $JBLB)
# -------------------------
def validate_token_balance(account_id, token_id, min_balance=1):
    """
    Verify if account owns enough of a given token (like JBLB).
    """
    url = f"{MIRROR_NODE}/accounts/{account_id}/tokens"
    response = requests.get(url)
    if response.status_code != 200:
        return False

    tokens = response.json().get("tokens", [])
    for token in tokens:
        if token.get("token_id") == token_id and int(token.get("balance", 0)) >= min_balance:
            return True
    return False

def publish_to_hcs(topic_id, message):
    return {'topic_id': topic_id or 'mock-topic', 'message': message, 'published_at': datetime.datetime.utcnow().isoformat()}
def create_fungible_token(name='JBLB Test', symbol='JBLB', initial_supply=1000000):
    return {'token_id': '0.0.' + str(abs(hash(name)) % 1000000), 'name': name, 'symbol': symbol, 'supply': initial_supply}

