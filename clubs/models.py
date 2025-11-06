from django.db import models
import uuid
from users.models import User
from clubs.constant import CLUB_TIERS, CLUB_TIER_CHOICES


class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clubs", null=True, blank=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CLUB_TIER_CHOICES, default="COMMON")
    owner_wallet = models.CharField(max_length=255, blank=True, null=True)

    tier = models.CharField(
        max_length=20,
        choices=CLUB_TIER_CHOICES,
        default="COMMON",
    )

    access_type = models.CharField(max_length=50, default="Free")
    privileges = models.TextField(blank=True, null=True)
    nft_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} ({self.tier})"
