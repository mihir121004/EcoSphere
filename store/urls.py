from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import shop
from store.views import Cart
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='home'),
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
    path('help/', views.help, name='help'),
    path('subscription/', views.subscription, name='subscription'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)