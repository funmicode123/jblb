from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import BasketSerializer, BattleSerializer, PlayerSerializer
from .services.hedera_service import join_battle
from .models import Basket, Battle, Player
class CreateBasketView(APIView):
    def post(self, request):
        serializer = BasketSerializer(data=request.data); serializer.is_valid(raise_exception=True); b = serializer.save(); return Response(BasketSerializer(b).data)
class CreateBattleView(APIView):
    def post(self, request):
        serializer = BattleSerializer(data=request.data); serializer.is_valid(raise_exception=True); b = serializer.save(); return Response(BattleSerializer(b).data)
class JoinBattleView(APIView):
    def post(self, request, battle_id):
        p = join_battle(battle_id, request.data); return Response(PlayerSerializer(p).data)
