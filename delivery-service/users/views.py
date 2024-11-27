from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CreateUserForm, CustomerSignUpForm, LoginForm, CreateOrderForm
from .models import *
from django.contrib.auth.decorators import login_required
from django_htmx.http import retarget, HttpResponseClientRedirect
from django.http import JsonResponse
from .utils import *


"""Registration view that validates the form and saves the user to the database"""


def register(request):
    print(request.session.items())

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password1 = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password1)
            form.create_customer(user)
            if user is not None:
                auth_login(request, user)
                request.session.save()
                print(request.session.items())
                return redirect("customer_sign_up")
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = CreateUserForm()
    return render(request, "register.html", {"form": form})


"""View after registration to input customer address."""


def customer_sign_up(request):
    print(request.user.is_authenticated)
    print(request.session.items())

    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            validated_address = form.save(commit=False)
            print(request.user.id)
            user = Customer.objects.get(user=request.user.id)
            validated_address.associated_customer = user
            validated_address.save()
            if user.default_pickup_address is None:
                user.default_pickup_address = validated_address
                user.save()
                messages.success(request, "Registration successful!")
                return redirect("customer_home")
            else:
                return redirect("create_delivery")
        else:
            print(form.errors)

            if "Confirm your address." in form.non_field_errors():
                formatted_address = form.get_formatted_address()
                address_components = form.get_address_components()
                context = populate_address_context(address_components)
                context["formatted_address"] = formatted_address
                context["entered_address"] = form.get_entered_address()
                context["location_name"] = request.POST.get("location_name")
                return render(request, "confirm_address.html", context)
            else:
                return render(request, "customer_sign_up.html", {"form": form})
    else:
        form = CustomerSignUpForm()
    return render(request, "customer_sign_up.html", {"form": form})


"""View that saves address components of inferred address to Customer model instance after user confirmation."""


def address_confirmation(request):
    user = Customer.objects.get(user=request.user)
    user.street_address = request.POST.get("street_address")
    user.sub_premise = request.POST.get("sub_premise")
    user.city = request.POST.get("city")
    user.zip_code = request.POST.get("zip_code")

    user.save()

    return redirect("customer_home")


# User login view that authenticates the user and logs them in
def login(request):
    print(request.user.is_authenticated)
    print(request.session.items())
    request.session.flush()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Login successful!")
                return redirect("customer_home")
            else:
                messages.error(request, "Username or password is incorrect.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


# User logout view that logs the user out
@login_required(login_url="/")
def logout(request):
    auth_logout(request)
    request.session.clear()
    messages.success(request, "Logout successful!")
    return redirect("login")


@login_required(login_url="/")
def customer_home(request):
    print(request.user.id)
    print(request.user.is_authenticated)

    return render(request, "customer_home.html", {})


@login_required(login_url="/")
def create_delivery(request):
    if request.method == "POST":
        form = CreateOrderForm(request.POST, user=request.user.id)
        if form.is_valid():
            form.save()
            messages.success(request, "Order added succesfully!")
            return redirect("customer_home")
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = CreateOrderForm(user=request.user.id)
        return render(
            request,
            "create_delivery.html",
            {"form": form},
        )


def calculate_price(request):
    response = price_calculation(request)

    return render(request, "calculate_price.html", {"polyline": response})
