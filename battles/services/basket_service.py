from rest_framework.response import Response
from rest_framework import status
from battles.repositories.basket_repository import BasketRepository
from battles.serializers import BasketSerializer
from battles.validator import validate_tokens
from clubs.models import Club
from clubs.repository import club_repository
from rest_framework.exceptions import ValidationError, PermissionDenied


class BasketService:
    @staticmethod
    def create_basket(user, club_id, name, tokens):
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            raise ValidationError ("Club not found.")

        if user not in club.members.all():
            raise PermissionDenied("You must join the club before creating a basket.")

        if not user.hedera_account_id:
            raise ValidationError ("User wallet address not found.")


        validate_tokens(tokens)

        total_weight = sum(token["weight"] for token in tokens)

        basket = BasketRepository.create_basket({
            "club": club,
            "creator": user,
            "creator_wallet": user.hedera_account_id,
            "name": name,
            "tokens": tokens,
            "total_weight": total_weight,
            "initial_value": 100,
            "current_value": 100,
            "oracle_source": "pyth"
        })
        return basket

    @staticmethod
    def get_basket(basket_id):
        basket = BasketRepository.get_basket_by_id(basket_id)
        if not basket:
            raise ValidationError("Basket not found.")
        return basket

    @staticmethod
    def list_baskets_for_club(club_id):
        return BasketRepository.list_baskets_by_club(club_id)
