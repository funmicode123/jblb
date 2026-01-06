from json import load
import os
from dotenv import load_dotenv
from hiero_sdk_python import (
    Client, TokenCreateTransaction, PrivateKey, 
    AccountId, TokenType, SupplyType
)

load_dotenv()

operator_id=AccountId.from_string(os.getenv("HEDERA_OPERATOR_ID"))
operator_key=PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))

client = Client()
client.set_operator(
    operator_id, operator_key
)

token_tx = (
    TokenCreateTransaction()
    .set_token_name("JSparks")
    .set_token_symbol("JSPK")
    .set_decimals(4)  
    .set_initial_supply(100_000)  
    .set_token_type(TokenType.FUNGIBLE_COMMON)
    .set_supply_type(SupplyType.FINITE)
    .set_max_supply(100_000)
    .set_treasury_account_id(operator_id)
    .freeze_with(client)
)

receipt = token_tx.execute(client)
token_id = receipt.token_id
print(f"Created token with ID: {token_id}")