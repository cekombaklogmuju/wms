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

_initialized = False

def init_once():
    global _initialized
    if _initialized:
        return
    _initialized = True
    if os.environ.get('VERCEL') or os.environ.get('AUTO_INIT_DB'):
        try:
            from init_db import run_init
            run_init()
        except Exception as e:
            import traceback
            traceback.print_exc()

def app(environ, start_response):
    init_once()
    return application(environ, start_response)
