"""
Gunicorn configuration (auto-loaded by gunicorn from this directory).

Makes the server bind to 0.0.0.0:$PORT as required by Render, so the
service works with Render's default start command (`gunicorn app:app`)
as well as the documented one.
"""
import os

# Render injects PORT; fall back to 8000 for local runs
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Free tier: single worker keeps memory low
workers = int(os.environ.get('WEB_CONCURRENCY', '1'))

timeout = 120
accesslog = '-'
errorlog = '-'
