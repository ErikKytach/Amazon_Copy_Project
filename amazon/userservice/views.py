from django.shortcuts import render, redirect
from userservice.forms import *
from django.contrib.auth import *
from main.views import *

def registration_func(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session["user_id"] = user.id
            create_cart_func(request)
            return redirect(all_products_func)
    form = UserRegistrationForm()

    slovnik = {
        "form": form
    }

    return render(request, "registration.html", context = slovnik)

def login_func(request):
    if request.method == "POST":
        form = UserLoginForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username = username, password = password)
            if user != None:
                request.session["user_id"] = user.id
                login(request, user)
                return redirect(all_products_func)
    else:
        form = UserLoginForm()

        slovnik = {
            "form": form
        }
        return render(request, "login.html", context=slovnik)
    

def logout_func(request):
    logout(request)
    return redirect(all_products_func)



def buy_cart_func(request):
    if request.method == "POST":
        paymenttype = request.POST.get("paymenttype")