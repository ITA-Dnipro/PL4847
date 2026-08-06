"""
URL configuration for project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("dashboard.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path("api/", include("content.urls")),
    path("api/auth/", include("authentication.urls")),
    path("api/", include("users.urls")),
    path("api/", include("startups.urls")),
]
