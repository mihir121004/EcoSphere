from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Subscription
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .models import Product, Cart, CartItem
from django.http import JsonResponse



# Create your views here.
def homepage(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:4]
    context = {
        "featured_products": featured_products
    }
    
    return render(request, "store/homepage.html",{
        "featured_products": featured_products
    })
def shop(request):
    print("CATEGORY PARAM:", request.GET.get('category')
          )
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
        
    products = Product.objects.filter(is_available=True)

    context = {
        'categories' : categories,
        'products' : products
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
    
        return redirect('shop')        
        
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