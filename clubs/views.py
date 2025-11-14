from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from clubs.serializers import ClubSerializer, JoinClubSerializer, ClubListSerializer
from clubs.services import club_service
from rest_framework.decorators import api_view, permission_classes
class CreateClubView(generics.CreateAPIView):
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        club = serializer.save()
        return Response(self.get_serializer(club).data, status=status.HTTP_201_CREATED)


class JoinClubView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        return club_service.join_club(request.user, club_id)


class LeaveClubView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        return club_service.leave_club(request.user, club_id)


class JoinedClubsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search")
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        return club_service.list_joined_clubs(request.user, search, page, page_size)


class ClubMembersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        return club_service.list_club_members(club_id, page, page_size)


class RemoveClubMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, club_id, member_id):
        return club_service.remove_member_from_club_by_admin(request.user, club_id, member_id)


class UpdateClubView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, club_id):
        return club_service.update_club_info(request.user, club_id, request.data)


class DeleteClubView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, club_id):
        return club_service.delete_club(request.user, club_id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_club_members_view(request, club_id):
    """
    List members in a specific club (Admin/Owner only)
    """
    return club_service.list_club_members(club_id)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_member_view(request, club_id, member_id):
    """
    Remove a member from a club (Admin/Owner only)
    """
    owner = request.user
    return club_service.remove_member_from_club_by_admin(owner, club_id, member_id)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_club_view(request, club_id):
    """
    Update club info (Owner only)
    """
    owner = request.user
    data = request.data
    return club_service.update_club_info(owner, club_id, data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_club_view(request, club_id):
    """
    Delete a club (Owner only)
    """
    owner = request.user
    return club_service.delete_club(owner, club_id)