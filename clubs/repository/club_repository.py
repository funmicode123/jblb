from django.shortcuts import get_object_or_404
from django.db.models import Q
from clubs.models import Club, CommonNFT


def get_club_by_id(club_id):
    return get_object_or_404(Club, id=club_id)


def user_in_club(club, user):
    return club.members.filter(id=user.id).exists()


def add_member_to_club(club, user):
    club.members.add(user)
    club.save()


def remove_member_from_club(club, user):
    club.members.remove(user)
    club.save()


def get_joined_clubs(user, search_query=None):
    clubs = Club.objects.filter(members=user)
    if search_query:
        clubs = clubs.filter(name__icontains=search_query)
    return clubs.order_by('-created_at')


def get_club_members(club):
    return club.members.all()


def is_owner(club, user):
    return club.owner == user


def get_free_common_nft():
    return CommonNFT.objects.filter(is_assigned=False).first()
