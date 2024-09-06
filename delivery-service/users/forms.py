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
from .models import Customer

"""User registration form that extends the UserCreationForm from Django's auth module. The form includes fields for first name, last name, email, username, and password."""


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    first_name = forms.CharField(max_length=50, widget=forms.TextInput())
    last_name = forms.CharField(max_length=50, widget=forms.TextInput())
    phone_number = forms.CharField(max_length=14, widget=forms.TextInput())

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
        self.fields["username"].widget.attrs["autofocus"] = False
        self.helper.form_action = reverse_lazy("register")
        self.helper.attrs = {
            "hx-post": reverse_lazy("register"),
            "hx-target": "#modals-here .modal-body",
        }
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField("first_name"),
                FloatingField("last_name"),
                FloatingField("username"),
                FloatingField("email"),
                FloatingField("phone_number"), #TODO phone number formatting is now always applied
                FloatingField("password1"),
                FloatingField("password2"),
            ),
            Div(
                Submit("save", "Sign Up", css_class="btn btn-primary ml-auto"),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )

    def create_customer(self, user):
        phone_number = self.cleaned_data.get("phone_number")
        customer = Customer.objects.create(user=user, phone_number=phone_number)
        return customer


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
                    Button(
                        "button",
                        "Sign Me Up",
                        css_class="btn btn-secondary",
                        **{
                            "hx-get": reverse_lazy(
                                "register"
                            ),  # URL to fetch the signup form
                            "hx-target": "#modals-here .modal-body",
                            "hx-trigger": "click",
                            "data-bs-toggle": "modal",
                            "data-bs-target": "#modals-here",
                        }
                    ),
                    # css_class="d-grid gap-2 d-md-flex justify-content-md-end",
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


"""User preferences form that allows the user to select their preferences based off of the categories in Preferences model."""


"""class UserPreferences(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically create boolean fields with custom widget attributes
        for field_name in self.Meta.fields:
            self.fields[field_name] = forms.BooleanField(required=False)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "",
                *self.Meta.fields,  # Include all fields in the layout
                css_class="form-check form-switch"
            ),
            ButtonHolder(
                Submit("submit", "Submit", css_class="btn btn-primary"),
                css_class="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
        )"""
