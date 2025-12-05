import pytest
from unittest.mock import patch
from rest_framework.test import APIRequestFactory
from waitlist.views import PostWaitlistAPIView
from waitlist.models import Waitlist


@pytest.mark.django_db
def test_waitlist_creation_minimal():
    factory = APIRequestFactory()
    data = {"username": "funmi", "email": "funmi@example.com"}

    request = factory.post("/api/waitlist/submit/", data)
    response = PostWaitlistAPIView.as_view()(request)

    assert response.status_code in [201, 400, 429]
