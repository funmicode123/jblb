import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from waitlist.models import Waitlist, EmailOutbox


@pytest.mark.django_db
@patch("waitlist.services.outbox_service.queue_email")
def test_submit_waitlist_success(mock_queue):
    client = APIClient()

    res = client.post("/api/waitlist/submit/", {
        "username": "funmi",
        "email": "funmi@example.com"
    })

    assert res.status_code == 201
    assert Waitlist.objects.count() == 1
    assert mock_queue.called

@pytest.mark.django_db
def test_duplicate_email_rejected():
    Waitlist.objects.create(username="x", email="dup@example.com")

    client = APIClient()
    res = client.post("/api/waitlist/submit/", {
        "username": "newuser",
        "email": "dup@example.com"
    })

    assert res.status_code == 400

@pytest.mark.django_db
def test_verify_token_flow():
    client = APIClient()

    # create user
    res = client.post("/api/waitlist/submit/", {
        "username": "funmi2",
        "email": "funmi2@example.com"
    })

    waitlist = Waitlist.objects.first()
    token = waitlist.verification_token

    # verify
    res2 = client.get(f"/api/waitlist/verify/?token={token}")

    assert res2.status_code == 200

    waitlist.refresh_from_db()
    assert waitlist.is_verified is True

@pytest.mark.django_db
def test_rate_limit():
    client = APIClient()

    for _ in range(3):
        client.post("/api/waitlist/submit/", {
            "username": "test",
            "email": "limit@example.com"
        })

    res = client.post("/api/waitlist/submit/", {
        "username": "test2",
        "email": "limit@example.com"
    })

    assert res.status_code == 429
