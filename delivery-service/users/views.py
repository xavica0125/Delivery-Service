from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CreateUserForm, LoginForm, UserPreferences
from .models import *
from django.contrib.auth.decorators import login_required
from django_htmx.http import retarget, HttpResponseClientRedirect
from django.http import JsonResponse


# Registration view that validates the form and saves the user to the database
def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password1 = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Registration successful!")
                if request.htmx:
                    # response = JsonResponse({"redirect": "user_preferences"})
                    # response["HX-Redirect"] = redirect("user_preferences").url
                    response = HttpResponseClientRedirect("user_preferences")
                    return response
        else:
            if request.htmx:
                response = render(request, "register.html", {"form": form})
                return retarget(response, "#modals-here .modal-body")
    else:
        form = CreateUserForm()
    return render(request, "register.html", {"form": form})


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


# User Preferences view that saves the user Preferencess to the database
@login_required(login_url="/")
def set_user_preferences(request):
    obj, created = Preferences.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserPreferences(request.POST or None, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, ("Success! You have updated your Preferences."))
            return redirect("home")
        else:
            messages.error(request, ("There was an error with processing your form."))
    else:
        form = UserPreferences(request.POST or None, instance=obj)
    return render(request, "user_preferences.html", {"form": form})
