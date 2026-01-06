from django.urls import path
from .views import PostWaitlistAPIView, VerifyWaitlistView, ListWaitlistAPIView, ReferralStatsView, ClearWaitlistView

urlpatterns = [
    path('submit/', PostWaitlistAPIView.as_view(), name='waitlist'),
    path('verify/', VerifyWaitlistView.as_view(), name='verify-waitlist'),
    path('list/', ListWaitlistAPIView.as_view(), name='waitlist-list'),
    path('referral-stats/', ReferralStatsView.as_view(), name='referral-stats'),
    path('clear/', ClearWaitlistView.as_view(), name='clear-waitlist'),
]