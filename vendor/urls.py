from django.urls import path, include
from . import views
from accounts import views as acc_view

urlpatterns = [
    path('', acc_view.my_account, name='v_account'),
    path('profile/', views.vendor_profile, name='v_profile'),

    # menu-builder
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # category crud
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # fooditems crud
    path('menu-builder/food-item/add/', views.add_food_items, name='add_food_items'),
    path('menu-builder/food-item/edit/<int:pk>/', views.edit_food_item, name='edit_food_items'),
    path('menu-builder/food-item/delete/<int:pk>/', views.delete_food_item, name='delete_food_items'),

    # opening hours
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove_opening_hours'),
]
