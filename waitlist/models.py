from datetime import timezone, timedelta

from django.db import models


def generate_custom_id():
    last = Waitlist.objects.order_by('-id').first()
    if not last:
        return "JBLB-001"
    num = int(last.custom_id.split('-')[-1])
    return f"JBLB-{str(num + 1).zfill(3)}"

def is_token_expired(self):
    if not self.token_created_at:
        return True
    return timezone.now() > self.token_created_at + timedelta(hours=24)

class Waitlist(models.Model):
    custom_id = models.CharField(max_length=20, unique=True, default=generate_custom_id)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    token_created= models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} <{self.email}>"

    class Meta:
        verbose_name_plural = "Waitlist"


class EmailOutbox(models.Model):
    to= models.EmailField()
    subject = models.CharField(max_length=255)
    html = models.CharField()
    status = models.CharField(max_length=20,
                              choices=[
                                  ('PENDING', "pending"),
                                  ("SENT", "sent"),
                                  ("FAILED", "failed"),
                              ], default='PENDING')
    retries=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
