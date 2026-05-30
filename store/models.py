from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    image_name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    email = models.EmailField(unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    

class Cart(models.Model):
   user = models.OneToOneField(
       User,
       on_delete=models.CASCADE,
       related_name="cart"
   )
   created_at = models.DateTimeField(auto_now_add=True)
   
   def __str__(self):
       return f"{self.user.username}'s cart"
   

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    ) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"