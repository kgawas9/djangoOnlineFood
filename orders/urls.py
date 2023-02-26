from django.urls import path

from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.order_payments, name='payments'),
    path('order-successful/', views.order_complete, name='order_complete'),
]