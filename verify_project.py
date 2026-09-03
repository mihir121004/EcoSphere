"""
Full end-to-end verification of the EcoSphere project.
Run:  python manage.py shell < verify_project.py
"""
import re
from django.test import Client
from django.test.utils import setup_test_environment
from django.test.runner import DiscoverRunner
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order, ContactMessage, Subscription

setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old_config = runner.setup_databases()

c = Client()

# Seed data if missing (DB is fresh test DB)
cats_data = [
    ("Personal Care", ["Bamboo Toothbrush|9.99|bamboo_toothbrush.jpg", "Organic Soap|5.99|organic_soap.jpg", "Natural Shampoo Bar|14.50|natural_shampoo.jpg"]),
    ("Kitchen & Dining", ["Compostable Cutlery|4.99|compostable_cutlery.jpg", "Glass Food Container|24.99|glass_food_container.jpg", "Organic Spices|12.00|organic_spices.jpg"]),
    ("Home & Living", ["Compost Bin|49.99|compost_bin.jpg", "LED Bulbs|19.99|energy-efficient_LED_bulbs.jpg", "Metal Water Bottle|29.99|metal_water_bottle.png"]),
    ("Clothing & Accessories", ["Cloth Shopping Bag|7.99|cloth_shopping_bag.jpg", "Hemp T-Shirt|25.00|hemp_clothing.jpg", "Organic Cotton Tee|22.50|organic_cotton_t-shirt.jpg"]),
    ("Office Supplies", ["Plantable Pen|2.99|eco-friendly_pen.jpg", "Seed Pencil|1.99|plantable_seed_pencil.jpg"]),
    ("Outdoor & Sports", ["Eco Footwear|89.99|eco-friendly_footware.jpg"]),
    ("Cleaning Products", ["Cleaning Liquid|9.50|eco-friendly_cleaning_liquid.jpg", "Garbage Bags|6.50|biodegradable_garbage_bag.jpg"]),
]
for cat_name, prods in cats_data:
    cat, _ = Category.objects.get_or_create(name=cat_name)
    for p in prods:
        name, price, img = p.split("|")
        Product.objects.get_or_create(
            name=name,
            defaults=dict(price=price, category=cat, stock=50,
                          image=f"products/{img}", image_name=img,
                          description=f"Eco-friendly {name.lower()}",
                          is_available=True, is_featured=False),
        )
for name in ["Bamboo Toothbrush", "Compost Bin", "Metal Water Bottle", "Hemp T-Shirt"]:
    Product.objects.filter(name=name).update(is_featured=True, stock=25)

passed, failed = 0, []

def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed.append(name)
        print(f"FAIL  {name}  {detail}")

print("=" * 60)
print("1. PUBLIC PAGES")
print("=" * 60)

r = c.get("/")
check("Homepage 200", r.status_code == 200)
check("Homepage shows featured", b"Bamboo Toothbrush" in r.content)
check("Homepage has add-to-cart buttons", b"add-to-cart" in r.content)

r = c.get("/shop/")
check("Shop 200", r.status_code == 200)
check("Shop shows all products", b"Organic Soap" in r.content)

r = c.get("/categories/")
check("Categories 200", r.status_code == 200)
check("Categories shows real category", b"Personal Care" in r.content)
check("Categories shows product count", b"products available" in r.content or b"product available" in r.content)

for url in ["/about/", "/contact/", "/help/", "/login/", "/signup/", "/forgot-password/"]:
    r = c.get(url)
    check(f"Page {url} 200", r.status_code == 200, f"status={r.status_code}")

print()
print("=" * 60)
print("2. FILTERS")
print("=" * 60)

cat = Category.objects.get(name="Personal Care")
r = c.get(f"/shop/?category={cat.id}")
check("Category filter works", b"Bamboo Toothbrush" in r.content and b"Metal Water Bottle" not in r.content)
check("Category filter active state", b"active" in r.content)

r = c.get("/shop/?price=under_20")
check("Price under_20", b"Seed Pencil" in r.content and b"Compost Bin" not in r.content)
r = c.get("/shop/?price=20_to_50")
check("Price 20-50 returns 200", r.status_code == 200)
r = c.get("/shop/?price=50_to_100")
check("Price 50-100 has results", b"Metal Water Bottle" in r.content or b"Eco Footwear" in r.content)
r = c.get("/shop/?price=above_100")
check("Price above_100 correct (no <100 items)", b"Bamboo Toothbrush" not in r.content)

r = c.get(f"/shop/?category={cat.id}&price=under_20")
check("Combined filters", b"Bamboo Toothbrush" in r.content and b"Glass Food Container" not in r.content)

r = c.get("/shop/?category=999")
check("Bad category id handled (no crash)", r.status_code == 200 and b"No products found" in r.content)


print()
print("=" * 60)
print("3. AUTH FLOW")
print("=" * 60)

r = c.post("/signup/", {"username": "tester", "email": "tester@example.com",
                        "password": "TestPass!2026", "password2": "TestPass!2026"}, follow=True)
check("Signup works", User.objects.filter(username="tester").exists())

r = c.post("/login/", {"username": "tester", "password": "TestPass!2026"}, follow=True)
check("Login works", b"logout" in r.content.lower() or b"tester" in r.content.lower())

r = c.get("/cart/", follow=True)
check("Cart page 200 when logged in", r.status_code == 200)

print()
print("=" * 60)
print("4. CART FLOW")
print("=" * 60)

p1 = Product.objects.get(name="Bamboo Toothbrush")
p2 = Product.objects.get(name="Compost Bin")

r = c.post(f"/add-to-cart/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
data = r.json()
check("Add to cart returns JSON success", data.get("success") is True, str(data))
check("Cart count = 1", data.get("cart_count") == 1, str(data))

c.post(f"/add-to-cart/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
cart = Cart.objects.get(user=User.objects.get(username="tester"))
check("Second add increments qty to 2", cart.items.first().quantity == 2, f"qty={cart.items.first().quantity}")

r = c.post(f"/add-to-cart/{p2.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
data = r.json()
check("Add second product, total qty = 3", data.get("cart_count") == 3, str(data))

r = c.get("/")
badge_live = re.search(rb'id="cart-badge".{0,500}?>\s*3\s*<', r.content, re.S)
check("Navbar cart badge shows live count (3)", b'id="cart-badge"' in r.content and badge_live is not None)

r = c.post("/update-cart/", {"item_id": cart.items.get(product=p1).id, "quantity": 5},
           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
data = r.json()
check("Update quantity works", data.get("success") is True)
cart.refresh_from_db()
check("Qty is now 5", cart.items.get(product=p1).quantity == 5)

r = c.post("/remove-from-cart/", {"item_id": cart.items.get(product=p1).id},
           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
data = r.json()
cart.refresh_from_db()
check("Remove works", not cart.items.filter(product=p1).exists())

r = c.get("/cart/")
check("Cart page shows item", b"Compost Bin" in r.content)

print()
print("=" * 60)
print("5. CHECKOUT & ORDER")
print("=" * 60)

stock_before = p2.stock
r = c.get("/checkout/")
check("Checkout 200", r.status_code == 200)

r = c.post("/place-order/", {"first_name": "Test", "last_name": "User", "email": "t@e.com",
                             "phone": "1234567890", "address": "1 Green St", "city": "Eco City",
                             "state": "Eco State", "pincode": "123456", "payment_method": "cod"}, follow=True)
order = Order.objects.filter(user=User.objects.get(username="tester")).first()
check("Order created", order is not None)
if order:
    check("Order total correct (49.99)", str(order.total) == "49.99", f"total={order.total}")
    check("Order id generated (ORD...)", order.order_id.startswith("ORD"), f"order_id={order.order_id}")
    check("Order has billing details", order.first_name == "Test" and order.city == "Eco City")
    check("Order has 1 item", order.items.count() == 1)
p2.refresh_from_db()
check("Stock decremented", p2.stock == stock_before - 1, f"{stock_before} -> {p2.stock}")
cart.refresh_from_db()
check("Cart cleared after order", cart.items.count() == 0)

# Order tracking / invoice pages
if order:
    r = c.get(f"/order-tracking/{order.order_id}/")
    check("Order tracking page 200 + shows id", r.status_code == 200 and order.order_id.encode() in r.content)
    r = c.get(f"/invoice/{order.order_id}/")
    check("Invoice page 200", r.status_code == 200)
r = c.get("/order-success/999/")
check("Bad order id -> 404 (logged in)", r.status_code == 404)

r = c.get("/cart/")
check("Empty cart page renders", r.status_code == 200)

# New account pages (logged in)
r = c.get("/profile/")
check("Profile page 200", r.status_code == 200)
r = c.get("/password_change/")
check("Password change page 200", r.status_code == 200)
for url in ["/help-center/", "/shipping-delivery/", "/returns-refunds/", "/privacy-policy/", "/terms-conditions/"]:
    r = c.get(url)
    check(f"Page {url} 200", r.status_code == 200, f"status={r.status_code}")

print()
print("=" * 60)
print("6. CONTACT & SUBSCRIPTION")
print("=" * 60)

c.post("/contact/", {"name": "A", "email": "a@e.com", "subject": "Hi", "message": "Hello"}, follow=True)
check("Contact message saved", ContactMessage.objects.filter(email="a@e.com").exists())

c.post("/subscription/", {"email": "sub@e.com"}, follow=True)
check("Subscription saved", Subscription.objects.filter(email="sub@e.com").exists())

print()
print("=" * 60)
print("7. LOGOUT & PROTECTED ROUTES")
print("=" * 60)

r = c.post("/logout/", follow=True)
check("Logout works (POST)", r.status_code == 200)

r = c.get("/checkout/", follow=True)
check("Checkout redirects to login when anonymous", "/login/" in r.request.get("PATH_INFO", ""))

r = c.post("/add-to-cart/1/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
data = r.json()
check("Anonymous add-to-cart returns JSON 401", r.status_code == 401 and data.get("success") is False)

r = c.get("/", follow=True)
check("No cart badge for anonymous users", b'id="cart-badge"' not in r.content)

r = c.get("/order-success/1/")
check("Order success redirects to login when anonymous", r.status_code == 302 and "/login/" in r.url)

print()
print("=" * 60)
print("8. DATA INTEGRITY")
print("=" * 60)

check("Categories count = 7", Category.objects.count() == 7, f"n={Category.objects.count()}")
check("Products >= 15", Product.objects.count() >= 15, f"n={Product.objects.count()}")
check("All products have images", Product.objects.filter(image="").count() == 0)
check("All products have stock", Product.objects.filter(stock=0).count() == 0)
check("All products have price", not Product.objects.filter(price__lte=0).exists())
for cat in Category.objects.all():
    if cat.products.count() == 0:
        check(f"Category '{cat.name}' has products", False)
broken_imgs = [p for p in Product.objects.all() if not p.image.storage.exists(p.image.name)]
check("All product image files exist on disk", len(broken_imgs) == 0, str([p.image.name for p in broken_imgs]))

print()
print("=" * 60)
print(f"RESULTS: {passed} passed, {len(failed)} failed")
if failed:
    print("FAILED:", *failed, sep="\n  - ")
else:
    print("ALL TESTS PASSED - PROJECT IS FULLY FUNCTIONAL")
print("=" * 60)

runner.teardown_databases(old_config)

