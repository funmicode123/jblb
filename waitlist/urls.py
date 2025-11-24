from django.urls import path
from .views import PostWaitlistAPIView, ListWaitlistAPIView

urlpatterns = [
    path('submit/', PostWaitlistAPIView.as_view(), name='waitlist'),
    path('list/', ListWaitlistAPIView.as_view(), name='waitlist'),
]