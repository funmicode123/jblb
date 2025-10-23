from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.username or str(self.id)
