from django.urls import path
from .views import (PostWaitlistAPIView, VerifyWaitlistView,
                    ListWaitlistAPIView, ReferralStatsView)


urlpatterns = [
    path('submit/', PostWaitlistAPIView.as_view(), name='waitlist'),
    path('verify/', VerifyWaitlistView.as_view(), name='verify-waitlist'),
    path('list/', ListWaitlistAPIView.as_view(), name='waitlist-list'),
    path('referrals/', ReferralStatsView.as_view(), name='referral-stats'),
]