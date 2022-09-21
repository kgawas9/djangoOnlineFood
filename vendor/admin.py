from django.contrib import admin
from .models import Vendor

# Register your models here.
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'vendor_name', 'created_at', 'is_approved'
    ]

    list_display_links = [
        'user', 'vendor_name'
    ]

