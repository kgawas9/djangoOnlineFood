from .models import Cart
from menu.models import FoodItem

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user = request.user)
            if cart_items:
                for item in cart_items:
                    cart_count += item.quantity
            
        except:
            cart_count = 0
            
    return dict(cart_count = cart_count)
