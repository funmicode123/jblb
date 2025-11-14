from blockchain.services.hedera_service import publish_intent, validate_token_balance
from clubs.models import Club
import os
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from clubs.repository import club_repository


JBLB_TOKEN_ID = os.getenv("JBLB_TOKEN_ID", "0.0.999999")
MIN_JBLB_BALANCE = int(os.getenv("JBLB_MIN_BALANCE", 1))


def create_club(name, owner, owner_wallet, category="COMMON", tier="COMMON", access_type="Free", privileges=""):
    """
    Creates a Club record in Django + publishes a blockchain mint intent.
    Requires the user to hold a minimum amount of JBLB tokens.
    """

    has_tokens = validate_token_balance(owner_wallet, JBLB_TOKEN_ID, min_balance=MIN_JBLB_BALANCE)
    if not has_tokens:
        return {
            "status": "failed",
            "message": f"Insufficient JBLB balance. You must hold at least {MIN_JBLB_BALANCE} $JBLB tokens to create a club."
        }

    intent = {
        "type": "mint_club_nft",
        "name": name,
        "owner_wallet": owner_wallet,
        "tier": tier,
        "category": category,
    }

    result = publish_intent(intent)

    return {
        "status": "success",
        "nft_id": result.get("nft_id", "mock-nft"),
        "tx_hash": result.get("tx_hash", "mock-hash"),
    }

def join_club(user, club_id):
    club = club_repository.get_club_by_id(club_id)

    if club_repository.user_in_club(club, user):
        return Response({"error": "Already a member of this club."}, status=status.HTTP_400_BAD_REQUEST)

    club_repository.add_member_to_club(club, user)
    return Response({"message": f"{user.username} successfully joined {club.name}"}, status=status.HTTP_200_OK)


def leave_club(user, club_id):
    club = club_repository.get_club_by_id(club_id)

    if not club_repository.user_in_club(club, user):
        return Response({"error": "You are not a member of this club."}, status=status.HTTP_400_BAD_REQUEST)

    club_repository.remove_member_from_club(club, user)
    return Response({"message": f"{user.username} has left {club.name}"}, status=status.HTTP_200_OK)


def list_joined_clubs(user, search_query=None, page=1, page_size=10):
    from clubs.serializers import ClubListSerializer

    clubs = club_repository.get_joined_clubs(user, search_query)
    paginator = Paginator(clubs, page_size)
    page_obj = paginator.get_page(page)
    serializer = ClubListSerializer(page_obj, many=True)

    return Response({
        "results": serializer.data,
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    }, status=status.HTTP_200_OK)


def list_club_members(club_id, page=1, page_size=10):
    from users.serializers import PublicUserSerializer
    club = club_repository.get_club_by_id(club_id)
    members = club_repository.get_club_members(club)

    paginator = Paginator(members, page_size)
    page_obj = paginator.get_page(page)
    serializer = PublicUserSerializer(page_obj, many=True)

    return Response({
        "club": club.name,
        "members": serializer.data,
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    }, status=status.HTTP_200_OK)


def remove_member_from_club_by_admin(owner, club_id, member_id):
    club = club_repository.get_club_by_id(club_id)

    if not club_repository.is_owner(club, owner):
        return Response({"error": "Only the club owner can remove members."}, status=status.HTTP_403_FORBIDDEN)

    member = club.members.filter(id=member_id).first()
    if not member:
        return Response({"error": "Member not found in this club."}, status=status.HTTP_404_NOT_FOUND)

    club_repository.remove_member_from_club(club, member)
    return Response({"message": f"{member.username} has been removed from {club.name}."}, status=status.HTTP_200_OK)


def update_club_info(owner, club_id, data):
    from clubs.serializers import ClubUpdateSerializer

    club = club_repository.get_club_by_id(club_id)
    if not club_repository.is_owner(club, owner):
        return Response({"error": "Only the club owner can update this club."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ClubUpdateSerializer(club, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_club(owner, club_id):
    club = club_repository.get_club_by_id(club_id)
    if not club_repository.is_owner(club, owner):
        return Response({"error": "Only the club owner can delete this club."}, status=status.HTTP_403_FORBIDDEN)

    club.delete()
    return Response({"message": f"Club '{club.name}' has been deleted."}, status=status.HTTP_200_OK)