from django.urls import path
from .views import (
    ReferralDashboardView,
    ReferralNetworkView, 
    LeaderboardView,
    RefreshLeaderboardView
)

urlpatterns = [
    path('dashboard/', ReferralDashboardView.as_view(), name='referral-dashboard'),
    path('network/', ReferralNetworkView.as_view(), name='referral-network'),
    path('leaderboard/', LeaderboardView.as_view(), name='referral-leaderboard'),
    path('refresh-leaderboard/', RefreshLeaderboardView.as_view(), name='refresh-leaderboard'),
]