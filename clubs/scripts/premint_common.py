import os
from hiero_sdk_python import Client, TokenMintTransaction, AccountId, PrivateKey, TokenId
import requests
from dotenv import load_dotenv

from clubs.models import CommonNFT

load_dotenv()

client = Client()
account_id= AccountId.from_string(os.getenv("HEDERA_OPERATOR_ID"))
private_key= PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))
client.set_operator(account_id, private_key)


COLLECTION_ID = os.getenv("JBLB_COMMON_COLLECTION_ID")

SUPPLY_KEY = private_key

COLLECTION_ID_STR = os.getenv("JBLB_COMMON_COLLECTION_ID")

PINATA_JWT = os.getenv("PINATA_JWT")

def upload_to_ipfs(metadata: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {"Authorization": f"Bearer {PINATA_JWT}"}
    response = requests.post(url, json=metadata, headers=headers)
    response.raise_for_status()
    return response.json()["IpfsHash"]

metadatas = []
for i in range(1, 11):
    meta = {
        "name": f"JBLB Test Club #{i}",
        "description": "Free NFT for first 10 test users",
        "image": "ipfs://Qmbafybeibm2rqih3rx733uepcgx6tmjzr4grnxnowitoykcxjpnqd5pwpkm4/Sample.png",
        "attributes": [{"trait_type": "Tier", "value": "COMMON"}]
    }
    cid = upload_to_ipfs(meta)
    uri = f"ipfs://{cid}"
    metadatas.append(f"ipfs://{cid}".encode())
    print(f" #{i} → {uri}")

COLLECTION_ID = TokenId.from_string(COLLECTION_ID_STR)
mint_tx = (
    TokenMintTransaction()
    .set_token_id(COLLECTION_ID)
    .set_metadata(metadatas)
    .freeze_with(client)
    .sign(SUPPLY_KEY)
)

receipt = mint_tx.execute(client)
serials = receipt.serial_numbers

for serial in serials:
    CommonNFT.objects.get_or_create(serial=serial)

print("Minted 10 NFTs!")
print("Serials:", serials)
print("Collection:", COLLECTION_ID)