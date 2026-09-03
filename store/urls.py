from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve as media_serve
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('shop/', views.shop, name='shop'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('help/', views.help, name='help'),
    path('subscription/', views.subscription, name='subscription'),
]

# Serve uploaded media through Django in all environments.
# (django.conf.urls.static.static() returns [] when DEBUG=False, which would
# break product images on Render, so we route media explicitly here.)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': settings.MEDIA_ROOT}),
]
