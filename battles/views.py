from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import BasketSerializer, BattleSerializer, PlayerSerializer
from .services.hedera_service import join_battle
from .models import Basket, Battle, Player
from battles.services.basket_service import BasketService


class CreateBasketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        serializer = BasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket_data = serializer.validated_data

        wallet_address = getattr(request.user, "hedera_account_id", None)
        if not wallet_address:
            return Response(
                {"error": "User wallet address not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            basket = BasketService.create_basket(
                user=request.user,
                club_id=club_id,
                basket_data=basket_data
            )
            return Response(BasketSerializer(basket).data,
                            status=status.HTTP_201_CREATED)

        except (ValueError, PermissionError) as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClubBasketListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        """
        List all baskets under a club.
        """
        baskets = BasketService.list_baskets_for_club(club_id)
        serializer = BasketSerializer(baskets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateBattleView(APIView):
    def post(self, request):
        serializer = BattleSerializer(data=request.data); serializer.is_valid(raise_exception=True); b = serializer.save(); return Response(BattleSerializer(b).data)


class JoinBattleView(APIView):
    def post(self, request, battle_id):
        p = join_battle(battle_id, request.data); return Response(PlayerSerializer(p).data)
