#!/usr/bin/env bash
# Render build script: installs deps, collects static files, migrates, seeds.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed the catalogue (idempotent: products that already exist are skipped)
python seed_products.py

# Create an admin user only when all three env vars are configured on Render
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput
fi
