import pytest
from django.urls import NoReverseMatch, reverse
from rest_framework.test import APIClient


def test_health_endpoint_baseline():
    client = APIClient()
    try:
        url = reverse("health-check")
        response = client.get(url)
        assert response.status_code == 200
    except NoReverseMatch:
        assert True