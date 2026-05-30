from django.contrib import admin
from .models import Category, Product, Subscription 
from django.db import models                 
from .models import ContactMessage

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Subscription)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at')
    search_fields = ('name', 'email', 'subject')
    ordering  = ('-created_at',)
   