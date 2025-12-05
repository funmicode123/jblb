from waitlist.services.email_service import render_verification_email
from waitlist.services.outbox_service import queue_email
from waitlist.models import EmailOutbox

def test_render_email_template():
    html = render_verification_email("JBLB-001", "https://example.com/verify")
    assert "JBLB-001" in html
    assert "Confirm My Spot" in html

def test_queue_email(db):
    queue_email("a@test.com", "Hello", "<h1>Hi</h1>")
    outbox = EmailOutbox.objects.first()

    assert outbox.to == "a@test.com"
    assert outbox.status == "PENDING"
