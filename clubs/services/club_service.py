from blockchain.services.hedera_service import publish_intent, validate_token_balance
from clubs.models import Club, CommonNFT
import os
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from clubs.repository import club_repository
from clubs.repository.club_repository import get_free_common_nft, add_member_to_club
from clubs.services.hedera_service import mint_and_assign_common_nft


JBLB_TOKEN_ID = os.getenv("JBLB_TOKEN_ID", "0.0.999999")
MIN_JBLB_BALANCE = int(os.getenv("JBLB_MIN_BALANCE", 1))


def create_club(name, owner, owner_wallet, category="COMMON", tier="COMMON", access_type="Free", privileges="Basic yield farms from JBLB partners", description=""):
    if not owner_wallet:
        raise ValidationError("Hedera wallet required.")

    club = Club.objects.create(
        owner=owner,
        name=name,
        owner_wallet=owner_wallet,
        tier=tier,
        category=category,
        access_type=access_type,
        privileges=privileges,
        description=description,
    )
    add_member_to_club(club, owner)

    if tier == "COMMON":
        free_nft = CommonNFT.objects.filter(is_assigned=False).first()
        if free_nft:
            free_nft.is_assigned = True
            free_nft.club = club
            free_nft.save()

            club.nft_id = os.getenv("JBLB_COMMON_COLLECTION_ID")
            club.nft_serial = free_nft.serial
            club.metadata_cid = f"premint-{free_nft.serial}"
            club.save()

            print(f"Assigned pre-mint NFT: Serial {free_nft.serial}")
        else:
            print("Assign Common Nft club to user")
            nft_data = mint_and_assign_common_nft(club)
            club.nft_id = nft_data["nft_id"]
            club.nft_serial = nft_data["nft_serial"]
            club.metadata_cid = nft_data["metadata_cid"]
            club.save()
    else:
        raise ValidationError("Only COMMON tier supported for now.")

    return club


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