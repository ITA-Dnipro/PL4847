from django.urls import path

from .views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileDetailView,
    RegisterView,
)

app_name = "users"

urlpatterns = [
    path(
        "auth/login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "profiles/<uuid:id>/",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path("auth/register/", RegisterView.as_view(), name="register"),
]
