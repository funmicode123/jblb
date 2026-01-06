import secrets
from datetime import timezone, timedelta
from django.db import models
from users.models import User


# def generate_custom_id():
#     last = Waitlist.objects.order_by('-id').first()
#     if not last:
#         return "JBLB-001"
#     num = int(last.custom_id.split('-')[-1])
#     return f"JBLB-{str(num + 1).zfill(3)}"


class Waitlist(models.Model):
    custom_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    token_created = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True, unique=True, db_index=True)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.referral_code:
            while True:
                code = secrets.token_urlsafe(8)[:10].upper()
                if not Waitlist.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break

        if is_new and not self.custom_id:
            self.custom_id = f"JBLB-{str(0).zfill(5)}"

        super().save(*args, **kwargs)

        if is_new and self.custom_id == f"JBLB-{str(0).zfill(5)}":
            self.custom_id = f"JBLB-{str(self.pk).zfill(5)}"
            super().save(update_fields=["custom_id"])

    def is_token_expired(self):
        if not self.token_created:
            return True
        return timezone.now() > self.token_created + timedelta(hours=24)

    def __str__(self):
        return f"{self.username} <{self.email}>"

    class Meta:
        verbose_name_plural = "Waitlist"


class EmailOutbox(models.Model):
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    html = models.TextField()
    status = models.CharField(max_length=20,
                              choices=[
                                  ('PENDING', "pending"),
                                  ("SENT", "sent"),
                                  ("FAILED", "failed"),
                              ], default='PENDING')
    retries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
