from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import BasketSerializer, BattleSerializer, ParticipantSerializer
from .services import join_battle
from .models import Basket, Battle, Participant
class CreateBasketView(APIView):
    def post(self, request):
        serializer = BasketSerializer(data=request.data); serializer.is_valid(raise_exception=True); b = serializer.save(); return Response(BasketSerializer(b).data)
class CreateBattleView(APIView):
    def post(self, request):
        serializer = BattleSerializer(data=request.data); serializer.is_valid(raise_exception=True); b = serializer.save(); return Response(BattleSerializer(b).data)
class JoinBattleView(APIView):
    def post(self, request, battle_id):
        p = join_battle(battle_id, request.data); return Response(ParticipantSerializer(p).data)
