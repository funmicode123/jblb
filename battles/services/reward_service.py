from decimal import Decimal
from battles.models import Battle, Player
from battles.services.hedera_service import mint_rank_nft

class RewardService:
    @staticmethod
    def distribute_final_rewards(battle: Battle):
        if battle.status != 'finished':
            raise ValueError("Battle must be finished to distribute rewards")

        battle.update_pool()
        player_pool = battle.winner_prize

        players = list(battle.participants.order_by('rank'))
        n = len(players)

        first = player_pool * Decimal('0.40')
        second = player_pool * Decimal('0.25')
        third = player_pool * (Decimal('0.20') if n == 4 else Decimal('0.15'))
        rest_pool = player_pool - first - second - third

        if n >= 1: players[0].usd_reward = first
        if n >= 2: players[1].usd_reward = second
        if n >= 3: players[2].usd_reward = third

        remaining = players[3:] if n > 3 else []
        if remaining:
            total_roi_weight = sum(max(Decimal(p.roi) + 100, Decimal('1')) for p in remaining)
            for p in remaining:
                weight = max(Decimal(p.roi) + 100, Decimal('1'))
                p.usd_reward = rest_pool * (weight / total_roi_weight)

        for player in players:
            player.usd_reward = player.usd_reward.quantize(Decimal('0.01'))
            player.jsparks_earned += player.usd_reward * Decimal('10')
            player.save()

            if player.rank <= 3:
                serial = mint_rank_nft(player.user, battle.title, player.rank)
                player.reward_nft_serial = serial
                player.save()

        print(f"Rewards distributed for battle {battle.title} | Pool: ${player_pool}")