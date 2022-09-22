from django.urls import path
from . import views

urlpatterns = [
    path('register-user/', views.register_user, name='register_user'),
    path('register-vendor/', views.register_vendor, name='register_vendor'),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('my-account/', views.my_account, name='my_account'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),


    # email verification
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]
