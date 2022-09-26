from django.urls import path, include
from . import views
from accounts import views as acc_view
urlpatterns = [
    path('', acc_view.my_account, name='v_account'),
    path('profile/', views.vendor_profile, name='v_profile'),
]
