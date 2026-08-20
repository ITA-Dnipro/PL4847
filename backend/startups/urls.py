from django.urls import path

from .views import StartupListView, SubscribeView

urlpatterns = [
    path("startups/", StartupListView.as_view(), name="startup-list"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
]
