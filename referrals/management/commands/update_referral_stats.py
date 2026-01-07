from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from waitlist.models import Waitlist
from referrals.models import ReferralStats
from django.db.models import Count

User = get_user_model()

class Command(BaseCommand):
    help = 'Update referral statistics for all users based on waitlist data'

    def handle(self, *args, **options):
        # Get all waitlist entries that have a referrer
        waitlist_with_referrer = Waitlist.objects.filter(
            referred_by__isnull=False
        ).select_related('referred_by__user', 'user')

        # Create a dictionary to count referrals per referrer
        referrer_counts = {}
        
        for entry in waitlist_with_referrer:
            if entry.referred_by.user:
                referrer_id = entry.referred_by.user.id
                if referrer_id not in referrer_counts:
                    referrer_counts[referrer_id] = {'total': 0, 'verified': 0}
                
                referrer_counts[referrer_id]['total'] += 1
                if entry.is_verified:
                    referrer_counts[referrer_id]['verified'] += 1

        # Update referral stats for each referrer
        for user_id, counts in referrer_counts.items():
            user = User.objects.get(id=user_id)
            stats, created = ReferralStats.objects.get_or_create(user=user)
            
            stats.total_referrals = counts['total']
            stats.verified_referrals = counts['verified']
            stats.pending_referrals = counts['total'] - counts['verified']
            stats.total_earnings = counts['verified'] * 10  # 10 JSparks per verified referral
            
            stats.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated stats for {user.username}: {counts["verified"]} verified referrals'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated referral stats for {len(referrer_counts)} users'
            )
        )