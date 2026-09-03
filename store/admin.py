from django.contrib import admin
from .models import Category, Product, Subscription, ContactMessage, Cart, CartItem, Order, OrderItem, Wishlist


# Category
admin.site.register(Category)


# Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "stock", "is_available", "is_featured", "created_at")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "description")


# Subscription
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("email",)


# Contact Message
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "subject")
    ordering = ("-created_at",)


# Cart
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    inlines = [CartItemInline]


# CartItem
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    list_filter = ("cart",)


# Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "total", "payment_method", "payment_status", "status", "created_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_id", "user__username", "email")
    inlines = [OrderItemInline]


# OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")


# Wishlist
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
