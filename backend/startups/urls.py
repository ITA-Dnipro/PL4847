from django.urls import path

from .views import StartupListView

urlpatterns = [
    path("startups/", StartupListView.as_view(), name="startup-list"),
]
