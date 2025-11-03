from django.urls import path
from .views import ProfileView, SignupView, LoginView

urlpatterns = [path('me/', ProfileView.as_view(), name='profile'),
path("signup/", SignupView.as_view(), name="signup"),
path("login/", LoginView.as_view(), name="login")
               ]
