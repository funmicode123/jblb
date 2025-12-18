import os
import logging
from celery import shared_task
from resend import Emails
from .models import EmailOutbox

logger = logging.getLogger(__name__)

# Removed global resend.api_key assignment

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries":3, "countdown": 30})
def process_outbox(self):
    print("PROCESS_OUTBOX TASK STARTED")
    logger.info("Starting to process email outbox...")
    
    import resend
    resend.api_key = os.getenv('RESEND_API_KEY')
    
    pending = EmailOutbox.objects.filter(status="PENDING")[:50]
    logger.info(f"Found {pending.count()} pending emails to process")

    if pending.count()==0:
        logger.info('No pending emails exist')
        return

    for item in pending:
        try:
            logger.info(f"Sending email to {item.to}")
            resend.Emails.send({
                "from": "JBLB <send@yieldsport.xyz>",
                "to": [item.to],
                "subject": item.subject,
                "html": item.html,
            })

            item.status = "SENT"
            logger.info(f"Email to {item.to} sent successfully")

        except Exception as e:
            logger.error(f"Failed to send email to {item.to}: {str(e)}")
            item.retries += 1
            item.status = "FAILED" if item.retries > 3 else "PENDING"

        item.save()
    
    logger.info("Finished processing email outbox")