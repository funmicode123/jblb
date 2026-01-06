from django.core.management.base import BaseCommand
from waitlist.models import Waitlist, EmailOutbox

class Command(BaseCommand):
    help = 'Clear all waitlist entries and email outbox for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--emails',
            nargs='+',
            type=str,
            help='Specific email addresses to delete (optional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all waitlist entries and email outbox records',
        )

    def handle(self, *args, **options):
        if options['emails']:
            # Delete specific emails
            for email in options['emails']:
                waitlist_entries = Waitlist.objects.filter(email=email)
                count = waitlist_entries.count()
                waitlist_entries.delete()
                
                outbox_entries = EmailOutbox.objects.filter(to=email)
                outbox_count = outbox_entries.count()
                outbox_entries.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted {count} waitlist entries and {outbox_count} email outbox entries for {email}'
                    )
                )
        elif options['all']:
            # Delete all entries
            waitlist_count = Waitlist.objects.count()
            outbox_count = EmailOutbox.objects.count()
            
            Waitlist.objects.all().delete()
            EmailOutbox.objects.all().delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted all {waitlist_count} waitlist entries and {outbox_count} email outbox entries'
                )
            )
        else:
            # Show usage if no arguments provided
            self.stdout.write(
                self.style.WARNING(
                    'Please specify either --emails <email1> <email2> ... or --all to delete entries'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Usage: python manage.py clear_waitlist --emails test@example.com'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Usage: python manage.py clear_waitlist --all'
                )
            )