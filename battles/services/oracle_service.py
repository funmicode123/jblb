import requests

ORACLE_URL = "https://hermes.pyth.network/api/latest_price_feeds?ids[]=HBAR/USD"

def get_hbar_price():
    try:
        resp = requests.get(ORACLE_URL, timeout=5)
        data = resp.json()
        price = float(data[0]["price"]["price"]) / 1e8
        return round(price, 4)
    except:
        return 0.12