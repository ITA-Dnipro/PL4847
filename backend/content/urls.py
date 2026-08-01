from django.urls import path

from .views import LandingContentView

urlpatterns = [
    path("content/landing/", LandingContentView.as_view(), name="landing-content"),
]
