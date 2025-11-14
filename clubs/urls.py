from django.urls import path
from .views import (
    CreateClubView,
    LeaveClubView,
    JoinClubView,
    JoinedClubsListView,
    ClubMembersListView,
    RemoveClubMemberView,
    UpdateClubView,
    DeleteClubView,
)


urlpatterns = [
    path('create/', CreateClubView.as_view(), name='create-club'),
    path('<uuid:club_id>/join/', JoinClubView.as_view(), name='join-club'),
    path("<uuid:club_id>/leave/", LeaveClubView.as_view(), name="leave-club"),
    path("joined/", JoinedClubsListView.as_view(), name="joined-clubs"),
    path("<uuid:club_id>/members/", ClubMembersListView.as_view(), name="club-members"),

# 🔐 Admin-only actions
    path("<uuid:club_id>/members/<uuid:member_id>/remove/", RemoveClubMemberView.as_view(), name="remove-member"),
    path("<uuid:club_id>/update/", UpdateClubView.as_view(), name="update-club"),
    path("<uuid:club_id>/delete/", DeleteClubView.as_view(), name="delete-club"),
]
