from django.urls import path
from .views import CreateBasketView, CreateBattleView, JoinBattleView


urlpatterns = [
    path('baskets/create/', CreateBasketView.as_view(), name='create-basket'),
    path('create/', CreateBattleView.as_view(), name='create-battle'),
    path('<uuid:battle_id>/join/', JoinBattleView.as_view(), name='join-battle'),
]
