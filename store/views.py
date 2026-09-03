from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Subscription, ContactMessage, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Count, Q, Sum


# ======================
# Homepage
# ======================
def homepage(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:4]
    return render(request, "store/homepage.html", {"featured_products": featured_products})


# ======================
# Shop with category & price filters
# ======================
def shop(request):
    category_id = request.GET.get('category')
    price_filter = request.GET.get('price')
    categories = Category.objects.all()

    products = Product.objects.filter(is_available=True)

    if category_id:
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            category_id = None

    if price_filter == 'under_20':
        products = products.filter(price__lt=20)
    elif price_filter == '20_to_50':
        products = products.filter(price__gte=20, price__lte=50)
    elif price_filter == '50_to_100':
        products = products.filter(price__gte=50, price__lte=100)
    elif price_filter == 'above_100':
        products = products.filter(price__gt=100)

    return render(request, 'store/shop.html', {
        'categories': categories,
        'products': products,
        'selected_category': category_id,
        'selected_price': price_filter,
    })


# ======================
# Categories
# ======================
def categories(request):
    # Emoji icons matched to category names (fallback icon for new categories)
    icon_map = {
        'Personal Care': '🧴',
        'Kitchen & Dining': '🍽',
        'Home & Living': '🏡',
        'Clothing & Accessories': '👕',
        'Office Supplies': '📒',
        'Outdoor & Sports': '🏕',
        'Cleaning Products': '🧽',
    }

    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    ).order_by('name')

    for category in categories:
        category.icon = icon_map.get(category.name, '♻')

    return render(request, 'store/categories.html', {'categories': categories})


# ======================
# About
# ======================
def about(request):
    return render(request, 'store/about.html')


# ======================
# Login
# ======================
def login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password")
        return redirect("login")
    return render(request, "store/login.html")


# ======================
# Forgot Password
# ======================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        # Always show the same message for security
        messages.info(request, "If that email exists, a password reset link has been sent to it.")
        return redirect("login")
    return render(request, "store/forgot-password.html")


# ======================
# Signup
# ======================
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not all([username, email, password, password2]):
            messages.error(request, "All fields are required")
            return redirect('signup')

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('signup')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created! Please login to continue.")
        return redirect('login')

    return render(request, 'store/signup.html')
# ======================
# Cart View
# ======================
@login_required(login_url='login')
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.subtotal() for item in items)

    return render(request, "store/cart.html", {
        "cart_items": items,
        "total": total,
    })


# ======================
# Add to Cart (AJAX)
# ======================
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "auth": False}, status=401)

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        # Block adding if completely out of stock
        if product.stock == 0:
            return JsonResponse({"success": False, "error": "Out of stock"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)


        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )
        if not created:
            # Cap quantity at available stock
            if cart_item.product.stock == 0 or cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({"success": False, "error": "Out of stock"}, status=400)

        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        return JsonResponse({"success": True, "cart_count": cart_count})
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)


# ======================
# Update Cart (AJAX)
# ======================
@login_required
def update_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")

        try:
            qty = int(quantity)
            if qty < 1:
                qty = 1

            cart_item = CartItem.objects.select_related("product").get(id=item_id, cart__user=request.user)

            # Cap quantity at available stock
            if cart_item.product.stock > 0 and qty > cart_item.product.stock:
                qty = cart_item.product.stock

            cart_item.quantity = qty
            cart_item.save()
            return JsonResponse({"success": True})
        except (CartItem. DoesNotExist, ValueError, TypeError):
            return JsonResponse({"success": False, "error": "Invalid item"}, status=400)
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)


# ======================
# Remove from Cart (AJAX)
# ======================
def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "auth": False}, status=401)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        deleted, _ = CartItem.objects.filter(
            id=item_id,
            cart__user=request.user
        ).delete()
        if deleted:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)
# ======================
# Checkout
# ======================
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        messages.info(request, "Your cart is empty. Add some products first.")
        return redirect("cart")

    total = sum(item.subtotal() for item in cart_items)

    for item in cart_items:

        item.total_price = item.product.price * item.quantity

    context = {
        "cart_items": cart_items,

        "total": total,
    }
    return render(request, "store/checkout.html", context)


# ======================
# Place Order
# ======================
@login_required
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    payment_method = request.POST.get('payment_method', 'cod')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    total = sum(item.subtotal() for item in cart.items.all())

    order = Order.objects.create(
        user=request.user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        payment_method=payment_method,
        total=total,
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

        # Decrement stock
        product = item.product
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()
        else:
            product.is_available = False
            product.save()

    cart.items.all().delete()

    # Demo payment flow: UPI/card are "paid" instantly, COD stays pending
    if payment_method in ('upi', 'card'):
        order.payment_status = 'SUCCESS'
        order.status = 'confirmed'
        order.save()
        messages.success(request, "Payment successful (demo)! Order placed.")
    else:
        messages.success(request, "Order placed successfully!")

    return redirect('order_tracking', order_id=order.order_id)


# ======================
# Order Success
# ======================
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)


    return render(request, "store/order_success.html", {"order": order})


# ======================
# Order Tracking
# ======================
@login_required
def order_tracking(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")

    return render(request, "store/order_tracking.html", {
        "order": order,
        "order_items": order.items.all(),
    })


# ======================
# Invoice
# ======================
@login_required
def invoice(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")

    return render(request, "store/invoice.html", {
        "order": order,
        "order_items": order.items.all(),
    })


# ======================
# Profile
# ======================
@login_required
def profile(request):
    current_orders = Order.objects.filter(
        user=request.user
    ).exclude(status='delivered').order_by('-created_at')

    previous_orders = Order.objects.filter(
        user=request.user,
        status='delivered'
    ).order_by('-updated_at')

    return render(request, 'store/profile.html', {
        'current_orders': current_orders,
        'previous_orders': previous_orders,
    })


# ======================
# Info / legal pages
# ======================
def help_center(request):
    return render(request, 'store/help_center.html')


def shipping_delivery(request):
    return render(request, 'store/shipping_delivery.html')


def returns_refunds(request):
    return render(request, 'store/returns_refunds.html')


def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')


def terms_conditions(request):
    return render(request, 'store/terms_conditions.html')
# ======================
# Contact
# ======================
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            messages.success(request, "Your message has been sent successfully!")
        else:
            messages.error(request, "Please fill in your name, email,and message.")

        return redirect("contact")

    return render(request, "store/contact.html")


# ======================
# Help
# ======================
def help(request):
    return render(request, 'store/help.html')


# ======================
# Newsletter Subscription
# ======================
def subscription(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Email is required")
            return redirect("home")

        subscription, created = Subscription.objects.get_or_create(email=email)


        # Send admin notification (only on new subscription)
        if created:

            send_mail(
                subject="New EcoSphere Subscription",
                message=f"A new user has subscribed: {email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )

        messages.success(request, "Subscribed successfully! Thank you for joining.")

    return redirect("home")
