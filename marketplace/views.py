from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch


from vendor.models import Vendor
from menu.models import Category, FoodItem
from .models import Cart
from .context_processors import get_cart_counter

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

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'category_details': categories,
        'cart_items': cart_items,
    }

    return render(request, 'marketplace/vendor_detail.html', context=context)



def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        # below check condition is depricated after django 4.0 release
        # if request.is_ajax():
        # ------------------------------------------------------------
        # alternative condition for request.is_ajax() is 
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check for the item exist in vendor or not
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                # check if the user has already added same item in cart or not
                try:
                    check_cart = Cart.objects.get(user=request.user, food_item=fooditem)
                    
                    # increase cart quantity
                    # if check_cart:
                    check_cart.quantity += 1
                    check_cart.save()
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Increased the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                    })

                except:
                    check_cart = Cart.objects.create(
                        user = request.user,
                        food_item = fooditem,
                        quantity = 1,
                    )

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Added the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                    })

            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'This item does not exist',
            })    
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request',
            })

    else:
        return JsonResponse({'status': 'login_required',
                            'message': 'Please login to continue'})



def decrease_item_from_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                food_item = FoodItem.objects.get(id=food_id)
                
                try:
                    check_cart = Cart.objects.get(user = request.user, food_item = food_item)

                    if check_cart.quantity >= 1:
                        check_cart.quantity -= 1
                        check_cart.save()

                    if check_cart.quantity == 0:
                        check_cart.delete()

                    return JsonResponse({
                        'status':'success',
                        'message':'Requested food item decreased from cart',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                    })

                except:
                    return JsonResponse({
                        'status':'failed',
                        'message':f'{food_item} does not exist in cart',
                        'cart_counter': get_cart_counter(request),
                    })
            except:
                return JsonResponse({
                    'status':'failed',
                    'message':'Requested food item does not exist in cart'
                })

    else:    
        return JsonResponse({
            'status':'login_required',
            'message':'Please login to continue'
        })


def cart(request):
    cart_items = Cart.objects.filter(user = request.user)
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context=context)
    