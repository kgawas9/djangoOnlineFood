from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.my_account, name='account'),
    path('register-user/', views.register_user, name='register_user'),
    path('register-vendor/', views.register_vendor, name='register_vendor'),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('my-account/', views.my_account, name='my_account'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),


    # vendor
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/', include('vendor.urls')),

    # email verification
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),

    # customer urls
    path('customer_dashboard/', include('customers.urls')),
]
