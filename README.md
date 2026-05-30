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

