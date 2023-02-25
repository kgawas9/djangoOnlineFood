from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount

from .forms import OrderForm
from .models import Order
from .utils import generate_order_number

import simplejson as json

# Create your views here.
@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user = request.user).order_by('created_at')
    # if not cart items send it to marketplace
    if cart_items.count() <= 0:
        return redirect('marketplace')
    
    # get this values from context processor
    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['total']
    tax_data = get_cart_amount(request)['tax_dict']

    # print(json.dumps(tax_data))
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']

            order.user = request.user

            # order details
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax

            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            return redirect('place_order')
        else:
            print(form.errors)


    return render(request, 'orders/place_order.html')