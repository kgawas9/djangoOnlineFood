"""foodOnline_main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# for media file set up
# ----------------------------
from django.conf import settings
from django.conf.urls.static import static
# ----------------------------

from . import views
from marketplace import views as marketplace_views
from accounts.decorators import is_admin_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),      # home page url

    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('cart/', marketplace_views.cart, name='cart'),

    # search
    path('search/', marketplace_views.search, name='search'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
