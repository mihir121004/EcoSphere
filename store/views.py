from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Subscription, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .models import Product, Cart, CartItem
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods



# Create your views here.
def homepage(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:4]
    context = {
        "featured_products": featured_products
    }
    
    return render(request, "store/homepage.html",{
        "featured_products": featured_products
    })


@require_http_methods(["GET"])
def health_check(request):
    """
    Lightweight health-check endpoint for uptime monitoring (e.g., UptimeRobot).
    Returns 200 OK with minimal JSON. No auth, no DB queries, no sensitive data.
    """
    return JsonResponse({"status": "ok"})


def shop(request):
    category_id = request.GET.get('category')
    price_range = request.GET.get('price_range')
    categories = Category.objects.all()

    # Start with all available products
    products = Product.objects.filter(is_available=True)

    # Filter by category if provided
    if category_id:
        products = products.filter(category_id=category_id)

    # Filter by price range if provided
    if price_range:
        if price_range == 'under_500':
            products = products.filter(price__lt=500)
        elif price_range == '500_1000':
            products = products.filter(price__gte=500, price__lt=1000)
        elif price_range == 'above_1000':
            products = products.filter(price__gte=1000)

    context = {
        'categories': categories,
        'products': products,
        'current_category': category_id,
        'current_price_range': price_range
    }

    return render(request, 'store/shop.html', context)

def categories(request):
    categories = Category.objects.all()
    return render(request, 'store/categories.html', {'categories': categories})

def about(request):
    return render(request, 'store/about.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        print("AUTH USER:" , user)

        if user:
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "store/login.html")

#logout view
def logout_user(request):
    logout(request)
    return redirect("login")

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

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
            messages.error(request, "Email already exists")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'store/signup.html')


@login_required(login_url='login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total =sum(item.subtotal() for item in items)

    return render(request, "store/cart.html", {
        "cart_items": items,
        "total": total
    })
    
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({"success": True})
        
@login_required
def update_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")

        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success":True})
    return JsonResponse({"success": False})
        

def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "auth": False}, status=401)

    if request.method == "POST":
        item_id = request.POST.get("item_id")

        CartItem.objects.filter(
            id=item_id,
            cart__user=request.user
        ).delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


def checkout(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)

    total = 0
    # Add total_price field for each item
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # calculate price × quantity
        total += item.total_price

    context ={
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "store/checkout.html", context)

@login_required
def place_order(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        payment_method = request.POST.get('payment_method')

        # Get cart items
        cart_items = CartItem.objects.filter(cart__user=request.user)
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        # Calculate total
        total = sum(item.subtotal() for item in cart_items)

        # Create order
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

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear cart
        cart_items.delete()

        # Handle payment
        if payment_method in ['upi', 'card']:
            # Demo payment flow
            order.payment_status = 'SUCCESS'
            order.status = 'confirmed'
            order.save()
            messages.success(request, "Payment Successful (Demo)! Order placed.")
            return redirect('order_tracking', order_id=order.order_id)
        else:
            # COD
            messages.success(request, "Order placed successfully!")
            return redirect('order_tracking', order_id=order.order_id)

    return redirect("checkout")

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name = request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )
        
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "store/contact.html")
    

def help(request):
    return render(request, 'store/help.html')

def forgot_password(request):
    return render(request, 'store/forgot-password.html')

def subscription(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Email is required")
            return redirect("home")

        # Save subscription
        subscription, created = Subscription.objects.get_or_create(email=email)

        # 🔔 SEND ADMIN NOTIFICATION (ONLY ON NEW SUBSCRIPTION)
        if created:
            send_mail(
                subject="New Subscription",
                message=f"A new user has subscribed: {email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["admin@example.com"],
                fail_silently=True,
            )

        messages.success(request, "Subscribed successfully!")

    return redirect("home")


@login_required
def order_tracking(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, "store/order_tracking.html", {
            "order": order,
            "order_items": order_items,
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")


@login_required
def invoice(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, "store/invoice.html", {
            "order": order,
            "order_items": order_items,
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")

@login_required
def profile(request):
    # Fetch current orders (not delivered)
    current_orders = Order.objects.filter(
        user=request.user
    ).exclude(status='delivered').order_by('-created_at')

    # Fetch previous orders (delivered)
    previous_orders = Order.objects.filter(
        user=request.user,
        status='delivered'
    ).order_by('-updated_at')

    context = {
        'current_orders': current_orders,
        'previous_orders': previous_orders,
    }

    return render(request, 'store/profile.html', context)

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
