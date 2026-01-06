from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Waitlist
from battles.models import Player
from battles.services.hedera_service import transfer_jsparks
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Waitlist)
def handle_waitlist_verification(sender, instance, created, **kwargs):
    """
    Handle waitlist verification and create user account if needed.
    Also award 10 JSparks to the referrer when a referred user verifies their email.
    """
    # Only process when a waitlist entry is updated (not created) and is_verified changes to True
    if not created and instance.is_verified:
        try:
            # Check if this is the first time this user is verified (to prevent duplicate processing)
            if hasattr(instance, '_is_verified_previous') and instance._is_verified_previous:
                return
            
            # Create user account if it doesn't exist
            if not instance.user:
                user = User.objects.create_user(
                    username=instance.username,
                    email=instance.email
                )
                instance.user = user
                instance.save(update_fields=['user'])
                logger.info(f"Created user account for {instance.username}")
            
            # Award referral reward if this user was referred
            if instance.referred_by:
                award_referral_reward(instance.referred_by)
                
        except Exception as e:
            logger.error(f"Error handling waitlist verification: {str(e)}")

def award_referral_reward(referrer_waitlist):
    """
    Award 10 JSparks to the referrer.
    """
    try:
        # Check if referrer has a user account
        if referrer_waitlist.user:
            # Get or create player for referrer
            player, created = Player.objects.get_or_create(user=referrer_waitlist.user)
            
            # Award 10 JSparks
            player.jsparks_earned += 10
            player.save()
            
            # Transfer JSparks on Hedera blockchain
            try:
                transfer_jsparks(referrer_waitlist.user, 10)
                logger.info(f"Awarded 10 JSparks to referrer {referrer_waitlist.username}")
            except Exception as e:
                logger.error(f"Failed to transfer JSparks to {referrer_waitlist.username}: {str(e)}")
        else:
            logger.warning(f"Referrer {referrer_waitlist.username} has no user account")
            
    except Exception as e:
        logger.error(f"Error awarding referral reward: {str(e)}")

# Store previous state to detect changes
@receiver(post_save, sender=Waitlist)
def store_previous_state(sender, instance, **kwargs):
    """
    Store the previous state of is_verified to detect changes.
    """
    try:
        if instance.pk:
            old_instance = Waitlist.objects.get(pk=instance.pk)
            instance._is_verified_previous = old_instance.is_verified
    except Waitlist.DoesNotExist:
        pass