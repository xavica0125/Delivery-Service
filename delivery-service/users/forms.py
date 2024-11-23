from django import forms
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Submit,
    Button,
    Layout,
    Fieldset,
    Row,
    Column,
    Div,
    HTML,
    ButtonHolder,
    Field,
)
from crispy_bootstrap5.bootstrap5 import FloatingField
from delivery_service.settings import EMAIL_HOST_USER
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from .task import send_password_reset_email
from .models import Customer, Address, Order
from .utils import validate_customer_address

"""User registration form that extends the UserCreationForm from Django's auth module. The form includes fields for first name, last name, email, username, and password."""


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    first_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"autofocus": True})
    )
    last_name = forms.CharField(max_length=50, widget=forms.TextInput())
    phone_number = forms.CharField(max_length=14, widget=forms.TextInput())
    notification_preference = forms.ChoiceField(choices=Customer.ContactChoice)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("register")

        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField("first_name"),
                FloatingField("last_name"),
                FloatingField("username"),
                FloatingField("email"),
                FloatingField(
                    "phone_number"
                ),  # TODO phone number formatting is not always applied
                FloatingField("notification_preference"),
                FloatingField("password1"),
                FloatingField("password2"),
            ),
            Div(
                Submit(
                    "save",
                    "Sign Me Up",
                    css_class="btn btn-primary",
                ),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )

    def create_customer(self, user):
        phone_number = self.cleaned_data.get("phone_number")
        notification_preference = self.cleaned_data.get("notification_preference")
        customer = Customer.objects.create(
            user=user,
            phone_number=phone_number,
            notification_preference=notification_preference,
        )


"""Customer sign up form to fill out additional preferences."""


class CustomerSignUpForm(forms.ModelForm):  # TODO change name of class
    street_address = forms.CharField(max_length=50, label="Street Address")
    sub_premise = forms.CharField(
        max_length=50, label="Street Address 2 (eg. Building, Apt #)", required=False
    )
    city = forms.CharField(max_length=50)
    state = forms.CharField(
        max_length=2,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "grayed-out"}),
        initial="TX",
        required=False,
    )
    zip_code = forms.CharField(max_length=10, label="Zip Code")
    validation_action, validation_response = None, None
    formatted_entered_address = ""

    class Meta:
        model = Address
        fields = (
            "street_address",
            "sub_premise",
            "city",
            "state",
            "zip_code",
        )

    def __init__(self, *args, **kwargs):
        super(CustomerSignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("customer_sign_up")

        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField("street_address"),
                FloatingField("sub_premise"),
                FloatingField("city"),
                FloatingField("state"),
                FloatingField("zip_code"),
            ),
            Div(
                Submit("submit", "Submit", css_class="btn btn-primary"),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        street_address = cleaned_data.get("street_address")
        sub_premise = cleaned_data.get("sub_premise")
        city = cleaned_data.get("city")
        zip_code = cleaned_data.get("zip_code")

        self.formatted_entered_address = (
            f"{street_address} {sub_premise}, {city}, TX, {zip_code}"
        )

        address = f"{street_address} {sub_premise}" if sub_premise else street_address

        self.validation_action, self.validation_response = validate_customer_address(
            address, city, zip_code
        )

        if self.validation_action == "FIX":
            raise forms.ValidationError(
                "The provided address is invalid. Please check and try again."
            )
        elif self.validation_action == "CONFIRM":
            raise forms.ValidationError("Confirm your address.")

        return cleaned_data

    def get_formatted_address(self):
        return self.validation_response.result.address.formatted_address

    def get_entered_address(self):
        return self.formatted_entered_address

    def get_address_components(self):
        return self.validation_response.result.address.address_components


"""User login form that includes fields for username and password."""


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"autofocus": True})
    )
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("login")

        # Define layout
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField(
                    "username",
                ),
                FloatingField(
                    "password",
                ),
            ),
            Div(
                Div(
                    HTML(
                        '<p><a href={{ "reset_password" }} class="link-offset-2 link-offset-3-hover link-underline link-underline-opacity-0 link-underline-opacity-75-hover">Forgot Password?</a></p>'
                    ),
                    css_class="me-auto",
                ),
                Div(
                    Submit("submit", "Login", css_class="btn btn-primary"),
                    HTML(
                        '<a href={{ "register" }} class="btn btn-secondary">Sign Up</a>'
                    ),
                    css_class="d-flex gap-2",
                ),
                css_class="d-flex justify-content-between align-items-center",
            ),
        )


"""Password reset form (enter email)"""


class Password_Reset_Form(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput())

    def __init__(self, *args, **kwargs):
        super(Password_Reset_Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("reset_password")
        self.helper.layout = Layout(
            FloatingField("email"),
            ButtonHolder(
                Submit("submit", "Enter", css_class="btn btn-primary"),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )

    def get_email(self, email):
        return User.objects.filter(email=email).first()

    def save(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        user = self.get_email(email)

        if user:
            request = kwargs.get("request")
            current_site = get_current_site(request)
            token_generator = kwargs.get("token_generator", default_token_generator)
            use_https = kwargs.get("use_https", False)

            # Send the task to Celery
            send_password_reset_email.delay(
                user_id=user.pk,
                domain=current_site.domain,
                protocol="https" if use_https else "http",
                token=token_generator.make_token(user),
            )


"""Password reset confirm form (enter new password)"""


class Password_Reset_Confirm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(),
        help_text="",
    )
    new_password2 = forms.CharField(
        label="New Password Confirmation",
        widget=forms.PasswordInput(),
        help_text="Enter the same password as before, for verification.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField("new_password1"),
                FloatingField("new_password2"),
            ),
            ButtonHolder(
                Submit("submit", "Submit", css_class="btn btn-primary"),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )


"""Order model form """


class CreateOrderForm(forms.ModelForm):
    pickup_address = forms.ModelChoiceField(
        queryset=Address.objects.none(), empty_label=None
    )
    delivery_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label="Select a destination",
    )
    time_window = forms.ChoiceField(
        choices=Order.TimeWindow,
        widget=forms.RadioSelect(),
        initial=Order.TimeWindow.TWO_HOUR,
    )
    weight = forms.IntegerField(label="Weight (in pounds)")
    content = forms.Textarea()

    class Meta:
        model = Order
        fields = (
            "pickup_address",
            "delivery_address",
            "time_window",
            "weight",
            "content",
        )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        user = Customer.objects.get(user=user)
        all_user_addresses = user.addresses.all()
        self.fields["pickup_address"].queryset = all_user_addresses
        self.fields["pickup_address"].initial = user.default_pickup_address
        self.fields["delivery_address"].queryset = all_user_addresses
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("create_delivery")
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        FloatingField("pickup_address"),
                        Button(
                            "add_new_address",
                            "Add new address",
                            css_class="btn btn-primary",
                            onclick=f"location.href='{reverse_lazy('customer_sign_up')}'",
                        ),
                        css_class="col",
                    ),
                    css_class="row mb-3",
                ),
                Div(
                    Div(
                        FloatingField("delivery_address"),
                        Button(
                            "add_new_address",
                            "Add new address",
                            css_class="btn btn-primary",
                            onclick=f"location.href='{reverse_lazy('customer_sign_up')}'",
                        ),
                        css_class="col",
                    ),
                    css_class="row mb-3",
                ),
                Div(
                    Div(
                        "time_window",
                        css_class="col form-check form-switch",
                    ),
                    css_class="row mb-3",
                ),
                Div(
                    Div(
                        FloatingField("weight"),
                    ),
                    css_class="row mb-3",
                ),
                Div(
                    Div(
                        FloatingField("content"),
                    ),
                    css_class="row mb-3",
                ),
                Div(css_id="price-div"),
                ButtonHolder(
                    Button(
                        "calculate_price",
                        "Calculate Price",
                        css_class="btn btn-secondary",
                        **{
                            "hx-get": reverse_lazy("calculate_price"),
                            "hx-target": "#price-div",
                            "hx-trigger": "click",
                        },
                    ),
                    Submit("submit", "Submit", css_class="btn btn-primary"),
                    css_class="d-grid gap-2 d-md-flex justify-content-md-end",
                ),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("pickup_address") == cleaned_data.get("delivery_address"):
            raise forms.ValidationError(
                "Pickup and delivery address can't be the same."
            )

        return cleaned_data
