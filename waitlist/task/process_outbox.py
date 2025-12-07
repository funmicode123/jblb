from celery import shared_task
import resend
from ..models import EmailOutbox

@shared_task
def process_outbox():
    pending = EmailOutbox.objects.filter(status="PENDING")[:50]

    for item in pending:
        try:
            resend.Emails.send({
                "from": "JBLB <send@yieldsport.xyz>",
                "to": [item.to],
                "subject": item.subject,
                "html": item.html,
            })

            item.status = "SENT"

        except Exception:
            item.retries += 1
            item.status = "FAILED" if item.retries > 3 else "PENDING"

        item.save()
