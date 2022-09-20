from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
# custom models
from .models import User
from .forms import UserForm

# Create your views here.
def register_user(request):
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
            messages.success(request, "Your account has been registered successfully, the verification link has sent to your registered email id. please activate your account")
            return redirect('register_user')

    else:
        form = UserForm()
    
    context = {
        'form' : form
    }
    return render(request, 'accounts/registerUser.html', context = context)

