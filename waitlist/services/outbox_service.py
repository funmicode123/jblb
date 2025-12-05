from ..models import EmailOutbox

def queue_email(to, subject, html):
    EmailOutbox.objects.create(
        to=to,
        subject=subject,
        html=html,
        status="PENDING"
    )
