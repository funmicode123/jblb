import os
import requests
from hiero_sdk_python import Client, TokenMintTransaction, AccountId, PrivateKey, TokenId
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.set_operator(
            AccountId.from_string(os.getenv("HEDERA_OPERATOR_ID")),
            PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))
)

SUPPLY_KEY = PrivateKey.from_string(
    os.getenv("HEDERA_SUPPLY_KEY", os.getenv("HEDERA_OPERATOR_KEY"))
)

def upload_to_ipfs(metadata: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {"Authorization": f"Bearer {os.getenv('PINATA_JWT')}"}
    resp = requests.post(url, json=metadata, headers=headers)
    resp.raise_for_status()
    return resp.json()["IpfsHash"]


def mint_and_assign_common_nft(club) -> dict:
    collection_id_str = os.getenv("JBLB_COMMON_COLLECTION_ID")
    if not collection_id_str:
        raise ValueError("JBLB_COMMON_COLLECTION_ID not set")

    collection_id = TokenId.from_string(collection_id_str)

    metadata = {
        "name": f"{club.name} - Common Club",
        "description": "Free JBLB Common Club Membership",
        "image": "ipfs://Qmbafybeibm2rqih3rx733uepcgx6tmjzr4grnxnowitoykcxjpnqd5pwpkm4/Sample.png",
        "attributes": [{"trait_type": "Tier", "value": "COMMON"}]
    }
    cid = upload_to_ipfs(metadata)

    mint_tx = (
        TokenMintTransaction()
        .set_token_id(collection_id)
        .set_metadata([f"ipfs://{cid}".encode()])
        .freeze_with(client)
        .sign(SUPPLY_KEY)
    )

    receipt = mint_tx.execute(client)
    serial = receipt.serial_numbers[0]

    return {
        "nft_id": str(collection_id),
        "nft_serial": serial,
        "metadata_cid": cid,
        "metadata_url": f"https://gateway.pinata.cloud/ipfs/{cid}"
    }

#You'll need the supply key that was set when creating the token to sign the mint transaction. Without it, the transaction will fail.