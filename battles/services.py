from .models import Battle, Participant, Basket
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
def join_battle(battle_id, data):
    battle = get_object_or_404(Battle, id=battle_id)
    user_wallet = data.get('user_wallet')
    basket_id = data.get('basket_id')
    basket = None
    if basket_id:
        basket = Basket.objects.filter(id=basket_id).first()
    p = Participant.objects.create(battle=battle, user_wallet=user_wallet, basket=basket)
    if battle.participants.count() >= battle.velocity:
        battle.status = 'active'
        battle.start_time = datetime.utcnow()
        battle.end_time = datetime.utcnow() + timedelta(seconds=battle.duration_seconds)
        battle.save()
    return p
