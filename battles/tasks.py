from celery import shared_task
from battles.models import Battle
from battles.services.rebalance_service import RebalanceService

@shared_task
def pyth_rebalance_all():
    active = Battle.objects.filter(status='active')
    for battle in active:
        try:
            RebalanceService.rebalance_battle(battle)
        except Exception as e:
            print(f"Rebalance failed for {battle.id}: {e}")