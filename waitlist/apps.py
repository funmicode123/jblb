from django.apps import AppConfig


class WaitlistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'waitlist'

    def ready(self):
        import waitlist.signals