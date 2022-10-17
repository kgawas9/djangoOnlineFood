from unicodedata import category
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

from accounts.models import UserProfile
from accounts.decorators import is_role_vendor
from .models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, ItemForm


# Create your views here.


def get_vendor(request):
    vendor = Vendor.objects.get(user = request.user)
    return vendor


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



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def menu_builder(request):
    # call get_vendor helper function to get the vendor
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor = vendor).order_by('created_at')

    context = {
        # 'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context = context)



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)

    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)

    context = {
        'food_items': fooditems,
        'category': category,
    }

    return render(request, 'vendor/fooditems_by_category.html', context=context)


@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)

        if category_form.is_valid():
            # to assign category name and vendor to save the form
            category_name = category_form.cleaned_data['category_name']

            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)

            category.save()     # Id will be get generated
            category.slug = slugify(category_name) + '-' + str(category.id)

            category.save()

            messages.success(request, "Category successfully added")
            return redirect('menu_builder')
        else:
            print(category_form.errors)

    else:
        category_form = CategoryForm()

    context = {
        'cat_form': category_form,
    }
    return render(request, 'vendor/add_category.html', context=context)



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category_form = CategoryForm(request.POST, instance=category)

        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)

            category_form.save()
            messages.success(request, "Category updated successfully")
            return redirect('menu_builder')
        else:
            print(category_form.errors)

    else:
        category_form = CategoryForm(instance=category)
    
    context = {
        'cat_form': category_form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context=context)



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, f'{category} deleted successfully')
    return redirect('menu_builder')



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def add_food_items(request):
    if request.method == 'POST':
        item_form = ItemForm(request.POST, request.FILES)

        if item_form.is_valid():
            food_title = item_form.cleaned_data['food_title']
            fooditem = item_form.save(commit=False)
            fooditem.vendor = get_vendor(request)
            
            fooditem.save()
            fooditem.slug = slugify(food_title) + '-' + str(fooditem.id)
            fooditem.save()
            
            messages.success(request, f'{food_title} successfully added into database')
            return redirect('fooditems_by_category', fooditem.category.id)

    item_form = ItemForm()
    item_form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'item_form': item_form,
    }
    return render(request, 'vendor/add_items.html', context=context)


def edit_food_item(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)

    if request.method == 'POST':
        food_item_form = ItemForm(request.POST, request.FILES, instance=food_item)

        if food_item_form.is_valid():
            food_title = food_item_form.cleaned_data['food_title']

            food_item = food_item_form.save(commit=False)
            
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            
            food_item_form.save()
            messages.success(request, f"{food_item} successfully updated")
            return redirect('fooditems_by_category', food_item.category.id)

    else:
        food_item_form = ItemForm(instance=food_item)
        # to add filter
        food_item_form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'item_form': food_item_form,
        'food_item': food_item,
    }
    return render(request, 'vendor/edit_items.html', context=context)



@login_required(login_url='login')
@user_passes_test(is_role_vendor)
def delete_food_item(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    food_item.delete()
    messages.success(request, f"{food_item} successfully deleted..")
    return redirect('fooditems_by_category', food_item.category.id)

