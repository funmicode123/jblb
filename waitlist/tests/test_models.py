from waitlist.models import Waitlist
from django.utils import timezone
from datetime import timedelta

def test_custom_id_auto_generation(db):
    w = Waitlist.objects.create(username="test", email="test@example.com")
    assert w.custom_id.startswith("JBLB-")

def test_token_expiry(db):
    w = Waitlist.objects.create(username="aa", email="aa@example.com")
    w.token_created = timezone.now() - timedelta(hours=25)
    assert w.token_created is not None
    assert w.token_created < timezone.now() - timedelta(hours=24)
