# EcoSphere (Django E-Commerce)

A Django-based e-commerce web application with product browsing, category filtering, cart management, checkout, and order tracking. Includes basic user auth (signup/login/profile) and informational pages (shipping, returns, privacy, terms, etc.).

## Features

- Product catalog & shop page
  - Category filter
  - Price-range filter
  - Featured products on homepage
- Authentication
  - Signup / Login / Logout
  - Password change
  - Profile page showing current and delivered orders
  - Forgot password page (UI)
- Cart
  - Add to cart (AJAX endpoint)
  - Update quantity (AJAX endpoint)
  - Remove item (AJAX endpoint)
  - Cart total calculation
- Orders
  - Checkout and place order
  - Order tracking page by `order_id`
  - Invoice page by `order_id`
  - Demo payment flow for `upi` and `card`; COD support
- Other pages
  - About, Contact, Help Center
  - Shipping & Delivery, Returns & Refunds
  - Privacy Policy, Terms & Conditions
- Media & static support
  - Product images stored under `products/`

## Tech Stack

- Python 3
- Django 5.2+

## Project Structure

- `manage.py` — Django entry point
- `ecosphere/` — Django project settings/URLs
- `store/` — main app (models, views, urls, templates)
- `media/` — uploaded images
- `products/` — (folder present in repo; product images are configured via Django `ImageField` upload)

## Setup

### 1) Create & activate a virtual environment

```bash
python -m venv env
source env/bin/activate
```

### 2) Install dependencies

If you have a `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

Otherwise, ensure Django and Pillow are installed (for image uploads):

```bash
pip install django pillow
```

### 3) Configure secrets

This project has a `SECRET_KEY` and `DEBUG=True` in `ecosphere/settings.py` (development use).

### 4) Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5) Create a superuser (optional)

```bash
python manage.py createsuperuser
```

## Run the server

```bash
python manage.py runserver
```

Then open:

- Home: `http://127.0.0.1:8000/`
- Shop: `http://127.0.0.1:8000/shop/`
- Cart: `http://127.0.0.1:8000/cart/`

## Key Endpoints

- `/` — homepage
- `/shop/` — product listing + filters
- `/add-to-cart/<product_id>/` — AJAX: add item to cart
- `/update-cart/` — AJAX: update cart item quantity
- `/remove-from-cart/` — AJAX: remove item from cart
- `/checkout/` — checkout page
- `/place-order/` — POST: create order + demo payment handling
- `/order-tracking/<order_id>/` — order status display
- `/invoice/<order_id>/` — invoice view
- `/login/`, `/signup/`, `/logout/`
- `/profile/` — current & previous orders

## Admin

Access Django admin at:

- `/admin/`

## Email

Email is configured to use Django’s console backend:

- `EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend`

Subscription form sends an admin notification using `send_mail()` when a new email subscribes.

## Notes / Development Details

- This is a development configuration: `DEBUG=True`.
- `ALLOWED_HOSTS` includes ngrok subdomains.
- Media serving is enabled in `store/urls.py` when `DEBUG` is on.

## TODO

See [`TODO.md`](./TODO.md) for the current development checklist.

# EcoSphere
