from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from vendor.models import Vendor
from menu.models import Category, FoodItem
# Create your views here.

def marketplace(request):
    vendor = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendor.count()

    context = {
        'vendor_list': vendor,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listing.html', context=context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',        # related name
            queryset= FoodItem.objects.filter(is_available=True),
        )
    )
    
    context = {
        'vendor': vendor,
        'category_details': categories,
    }

    return render(request, 'marketplace/vendor_detail.html', context=context)