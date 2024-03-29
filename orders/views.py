from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
        
        order.payment = payment
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
        mail_subject = 'Order confirmed - ' + str(order_number)
        mail_template = 'orders/emails/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }

        send_notification(mail_subject, mail_template, context)
        
        # send order received email to vendor
        mail_subject = 'New order received '
        mail_template = 'orders/emails/new_order_received.html'

        to_emails = []
        for item in cart_items:
            if item.food_item.vendor.user.email not in to_emails:
                to_emails.append(item.food_item.vendor.user.email)

        # ===================================================================
        # to send an individual emails with food item summary to vendor
        # ordered_food_items = OrderedFood.objects.filter(order=order)
        # for item in ordered_food_items:
        #     print(item)
        # ===================================================================

        context = {
            'order': order,
            'to_email': to_emails,
        }

        send_notification(mail_subject=mail_subject, mail_template=mail_template, context=context)
        
        # clear the cart if payment is success
        cart_items.delete()

        # return back to ajax with the status success or failure
        return JsonResponse({
            'order_number': order_number,
            'transaction_id': transaction_id,
            'message': 'success'
            })
    
    return HttpResponse("payments view")


@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number = order_number, payment__transaction_id =transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += item.price * item.quantity

        tax_data = json.loads(order.tax_data)
        # print(tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data
        }
        return render(request, 'orders/order_complete.html', context=context)

    except Exception as e:
        # print('in exception', str(e))
        return redirect('place_order')
        
    

# http://127.0.0.1:8000/orders/order-successful/?order_no=2023022619434165&trans_id=400567559E046321K