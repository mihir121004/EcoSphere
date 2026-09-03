# EcoSphere (Django E-commerce)

EcoSphere is a Django-based web application for browsing eco-friendly products, viewing categories, managing a shopping cart, checkout, and contacting/subscribing.

## Features

- Product browsing & categories
- Featured products on homepage
- Authentication (login/signup/logout)
- Shopping cart (add/update/remove items)
- Cart total calculation
- Checkout page
- Contact form (stores messages in DB)
- Newsletter subscription (stores unique emails)

## Tech Stack

- Python
- Django
- SQLite (default)
- HTML templates + static assets

## Project Structure

- `manage.py` — Django management entrypoint
- `ecosphere/` — project settings/urls
- `store/` — application (models, views, templates, static, migrations)
- `media/` — uploaded product images (served in development)
- `db.sqlite3` — local database

## Setup (Development)

1. (Recommended) Create and activate a virtual environment.
2. Install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```

   If you don’t have `requirements.txt` in this repo, install Django manually:

   ```bash
   pip install django
   ```

3. Run migrations:

   ```bash
   python manage.py migrate
   ```

4. (Optional) Create an admin user:

   ```bash
   python manage.py createsuperuser
   ```

5. Start the server:

   ```bash
   python manage.py runserver
   ```

6. Open in your browser:

   - http://127.0.0.1:8000

## Environment Variables / Settings Notes

- `DEBUG = True`
- The project uses Django’s console email backend (`EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend`).
- `MEDIA_URL` + `MEDIA_ROOT` are configured for development media serving.

## URLs (Main)

- `/` — homepage
- `/shop/` — shop page
- `/categories/` — categories list
- `/about/` — about page
- `/login/` — login
- `/signup/` — signup
- `/logout/` — logout
- `/cart/` — cart
- `/add-to-cart/<product_id>/` — add product to cart
- `/update-cart/` — update cart quantities (AJAX)
- `/remove-from-cart/` — remove cart item (AJAX)
- `/checkout/` — checkout
- `/place-order/` — order placeholder
- `/contact/` — contact form
- `/subscription/` — newsletter subscription

## Admin

- Django admin is available at: `/admin/`

## Media / Product Images

- Product images are expected under `media/` (and uploaded to `products/` via the `ImageField`).

## Notes

- To use the cart-related endpoints, you must be authenticated (views are `login_required`).

## License

Add your license here (or remove this section).

## Deploy to Render (Free)

The repo is pre-configured for one-click deployment via Render Blueprint.

### Option A — Blueprint (recommended)
1. Push this repo to GitHub.
2. Go to https://dashboard.render.com → **New** → **Blueprint** → select the repo.
3. Render reads `render.yaml` and creates:
   - a free web service (gunicorn + WhiteNoise)
   - a free PostgreSQL database (`DATABASE_URL` is wired automatically)
4. Optional: fill in `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` when prompted to get an admin account created on first build.
5. Deploy. Done.

### Option B — Manual
1. **New** → **Web Service** → connect the repo.
2. Runtime: Python · Build: `./build.sh` · Start: `gunicorn ecosphere.wsgi:application --bind 0.0.0.0:$PORT`
3. Add env vars: `PYTHON_VERSION=3.14.0`, `DEBUG=False`, `SECRET_KEY=<random>`, plus `DJANGO_SUPERUSER_*` if you want an admin.
4. **New** → **Postgres** (free) and copy its *Internal Database URL* into the web service's `DATABASE_URL` var.

### How it works on Render
- `build.sh` installs deps → `collectstatic` → `migrate` → seeds the 29-product catalogue (idempotent) → optionally creates the superuser.
- Static files are served by **WhiteNoise** (no CDN needed).
- Product images ship **inside the git repo** (`media/products/`), so they survive Render's ephemeral disk on every deploy — the seeder references them by deterministic name.
- Render free-tier notes: the web service sleeps after ~15 min idle (first visit is slow), and the free Postgres expires after 30 days — upgrade the DB plan or re-create it to keep data.

### Local development
Works exactly as before: `python manage.py runserver` uses SQLite + DEBUG=True with no env vars required.


