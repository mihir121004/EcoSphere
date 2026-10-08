from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import shop
from store.views import Cart
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('', views.homepage, name='home'),
    path('health/', views.health_check, name='health_check'),
    path('shop/', views.shop, name='shop'),
    path('about/', views.about, name='about'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path("remove-from-cart/", views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-tracking/<str:order_id>/', views.order_tracking, name='order_tracking'),
    path('invoice/<str:order_id>/', views.invoice, name='invoice'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('help/', views.help, name='help'),
    path('help-center/', views.help_center, name='help_center'),
    path('shipping-delivery/', views.shipping_delivery, name='shipping_delivery'),
    path('returns-refunds/', views.returns_refunds, name='returns_refunds'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('subscription/', views.subscription, name='subscription'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='store/password_change.html', success_url='/profile/'), name='password_change'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)