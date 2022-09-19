from django.contrib import admin
from .models import User, UserProfile

# to make the field read-only in admin panel
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # to make the field read-only in admin panel
    # ===================================
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    # ===================================

    list_display = [
        'email', 'first_name', 'last_name', 'username', 'role', 'created_date', 'modified_date', 'is_active'
    ]

    ordering = ('-date_joined',)
    

admin.site.register(UserProfile)