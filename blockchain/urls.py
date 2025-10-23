from django.urls import path
from .views import AnomaIntentView, HederaPublishView
urlpatterns = [path('anoma/intent/', AnomaIntentView.as_view()), path('hedera/publish/', HederaPublishView.as_view())]
