from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import (
    CreateUserForm,
    CustomerSignUpForm,
    LoginForm,
    CreateOrderForm,
    ContactForm,
)
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django_htmx.http import retarget, HttpResponseClientRedirect, reswap, push_url
from .utils import *
from django.db.models import Q, CharField
from django.db.models.functions import Cast
import decimal
import json

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
            Contact.objects.create(
                contact_name=request.POST.get("contact_name"),
                phone_number=request.POST.get("phone_number"),
                address=validated_address,
            )
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
                context["contact_name"] = request.POST.get("contact_name")
                context["phone_number"] = request.POST.get("phone_number")
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
    recent_order_list = retrieve_orders(request.user.id, "recent")

    return render(
        request, "customer_home.html", {"recent_order_list": recent_order_list}
    )


@login_required(login_url="/")
def create_delivery(request):
    if request.method == "POST":
        form = CreateOrderForm(request.POST, user=request.user.id)
        if form.is_valid():
            ref_list = json.loads(request.POST.get("jsonRefValues"))
            distance = request.POST.get("distance")
            order_instance = form.save(distance, request.user.id)
            add_reference_values(ref_list, order_instance)
            tax = f"{order_instance.total_amount * (Decimal(8.25) / 100):,.2f}"
            context = {
                "order_instance": order_instance,
                "order_price": f"{order_instance.total_amount:,.2f}",
                "tax": tax,
                "final_price": f"{order_instance.total_amount + Decimal(tax):,.2f}",
            }
            return render(request, "calculate_price.html", context)
        else:
            return render(request, "create_delivery.html", {"form": form})
    else:
        form = CreateOrderForm(user=request.user.id)
        return render(
            request,
            "create_delivery.html",
            {"form": form},
        )


@login_required(login_url="/")
def delivery_price(request):
    return render(request, "calculate_price.html")


@login_required(login_url="/")
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(
            request.POST, delivery_address_pk=request.POST.get("address")
        )
        if form.is_valid():
            contact_instance = form.save(commit=False)
            contact_instance.phone_number = request.POST.get("phone_number")
            contact_instance.save()
            messages.success(request, "Contact successfully added!")
            return redirect("create_delivery")
    else:
        delivery_address = request.GET.get("delivery_address")
        form = ContactForm(delivery_address_pk=delivery_address)
        return render(
            request,
            "create_contact.html",
            {"form": form},
        )


@login_required(login_url="/")
def contact_options(request):
    delivery_address = request.GET.get("delivery_address")
    contact_list = Contact.objects.filter(address=delivery_address)
    context = {
        "contact_list": contact_list,
        "delivery_address": delivery_address,
    }
    return render(request, "contact_options.html", context)


@login_required(login_url="/")
def view_deliveries(request):
    if request.method == "GET":
        order_list = retrieve_orders(request.user.id)
        paginator = Paginator(order_list, 25)
        requested_page = request.GET.get("page")
        is_end = False
        if paginator.num_pages == int(requested_page):
            is_end = True
        try:
            page_obj = paginator.get_page(int(requested_page))
        except ValueError:
            return render(request, "view_deliveries.html", {"order_list": []})
        else:
            if request.htmx:
                return render(
                    request,
                    "partials/load_more_orders.html",
                    {"continued_order_list": page_obj, "is_end": is_end},
                )
            else:
                return render(
                    request,
                    "view_deliveries.html",
                    {"order_list": page_obj, "is_end": is_end},
                )


@login_required(login_url="/")
def delivery_details(request):
    if request.method == "GET":
        delivery_control_number = request.GET.get("control_number")
        delivery_instance = Order.objects.get(control_number=delivery_control_number)
        response = render(
            request, "view_order.html", {"delivery_instance": delivery_instance}
        )
        return push_url(
            response, f"/delivery/details/?control_number={delivery_control_number}"
        )  # Return delivery details along with updating URL history to be able to return back to previous table state


@login_required(login_url="/")
def search_deliveries(request):
    if request.method == "POST":
        search_string = request.POST.get("search")
        print(search_string)

        search_queryset = Order.objects.annotate(
            ref_num=Cast("control_number", CharField()),
        ).filter(
            Q(time_created_string__icontains=search_string)
            | Q(ref_num__icontains=search_string)
            | Q(delivery_address__full_address__icontains=search_string)
            | Q(pickup_address__full_address__icontains=search_string)
        )

        return render(
            request, "partials/search_results.html", {"search_results": search_queryset}
        )
