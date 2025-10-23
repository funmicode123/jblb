from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/clubs/', include('clubs.urls')),
    path('api/battles/', include('battles.urls')),
    path('api/blockchain/', include('blockchain.urls')),
]
