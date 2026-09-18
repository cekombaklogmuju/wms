import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = get_wsgi_application()

if os.environ.get('VERCEL'):
    try:
        from init_db import run_init
        run_init()
    except Exception as e:
        print(f"Init error: {e}")
