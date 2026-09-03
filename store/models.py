from django.db import models
from django.contrib.auth.models import User


# =========================
# Category Model
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# =========================
# Product Model
# =========================
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    image_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=True)

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


# =========================
# Subscription Model
# =========================
class Subscription(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# =========================
# Contact Messages
# =========================
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)

    email = models.EmailField()

    subject = models.CharField(max_length=200)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# Cart
# =========================
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"{self.user.username}'s Cart"


# =========================
# Cart Item
# =========================
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


# =========================
# Wishlist
# =========================
class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# =========================
# Order
# =========================
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_id = models.CharField(max_length=20, unique=True, blank=True)

    # Billing / shipping details captured at checkout
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='cod'
    )
    payment_status = models.CharField(max_length=20, default='pending')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate a human-friendly order id (ORD000001) once
        if not self.order_id:
            self.order_id = f"ORD{self.pk:06d}" if self.pk else f"ORD{Order.objects.count() + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id}"


# =========================
# Order Item
# =========================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"