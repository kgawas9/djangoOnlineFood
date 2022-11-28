from django.contrib import admin
from .models import Vendor, OpeningHour

# Register your models here.
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'vendor_name', 'vendor_license', 'is_approved'
    ]

    list_display_links = [
        'user', 'vendor_name'
    ]

    list_editable = [
        'is_approved'
    ]

    prepopulated_fields= {
        'vendor_slug':('vendor_name',)
    }


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display= [
        'vendor', 'day', 'from_hour', 'to_hour'
    ]

