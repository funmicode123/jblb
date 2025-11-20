from battles.models import Basket
from clubs.models import Club
from pythclient.pythclient import PythClient
from pythclient.utils import get_key
import asyncio

class BasketRepository:
    @staticmethod
    def create_basket(data) -> Basket:
        club = Club.objects.get(id=data['club'].id)

        #initial_value = BasketRepository._fetch_oracle_initial_value(data["tokens"])

        basket = Basket.objects.create(
            club=club,
            creator=data["creator"],
            creator_wallet=data["creator_wallet"],
            name=data.get("name"),
            tokens=data.get("tokens", []),
            total_weight=data["total_weight"],
            initial_value=100,
            current_value=100,
            oracle_source="pyth"
        )
        return basket

    @staticmethod
    def _fetch_oracle_initial_value(tokens):
        async def fetch_prices():
            solana_network = "devnet"
            mapping_key = get_key(solana_network, "mapping")
            program_key = get_key(solana_network, "program")

            async with PythClient(
                    first_mapping_account_key=mapping_key,
                    program_key=program_key) as client:
                await client.refresh_all_prices()

                total_value = 0.0
                for token in tokens:
                    symbol = f"{token['symbol'].upper()}/USD"  # e.g., "HBAR/USD"
                    try:
                        products = await client.get_products()
                        product = next((p for p in products if symbol in str(p.attrs)), None)
                        if product:
                            prices = await product.get_prices()
                            price_info = list(prices.values())[0] if prices else None
                            if price_info:
                                price = price_info.aggregate_price.price / (10 ** price_info.aggregate_price.expo)
                                weight = token["weight"] / 100.0
                                total_value += price * weight
                                print(f"✅ Oracle: {symbol} = ${price:.4f} * {weight * 100}%")
                            else:
                                raise ValueError("No price info available")
                        else:
                            print(f"No feed for {symbol} — fallback $1")
                            total_value += 1.0 * (token["weight"] / 100.0)
                    except Exception as e:
                        print(f"Oracle error for {symbol}: {e} — fallback $1")
                        total_value += 1.0 * (token["weight"] / 100.0)

                print(f"Total initial_value from Pyth: ${total_value:.2f}")
                return total_value or 100.0

                # Run async in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_prices())
            finally:
                loop.close()

    @staticmethod
    def get_basket_by_id(basket_id):
        return Basket.objects.filter(id=basket_id).first()

    @staticmethod
    def list_baskets_by_club(club_id):
        return Basket.objects.filter(club_id=club_id).order_by("-created_at")