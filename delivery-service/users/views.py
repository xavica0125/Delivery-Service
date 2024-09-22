from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CreateUserForm, CustomerSignUpForm, LoginForm
from .models import *
from django.contrib.auth.decorators import login_required
from django_htmx.http import retarget, HttpResponseClientRedirect
from django.http import JsonResponse
from .utils import *


# Registration view that validates the form and saves the user to the database
def register(request):
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
                messages.success(request, "Registration successful!")
                if request.htmx:
                    # response = JsonResponse({"redirect": "user_preferences"})
                    # response["HX-Redirect"] = redirect("user_preferences").url
                    # response = HttpResponseClientRedirect("customer_sign_up")
                    # return response
                    return redirect("customer_sign_up")
        else:
            if request.htmx:
                response = render(request, "register.html", {"form": form})
                return retarget(response, "#modals-here .modal-body")
    else:
        form = CreateUserForm()
    return render(request, "register.html", {"form": form})


"""View after registration to input customer address and payment information."""


def customer_sign_up(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                response = HttpResponseClientRedirect("user_preferences")
                return response
        else:
            if request.htmx:
                response = render(request, "customer_sign_up.html", {"form": form})
                return retarget(response, "#modals-here .modal-body")
    else:
        form = CustomerSignUpForm()
    return render(request, "customer_sign_up.html", {"form": form})


# User login view that authenticates the user and logs them in
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Login successful!")
                return redirect("user_preferences")
            else:

                messages.error(request, "Username or password is incorrect.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


# User logout view that logs the user out
def logout(request):
    auth_logout(request)
    messages.success(request, "Logout successful!")
    return redirect("login")
