from django.contrib import admin
from .models import Category, FoodItem


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('category_name',)
    }

    list_display = (
        'category_name', 'vendor', 'updated_at'
    )

    search_fields=(
        'category_name', 'vendor__vendor_name'
    )

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields= {
        'slug':('food_title',)
    }

    list_display = (
        'food_title', 'category', 'vendor', 'price', 'updated_at', 'is_available'
    )

    list_editable = (
        'is_available',
    )

    search_fields = (
        'food_title', 'category__category_name', 'vendor__vendor_name', 'price',
    )

    list_filter = [
        'is_available'
    ]

