from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages


from accounts.models import UserProfile
from .models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm

# Create your views here.
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user = request.user)
    vendor = get_object_or_404(Vendor, user = request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance = profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance = vendor)

        if not profile_form.is_valid() and vendor_form.is_valid():
            messages.error(request, 'Something went wrong, please check your input')
            return redirect('v_profile')
        
        profile_form.save()
        vendor_form.save()
        messages.success(request, 'Your profile has updated successfully')
        return redirect('v_profile')

    # since its a update form need to pass the instance of the classes to get the user data
    profile_form = UserProfileForm(instance= profile)
    vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    return render(request, 'vendor/vendor_profile.html', context = context)
