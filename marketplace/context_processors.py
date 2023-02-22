from ast import Sub
from .models import Cart, Tax
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


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    total = 0
    tax_dict = {}

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user= request.user)

        if cart_items:
            for item in cart_items:
                food_item = FoodItem.objects.get(pk=item.food_item.id)
                subtotal += (food_item.price * item.quantity)

        get_tax = Tax.objects.filter(is_active = True)

        for tx in get_tax:
            tax_type = tx.tax_type
            tax_per = tx.tax_percentage
            tax_amt = round((tax_per * subtotal)/100, 2)

            # print(tax_type, tax_per, tax_amt)
            tax_dict.update({tax_type: {str(tax_per) : tax_amt}})

        # for key in tax_dict.values():
        #     for val in key.values():
        #         tax = tax + val
        
        # alternative way to calculate tax in single line
        tax = sum(val for key in tax_dict.values() for val in key.values())
        total = subtotal + tax

        # print(tax_dict)
        # check for how to pass tax_dict details
    return dict(subtotal=subtotal, tax=tax, total=total, tax_dict=tax_dict)

