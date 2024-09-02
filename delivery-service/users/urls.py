from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from users.forms import Password_Reset_Form, Password_Reset_Confirm

urlpatterns = [
    path("", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="../templates/password_reset.html",
            form_class=Password_Reset_Form,
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="../templates/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=Password_Reset_Confirm,
            success_url="/",
            template_name="../templates/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
]
