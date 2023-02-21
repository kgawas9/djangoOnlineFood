from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q

from datetime import date, datetime

from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amount


# distance calculation
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # 'D is shortcut for distance
from django.contrib.gis.db.models.functions import Distance

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

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')

    todays_date = date.today()
    today = todays_date.isoweekday()
    current_opening_hour = OpeningHour.objects.filter(vendor = vendor, day=today)

    current_time = datetime.now().strftime("%H:%M:%S")
    
    is_open = False
    for cur_op_hr in current_opening_hour:
        start_time = str(datetime.strptime(cur_op_hr.from_hour, "%I:%M %p").time())
        end_time = str(datetime.strptime(cur_op_hr.to_hour, "%I:%M %p").time())

        if current_time > start_time and current_time < end_time:
            is_open = True
            break
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'category_details': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hour': current_opening_hour,
        'is_open': is_open,
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
                        'cart_amount': get_cart_amount(request),
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
                        'cart_amount': get_cart_amount(request),
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
                        'cart_amount': get_cart_amount(request),
                    })

                except:
                    return JsonResponse({
                        'status':'failed',
                        'message':f'{food_item} does not exist in cart',
                        'cart_counter': get_cart_counter(request),
                        'cart_amount': get_cart_amount(request),
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


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user = request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
        'cart_amount': get_cart_amount(request),
    }
    return render(request, 'marketplace/cart.html', context=context)


# ===============================================
# another approach to delete the cart item based on food_item id
# @login_required(login_url='login')
# def delete_cart_item(request, food_id):
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             try:
#                 food_item = FoodItem.objects.get(id=food_id)
#                 try:
#                     cart_item = Cart.objects.get(food_item=food_item, user=request.user)

#                     return JsonResponse({
#                         'status': 'Success',
#                         'message': f'{ cart_item.food_item } successfully deleted from cart',    
#                     })
#                 except:
#                     return JsonResponse({
#                     'status': 'Failed',
#                     'message': 'food item does not found in cart',
#                 })    
#             except:
#                 return JsonResponse({
#                     'status': 'Failed',
#                     'message': 'food item does not exist',
#                 })
#         else:
#             return JsonResponse({
#                     'status': 'Failed',
#                     'message': 'Invalid request',
#                 })
# end another approach to delete the cart item based on food_item id

@login_required(login_url='login')
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        # check for ajax request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user = request.user, id = cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'success',
                        'message': f'{ cart_item.food_item.food_title } successfully deleted',
                        'cart_counter': get_cart_counter(request),
                        'qty': cart_item.quantity,
                        'cart_amount': get_cart_amount(request),
                    })

            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'This item does not exist in cart',
                })
        else:
            return JsonResponse({
                    'status': 'Failed',
                    'message': 'Invalid request',
                })



def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    
    address = request.GET['address']
    keyword = request.GET['keyword']
    latitude = request.GET['lat']
    longitude = request.GET['lng']
    radius = request.GET['radius']

    print(address, keyword, latitude, longitude, radius)

    # Get vendor ids that has the food item which user is looking for

    fetch_vendors_by_food_items = FoodItem.objects.filter(food_title__icontains = keyword, is_available = True).values_list('vendor', flat=True)
    
    vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | Q(vendor_name__icontains = keyword, is_approved = True, user__is_active =True))

    if latitude and longitude and radius:
        pnt = GEOSGeometry('POINT(%s %s)' %(longitude, latitude))

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | Q(vendor_name__icontains = keyword, is_approved = True, user__is_active =True), 
                                            user_profile__location__distance_lte=(pnt, D(km=radius))
                                            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
            v.kms = round(v.distance.km,2)

    vendor_count = vendors.count()
    
    context = {
        'vendor_list': vendors,
        'vendor_count': vendor_count,
        'source_location': address,
    }

    return render(request, 'marketplace/listing.html', context= context)

