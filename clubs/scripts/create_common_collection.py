import os
from hiero_sdk_python import (
    PrivateKey,
    TokenCreateTransaction,
    TokenType,
    Client,
    AccountId
)
from dotenv import load_dotenv

load_dotenv()

client = Client()
operator_id = AccountId.from_string(os.getenv("HEDERA_OPERATOR_ID"))
admin_key = PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))
client.set_operator(operator_id, admin_key)

supply_key = admin_key

tx = (
    TokenCreateTransaction()
    .set_token_name("JBLB Common Club")
    .set_token_symbol("JBLB-C")
    .set_token_type(TokenType.NON_FUNGIBLE_UNIQUE)
    .set_treasury_account_id(operator_id)
    .set_admin_key(admin_key)
    .set_supply_key(supply_key)
    .freeze_with(client)
)

signed_tx = tx.sign(admin_key)
receipt = signed_tx.execute(client)

token_id = receipt.token_id
print("Collection ID:", token_id)