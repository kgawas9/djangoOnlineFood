from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.defaultfilters import slugify

# custom models
from .models import User, UserProfile
from .forms import UserForm
from vendor.forms import VendorForm
from .utils import detectUser, send_verification_email
from .decorators import is_role_vendor, is_role_customer, is_admin_user
from vendor.models import Vendor


# Create your views here.
def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in..")
        return redirect('my_account')

    if request.method == 'POST':
        form = UserForm(request.POST)
        
        if form.is_valid():
            # create user using form
            # ----------------------------------------------------------
            
            # password = form.cleaned_data['password']

            # user = form.save(commit = False)
            # user.set_password(password)
            # user.role = User.CUSTOMER

            # user.save()
            
            # ----------------------------------------------------------
            
            # another way using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )

            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            email_subject = 'Confirm E-mail Address'
            email_template = 'accounts/emails/account_verification_email.html'
            
            send_verification_email(request, user, email_subject, email_template)

            messages.success(request, "Your account has been registered successfully, the verification link has sent to your registered email id. please activate your account")
            return redirect('register_user')

    else:
        form = UserForm()
    
    context = {
        'form' : form
    }
    return render(request, 'accounts/registerUser.html', context = context)


def register_vendor(request):
    if request.user.is_authenticated:
        # if request.user.role == 'vendor':
        messages.warning(request, "You are already logged in..")
        return redirect('my_account')
        # else:
        #     logout(request)
        #     return redirect('register_vendor')

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        # To receive the file
        vendor_form = VendorForm(request.POST, request.FILES)

        if user_form.is_valid() and vendor_form.is_valid():
            vendor_name = vendor_form.cleaned_data['vendor_name']
            user = user_form.save(commit=False)
            
            # password = user_form.cleaned_data['password']
            # print(password)
            
            user.set_password(user_form.cleaned_data['password'])
            user.role = User.VENDOR
            user.save()

            # to allocate user and user_profile need to make commit = false
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user = user)
            vendor.user_profile = user_profile
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)
            vendor.save()

            # Send verification email
            email_subject = 'Confirm E-mail Address'
            email_template = 'accounts/emails/account_verification_email.html'
            
            send_verification_email(request, user, email_subject, email_template)

            messages.success(request, "Your account has been registered successfully, please wait for the approval..")
            return redirect('register_vendor')

    user_form = UserForm()
    vendor_form = VendorForm()

    context = {
        'u_form': user_form,
        'v_form': vendor_form,
    }
    return render(request, 'accounts/register_vendor.html', context=context)


def activate_account(request, uidb64, token):
    # to activaet the user by setting is_active to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations, your accounts is activated..")
        return redirect('my_account')

    messages.error(request, "Something went wrong, Invalid request..")
    return redirect('login')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in..")
        return redirect('my_account')

    if request.method == 'POST':
        email_id = request.POST['email']
        user_password = request.POST['password']

        if not email_id or not user_password:
            messages.error(request, 'Email id or password should not be blank..')
            return redirect('login')
        
        else:
            user = auth.authenticate(email=email_id, password = user_password)
            if user is None:
                messages.error(request, 'User not found, please verify your credentials')
                return redirect('login')

            auth.login(request, user)
            messages.success(request, f'Welcome { user.first_name }, you are now logged in..')
            return redirect('my_account')

    return render(request, 'accounts/login.html')



def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out, see you seen')
    return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if not email:
            messages.error(request, 'Please enter your email address to continue..')
            return redirect('forgot_password')

        if not User.objects.filter(email=email).exists():
            messages.error(request, f'User with email id {email} is not exist, please verify your email id..')
            return redirect('forgot_password')

        # send an email verification link to reset the password
        user = User.objects.get(email__exact=email)

        email_subject = 'Reset Your Password'
        email_template = 'accounts/emails/reset_password_email.html'
        send_verification_email(request, user, email_subject, email_template)

        messages.success(request, "Password reset link has been sent to your email address..")
        return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Password and confirm password does not matched..')
            return redirect('reset_password')
        
        # to get the user id from session
        user_id = request.session.get('uid')
        user = User.objects.get(pk=user_id)
        user.set_password(password)
        user.is_active = True
        user.save()
        messages.success(request, "Your password has reset successfully, you may login to your account now")
        return redirect('login')
        
    return render(request, 'accounts/reset_password.html')

def reset_password_validate(request, uidb64, token):
    # validate user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')

    messages.error(request, "Something went wrong, Invalid request..")
    return redirect('login')


# once the user will click on my account -
# 1. user will redirect to my_account view and then check if the user is customer or vendor from utils.py file
# 2. Then it will redirect to customer account url or vendor account url

@login_required(login_url='login')
def my_account(request):
    user = request.user
    redirect_url = detectUser(user)
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(is_role_customer)
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')


@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def vendor_dashboard(request):
    return render(request, 'accounts/vendor_dashboard.html')
