"""
WSGI config for BD project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# Use BD_FAZENDA settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BD_FAZENDA.settings')

# Initialize Django
application = get_wsgi_application()

# Optional: Run migrations automatically on Vercel
def init():
    """Initialize application on first run"""
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✓ Migrations completed")
    except Exception as e:
        print(f"⚠ Migration warning: {e}")

try:
    init()
except Exception as e:
    print(f"⚠ Init warning: {e}")
