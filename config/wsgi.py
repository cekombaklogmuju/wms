"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Auto-migrate and seed for serverless cold-starts on Vercel / ephemeral environments
if os.environ.get('VERCEL') or os.environ.get('AUTO_INIT_DB'):
    try:
        from init_db import run_init
        run_init()
    except Exception as e:
        print(f"Auto-init error: {e}")

app = application
