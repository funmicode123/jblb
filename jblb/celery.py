import os
import django
import sys
from celery import Celery

# Workaround for EntryPoint compatibility issue
try:
    from importlib_metadata import entry_points
    # Patch the entry_points function if needed
    if hasattr(entry_points(), 'get') is False:
        def patched_entry_points():
            def get(group=None):
                if group is None:
                    return entry_points()
                return [ep for ep in entry_points() if ep.group == group]
            return type('EntryPoints', (), {'get': get})()
        
        # Replace the original entry_points function
        import celery.bin.celery
        original_entry_points = entry_points
        celery.bin.celery.entry_points = patched_entry_points
except ImportError:
    pass

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jblb.settings')

# Setup Django
django.setup()

# Create the Celery app
app = Celery('jblb')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Print discovered tasks for debugging
print("Discovered tasks:", app.tasks.keys())

# Explicitly import task modules to ensure they are registered
from waitlist import tasks as waitlist_tasks
