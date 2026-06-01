from django.contrib import admin
from django.db import models
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
import csv
from .models import (
    Category,
    Product,
    Subscription,
    ContactMessage,
    Cart,
    CartItem,
    Order,
    OrderItem
)

# ---------------------------
# CATEGORY
# ---------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# ---------------------------
# PRODUCT
# ---------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "category",
        "is_available",
        "is_featured",
        "image_preview",
    )
    list_filter = ("is_available", "is_featured", "category")
    search_fields = ("name", "category__name")
    list_editable = ("price", "is_available", "is_featured")
    ordering = ("-id",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image"

    actions = ['make_featured', 'make_unfeatured', 'make_available', 'make_unavailable']

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} products marked as featured.")
    make_featured.short_description = "Mark selected products as featured"

    def make_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} products unmarked as featured.")
    make_unfeatured.short_description = "Unmark selected products as featured"

    def make_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, f"{queryset.count()} products marked as available.")
    make_available.short_description = "Mark selected products as available"

    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f"{queryset.count()} products marked as unavailable.")
    make_unavailable.short_description = "Mark selected products as unavailable"








# ---------------------------
# CART ITEM INLINE
# ---------------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "get_total")
    can_delete = False

    def get_total(self, obj):
        return obj.product.price * obj.quantity

    get_total.short_description = "Total Price"


# ---------------------------
# CART (READ-ONLY)
# ---------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    readonly_fields = ("user", "created_at")
    inlines = [CartItemInline]

    def has_add_permission(self, request):
        return False


# ---------------------------
# ORDER ITEM INLINE
# ---------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total")
    can_delete = False

    def get_total(self, obj):
        price = obj.price if obj.price is not None else 0
        quantity = obj.quantity if obj.quantity is not None else 0
        return price * quantity

    get_total.short_description = "Total"


# ---------------------------
# ORDER
# ---------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "total",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
        "get_items_count",
    )

    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order_id",
        "user__username",
        "user__email",
    )

    ordering = ("-created_at",)

    inlines = [OrderItemInline]

    readonly_fields = (
        "user",
        "total",
        "payment_method",
        "payment_status",
        "created_at",
        "get_items_count",
    )

    fieldsets = (
        ("Customer Info", {
            "fields": ("user",)
        }),
        ("Payment Details", {
            "fields": ("payment_method", "payment_status", "total")
        }),
        ("Order Status", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )

    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'export_orders_csv']

    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = "Items"

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} orders marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'User', 'Email', 'Total', 'Payment Method', 'Payment Status', 'Order Status', 'Created At'])

        for order in queryset:
            writer.writerow([
                order.order_id,
                order.user.username,
                order.user.email,
                order.total,
                order.payment_method,
                order.payment_status,
                order.status,
                order.created_at,
            ])

        return response
    export_orders_csv.short_description = "Export selected orders to CSV"

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------
# DASHBOARD STATISTICS
# ---------------------------
class DashboardAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(payment_status='completed').aggregate(Sum('total'))['total__sum'] or 0
        total_products = Product.objects.count()
        total_users = Cart.objects.count()  # Approximate user count
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='delivered').count()

        extra_context.update({
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_products': total_products,
            'total_users': total_users,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
        })

        return super().changelist_view(request, extra_context)


# ---------------------------
# CONTACT MESSAGE ACTIONS
# ---------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "subject")
    ordering = ("-created_at",)
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    actions = ['mark_as_read', 'mark_as_unread', 'export_messages_csv']

    def is_read(self, obj):
        return getattr(obj, '_is_read', False)
    is_read.boolean = True
    is_read.short_description = "Read"

    def mark_as_read(self, request, queryset):
        queryset.update(_is_read=True)
        self.message_user(request, f"{queryset.count()} messages marked as read.")
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(_is_read=False)
        self.message_user(request, f"{queryset.count()} messages marked as unread.")
    mark_as_unread.short_description = "Mark selected messages as unread"

    def export_messages_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Subject', 'Message', 'Created At'])

        for message in queryset:
            writer.writerow([
                message.name,
                message.email,
                message.subject,
                message.message,
                message.created_at,
            ])

        return response
    export_messages_csv.short_description = "Export selected messages to CSV"


# ---------------------------
# SUBSCRIPTION ACTIONS
# ---------------------------
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "is_active")
    search_fields = ("email",)
    ordering = ("-created_at",)
    actions = ['export_subscriptions_csv']

    def is_active(self, obj):
        return True  # All subscriptions are active unless unsubscribed
    is_active.boolean = True
    is_active.short_description = "Active"

    def export_subscriptions_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Email', 'Subscribed At'])

        for subscription in queryset:
            writer.writerow([
                subscription.email,
                subscription.created_at,
            ])

        return response
    export_subscriptions_csv.short_description = "Export selected subscriptions to CSV"


# ---------------------------
# CUSTOM ADMIN SITE
# ---------------------------
class EcoSphereAdminSite(admin.AdminSite):
    site_header = "EcoSphere Administration"
    site_title = "EcoSphere Admin Portal"
    index_title = "Welcome to EcoSphere Admin Dashboard"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        # Add custom statistics to the index page
        if request.path == '/admin/':
            # Calculate statistics
            stats = {
                'total_orders': Order.objects.count(),
                'total_revenue': Order.objects.filter(payment_status='completed').aggregate(Sum('total'))['total__sum'] or 0,
                'total_products': Product.objects.count(),
                'total_users': Cart.objects.count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
                'recent_orders': Order.objects.order_by('-created_at')[:5],
            }

            # Add stats to context
            for app in app_list:
                if app['app_label'] == 'store':
                    app['stats'] = stats
                    break

        return app_list

# Create custom admin site
admin_site = EcoSphereAdminSite(name='ecosphere_admin')

# Re-register all models with the custom admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(ContactMessage, ContactMessageAdmin)
admin_site.register(Cart, CartAdmin)
admin_site.register(Order, OrderAdmin)

# ---------------------------
# USER PROFILE
# ---------------------------
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ("user", "phone", "city", "created_at")
#     search_fields = ("user__username", "phone", "city")
#     ordering = ("-created_at",)
