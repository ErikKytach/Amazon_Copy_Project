"""
URL configuration for amazon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
from django.contrib.admin import site
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from main.views import *
from userservice.views import *

urlpatterns = [
    path("i18n/", include('django.conf.urls.i18n')),
    path("add_category/", add_category_func),
    path("add_manufacturer/", add_manufacturer_func),
    path('admin/', site.urls),
]

urlpatterns += i18n_patterns(
    path('', all_products_func, name='home'),
    path("all_products/", all_products_func, name='all_products'),
    path("add_product/", add_product_func, name='add_product'),
    path("registration/", registration_func, name='registration'),
    path("login/", login_func, name='login'),
    path("logout/", logout_func, name='logout'),
    path("info_product/<int:id>", info_product_func, name='info_product'),
    path("info_cart/", info_cart_func, name='info_cart'),
    path("add_to_cart/<int:id>/", add_item_to_cart_func, name='add_to_cart'),
    path("one_more/<int:id>/", add_item_plus_one_in_cart_func, name='one_more'),
    path("one_less/<int:id>/", remove_item_minus_one_in_cart_func, name='one_less'),
    path("clear_cart/", clear_cart_func, name='clear_cart'),
    path("buy_cart/", confirm_order_func, name='buy_cart'),
    path("all_orders/", all_orders_func, name='all_orders'),
    path("delete_orders/", delete_all_orders_func, name='delete_orders'),
    path("filter_by_manufacturer/", filter_by_manufacturer_func, name='filter_by_manufacturer'),
    path("filter_by_category/", filter_by_category_func, name='filter_by_category'),
    path("filter_by_price/", filter_by_price_func, name='filter_by_price'),
    path("filter_by_series/", filter_by_series_func, name='filter_by_series'),
    path("filter_by_processor/", filter_by_processor_func, name='filter_by_processor'),
    path("search/", search_products_func, name='search'),
    path("check_username/", check_username_func, name='check_username'),
    path("add_payment_method/", add_payment_method_func, name='add_payment_method'),
    path("my_products/", my_products_func, name='my_products'),
    path("edit_product/<int:product_id>/", edit_product_func, name='edit_product'),
    path("delete_product/<int:product_id>/", delete_product_func, name='delete_product'),
)

