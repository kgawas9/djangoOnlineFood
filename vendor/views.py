from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


from accounts.models import UserProfile
from accounts.decorators import is_role_vendor
from .models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm


# Create your views here.
@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user = request.user)
    vendor = get_object_or_404(Vendor, user = request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance = profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance = vendor)

        if not profile_form.is_valid() and vendor_form.is_valid():
            messages.error(request, 'Something went wrong, please see the error messages.')
            # return redirect('v_profile')

        else:
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Your profile has updated successfully')
            return redirect('v_profile')

    # since its a update form need to pass the instance of the classes to get the user data
    else:
        profile_form = UserProfileForm(instance= profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    return render(request, 'vendor/vendor_profile.html', context = context)
