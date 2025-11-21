from django.urls import path
from .views import WaitlistAPIView

urlpatterns = [
    path('api/waitlist/', WaitlistAPIView.as_view(), name='waitlist'),
]