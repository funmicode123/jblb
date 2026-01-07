from django.db import models
from django.contrib.auth import get_user_model
from waitlist.models import Waitlist
from django.utils import timezone
import uuid

User = get_user_model()

class ReferralStats(models.Model):
    """
    Tracks referral statistics for each user
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_stats')
    total_referrals = models.PositiveIntegerField(default=0)
    verified_referrals = models.PositiveIntegerField(default=0)
    pending_referrals = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=4, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Referral Statistics"
    
    def __str__(self):
        return f"{self.user.username} - {self.verified_referrals} referrals"

class LeaderboardEntry(models.Model):
    """
    Cached leaderboard entry for performance
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    username = models.CharField(max_length=100)
    verified_referrals = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=4, default=0.0)
    rank = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-verified_referrals', '-total_earnings']
        indexes = [
            models.Index(fields=['rank']),
            models.Index(fields=['verified_referrals']),
        ]
    
    def __str__(self):
        return f"#{self.rank} {self.username} - {self.verified_referrals} referrals"

class ReferralNetwork(models.Model):
    """
    Tracks the referral network relationships
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outgoing_referrals')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incoming_referrals')
    waitlist_entry = models.ForeignKey(Waitlist, on_delete=models.CASCADE, related_name='referral_network')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['referrer', 'referred_user']
        indexes = [
            models.Index(fields=['referrer']),
            models.Index(fields=['referred_user']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"