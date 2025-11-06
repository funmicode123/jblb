from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from battles.services.wallet_service import create_user_wallet


@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        wallet = create_user_wallet(instance)
        instance.wallet_address = wallet["account_id"]
        instance.save()
