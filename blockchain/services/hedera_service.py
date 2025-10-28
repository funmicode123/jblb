import os, datetime, requests
from hedera import TokenId, AccountId, Client, TokenInfoQuery
from anoma_sdk import WallectClient

HEDERA_OPERATOR_ID = os.getenv('HEDERA_OPERATOR_ID')
HEDERA_OPERATOR_KEY = os.getenv('HEDERA_OPERATOR_KEY')
def publish_to_hcs(topic_id, message):
    return {'topic_id': topic_id or 'mock-topic', 'message': message, 'published_at': datetime.datetime.utcnow().isoformat()}
def create_fungible_token(name='JBLB Test', symbol='JBLB', initial_supply=1000000):
    return {'token_id': '0.0.' + str(abs(hash(name)) % 1000000), 'name': name, 'symbol': symbol, 'supply': initial_supply}

def create_hedera_account():
    """
    Create a Hedera testnet account using the Operator Key and Mirror Node.
    """
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")
    operator_id = os.getenv("HEDERA_OPERATOR_ID")

    # This requires an integration layer like Hashio or Hedera JSON RPC relay.
    payload = {
        "transaction": {
            "operator": operator_id,
            "key": operator_key,
        }
    }

    response = requests.post(f"{HEDERA_API_URL}/accounts", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Hedera account creation failed: {response.text}")

def verify_nft_ownership(player):
    if player.chain == "hedera":
        client = Client.for_testnet()
        # Connect with credentials (should be from .env)
        client.setOperator(AccountId.fromString("0.0.xxxx"), "hedera_private_key_here")

        token_id = TokenId.fromString(player.nft_token_id)
        info = TokenInfoQuery(token_id).execute(client)

        # Example: check if wallet_address holds this token
        return player.wallet_address in [assoc.accountId.toString() for assoc in info.accounts]

    elif player.chain == "anoma":
        wallet = WalletClient(network="testnet")
        tokens = wallet.get_tokens(player.wallet_address)
        return player.nft_token_id in [t.id for t in tokens]

    return False