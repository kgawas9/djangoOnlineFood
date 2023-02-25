from django.contrib import admin

from .models import Payment, Order, OrderedFood

# Register your models here.

class OrderFoodOnline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'quantity', 'user', 'fooditem', 'price', 'amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'is_ordered'
    ]
    inlines = [OrderFoodOnline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
