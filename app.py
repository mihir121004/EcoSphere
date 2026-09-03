"""
Render-compatibility entrypoint.

Render's default start command for Python services is `gunicorn app:app`.
This module exposes the Django WSGI application under that name so the
service boots correctly even if the start command is left at its default.

The documented/preferred start command is:
    gunicorn ecosphere.wsgi:application --bind 0.0.0.0:$PORT

See also gunicorn.conf.py, which binds to 0.0.0.0:$PORT automatically.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecosphere.settings')

application = get_wsgi_application()
