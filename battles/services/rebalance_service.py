from decimal import Decimal
from battles.services.pyth_service import PythService
from battles.models import Player, Battle

class RebalanceService:
    @staticmethod
    def rebalance_battle(battle: Battle):
        players = battle.participants.select_related('basket').all()

        for player in players:
            total_value = Decimal('0')
            for token in player.basket.tokens:
                price = PythService.get_price_usd(token["symbol"])
                weight = Decimal(token["weight"]) / Decimal('100')
                total_value += price * weight

            player.current_value = float(total_value * 100)
            player.roi = float(((total_value * 100) / 100 - 1) * 100)
            player.save()

        ranked = players.order_by("-roi")
        for rank, player in enumerate(ranked, 1):
            player.rank = rank
            player.save()

        for player in ranked:
            jsparks = Decimal(player.roi) * Decimal('10')
            player.jsparks_earned = min(max(jsparks, 0), Decimal('5000'))
            player.save()

        return battle