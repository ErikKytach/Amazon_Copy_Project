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
from django.contrib import admin
from django.urls import path
from main.views import *
from userservice.views import *

urlpatterns = [
    path("all_products/", all_products_func),
    path("add_product/", add_product_func),
    path("add_manufacturer/", add_manufacturer_func),
    path("add_category/", add_category_func),
    path("registration/", registration_func),
    path("login/", login_func),
    path("logout/", logout_func),
    path("info_product/<int:id>", info_product_func),
    path("info_cart/", info_cart_func),
    path("add_to_cart/<int:id>/", add_item_to_cart_func),
    path("one_more/<int:id>/", add_item_plus_one_in_cart_func),
    path("one_less/<int:id>/", remove_item_minus_one_in_cart_func),
    path("clear_cart/", clear_cart_func),
    path("buy_cart/", confirm_order_func),
    path("all_orders/", all_orders_func),
    path("delete_orders/", delete_all_orders_func),
    path("filter_by_manufacturer/", filter_by_manufacturer_func),
    path("filter_by_category/", filter_by_category_func),
    path("filter_by_price/", filter_by_price_func),
    path("filter_by_series/", filter_by_series_func),
    path("filter_by_processor/", filter_by_processor_func)
]
