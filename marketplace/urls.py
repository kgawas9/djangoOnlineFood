from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_details, name='vendor_detail'),

    # cart
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease-item-from-cart/<int:food_id>/', views.decrease_item_from_cart, name='decrease_item_from_cart'),

    # cart details
    path('delete_cart/<int:cart_id>/', views.delete_cart, name = 'delete_cart'),
]
