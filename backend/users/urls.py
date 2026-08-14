from django.urls import path

from .views import PasswordResetConfirmView, PasswordResetRequestView, ProfileDetailView

app_name = "users"

urlpatterns = [
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
    path("profiles/<uuid:id>/", ProfileDetailView.as_view(), name="profile-detail"),
]
