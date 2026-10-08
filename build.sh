#!/usr/bin/env bash
# Render build script: installs deps, collects static files, migrates, seeds.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input

# Wait for database to be ready (Render internal DNS may need a moment)
echo "Waiting for database..."
for i in {1..30}; do
  if python manage.py migrate --check 2>/dev/null; then
    echo "Database ready"
    break
  fi
  echo "Attempt $i: database not ready, waiting 2s..."
  sleep 2
done

python manage.py migrate

# Seed the catalogue (idempotent: products that already exist are skipped)
python seed_products.py

# Create an admin user only when all three env vars are set AND the user doesn't already exist
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created.')
else:
    print('Superuser already exists, skipping.')
"
fi