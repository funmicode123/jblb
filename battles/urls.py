from django.urls import path
from .views import CreateBasketView, CreateBattleView, JoinBattleView, ClubBasketListView


urlpatterns = [
    path('clubs/<uuid:club_id>/baskets/create/', CreateBasketView.as_view(), name='create-basket'),
    path("clubs/<uuid:club_id>/baskets", ClubBasketListView.as_view(), name="club-baskets"),
    path('create/', CreateBattleView.as_view(), name='create-battle'),
    path('<uuid:battle_id>/join/', JoinBattleView.as_view(), name='join-battle'),
]
