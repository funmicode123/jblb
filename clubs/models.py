from django.db import models
import uuid
from django.conf import settings
from users.models import User
from clubs.constant import CLUB_TIERS, CLUB_TIER_CHOICES


class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_clubs", null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
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
    nft_serial = models.BigIntegerField(null=True, blank=True)
    metadata_cid = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="joined_clubs", blank=True)


    def __str__(self):
        return f"{self.name} ({self.tier})"

    @property
    def tier_config(self):
        return CLUB_TIERS.get(self.tier, {})