from django.urls import path

from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.customer_dashboard, name='cust_dashboard'),
    path('profile/', views.cust_profile, name='cust_profile')
]