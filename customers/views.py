from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import User, UserProfile
from accounts.forms import UserProfileForm, UserInfoForm

# Create your views here.
@login_required(login_url='login')
def cust_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)    

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if not profile_form.is_valid() or not user_form.is_valid():
            if not profile_form.is_valid():
                messages.error(request, "Something went wrong, your profile conents are not valid")
            elif not user_form.is_valid():
                messages.error(request, "Something went wrong, either firstname, lastname or phone number is not valid")
            return redirect('cust_profile')
        else:
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile successfully updated")
            return redirect('cust_profile')

    if request.method == 'GET':
        profile_form = UserProfileForm(instance = profile)
        user_form = UserInfoForm(instance= request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }
    return render(request, 'customers/cust_profile.html', context=context)
