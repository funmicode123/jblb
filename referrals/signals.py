from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReferralStats, ReferralNetwork
from waitlist.models import Waitlist
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Waitlist)
def update_referral_stats(sender, instance, **kwargs):
    """
    Update referral statistics when waitlist entries are verified
    """
    if instance.is_verified and instance.referred_by and instance.user:
        referral_network, created = ReferralNetwork.objects.get_or_create(
            referrer=instance.referred_by.user,
            referred_user=instance.user,
            waitlist_entry=instance,
            defaults={'is_verified': True}
        )
        
        if not created:
            referral_network.is_verified = True
            referral_network.save()
        
        referrer_stats, created = ReferralStats.objects.get_or_create(
            user=instance.referred_by.user
        )
        
        referrer_stats.total_referrals = instance.referred_by.referrals.count()
        referrer_stats.verified_referrals = instance.referred_by.referrals.filter(is_verified=True).count()
        referrer_stats.pending_referrals = instance.referred_by.referrals.filter(is_verified=False).count()
        referrer_stats.total_earnings = referrer_stats.verified_referrals * 10  # 10 JSparks per referral
        referrer_stats.save()