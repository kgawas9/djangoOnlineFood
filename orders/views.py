from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount

from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number

from accounts.utils import send_notification

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
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context=context)
        else:
            print(form.errors)

    # context = {
    #             'order': None,
    #             'cart_items': cart_items,
    #         }
    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def order_payments(request):
    # check if the request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment detail in  payment table (database)
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        # ============================================================
        # if value does not found in post it will return key error with below approach, however
        # it does works the same
        # status = request.POST['status']   
        # ============================================================

        # update payment
        order = Order.objects.get(user=request.user, order_number = order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status.lower()
        )

        payment.save()

        # update order model
        
        order.Payment = payment
        order.is_ordered = True
        order.save()

        # move the cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:    
            ordered_food = OrderedFood(
                order = order,
                payment = payment,
                user = request.user,
                fooditem = item.food_item,

                quantity = item.quantity,
                price = item.food_item.price,
                amount = item.food_item.price * item.quantity,        # to calculate total amount
            )

            ordered_food.save()

        # send order confirmation email to customer
        mail_subject = 'Order confirmed - ' 
        mail_template = 'orders/emails/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }

        send_notification(mail_subject, mail_template, context)
        return HttpResponse('Data saved and email sent')
        # send order received email to vendor

        # clear the cart if payment is success

        # return back to ajax with the status success or failure
    return HttpResponse("payments view")