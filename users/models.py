from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.encryption import decrypt_value
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    hedera_account_id = models.CharField(max_length=100, blank=True, null=True)
    hedera_public_key = models.TextField(blank=True, null=True)
    hedera_private_key = models.TextField(blank=True, null=True)


    def get_hedera_keys(self):
        return {
            "account_id": self.hedera_account_id,
            "public_key": decrypt_value(self.hedera_public_key),
            "private_key": decrypt_value(self.hedera_private_key)
        }

    def __str__(self):
        return self.username or str(self.id)
