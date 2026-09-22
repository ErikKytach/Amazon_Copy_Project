from django.shortcuts import render, redirect
from userservice.forms import *
from django.contrib.auth import *
from django.http import JsonResponse
from django.contrib import messages

def registration_func(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        print(form.data)
        print(request.POST)
        if form.is_valid() and "admin" not in form.cleaned_data["username"].lower():
            user = form.save()
            print()
            login(request, user)
            request.session["user_id"] = user.id
            from main.views import create_cart_func
            create_cart_func(request)
            return redirect('/all_products/')
        else:
            return redirect("/registration/")

    form = UserRegistrationForm()

    slovnik = {
        "form": form
    }

    return render(request, "registration.html", context = slovnik)

def login_func(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = UserLoginForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username = username, password = password)
            if user != None:
                request.session["user_id"] = user.id
                login(request, user)
                storage = messages.get_messages(request)
                storage.used = True
                return redirect('/all_products/')
    else:
        form = UserLoginForm()

    slovnik = {
        "form": form
    }
    return render(request, "login.html", context=slovnik)


def logout_func(request):
    logout(request)
    return redirect('/all_products/')



def buy_cart_func(request):
    if request.method == "POST":
        paymenttype = request.POST.get("paymenttype")


def check_username_func(request):
    username = request.GET.get("username", "")
    User = get_user_model()
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"is_taken": is_taken})