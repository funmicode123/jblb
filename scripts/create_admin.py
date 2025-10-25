# scripts/create_admin.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jblb.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@example.com', 'Your$trongP@ssw0rd')
    print("Created admin")
else:
    print("Admin exists")
