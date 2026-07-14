from django.urls import path
from api.views import HealthCheck

urlpatterns = [
    path('health/', HealthCheck.as_view())
]