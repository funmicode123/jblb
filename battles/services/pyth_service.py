from decimal import Decimal
from pythclient.pythclient import PythClient
from pythclient.utils import get_key
import asyncio

class PythService:
    _client = None
    _loop = None

    HBAR_PRICE_ID = "0x3728e591097635310e6341af53db8b7ee42da9b3a8d918f9463ce9cca886dfbd"

    @classmethod
    def _get_loop(cls):
        if cls._loop is None or cls._loop.is_closed():
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)
        return cls._loop

    @classmethod
    def get_client(cls):
        if cls._client is None:
            loop = cls._get_loop()
            mapping_key = get_key("testnet", type="mapping")
            program_key = get_key("testnet", type="program")
            cls._client = PythClient(first_mapping_account_key=mapping_key, program_key=program_key)
            loop.run_until_complete(cls._client.refresh_all_prices())
        return cls._client

    @classmethod
    def get_hbar_price_usd(cls) -> Decimal:
        try:
            client = cls.get_client()
            loop = cls._get_loop()

            async def fetch():
                price_feed = await client.get_price_feed(cls.HBAR_PRICE_ID)
                if not price_feed:
                    return None
                price = Decimal(price_feed.price)
                expo = price_feed.expo
                return price / Decimal(10) ** expo

            result = loop.run_until_complete(fetch())
            return result.quantize(Decimal('0.00000001')) if result else Decimal('0.05')

        except Exception as e:
            print(f"Pyth HBAR error: {e} → fallback $0.05")
            return Decimal('0.05')