import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    return User.objects.create_user(
        email="user@example.com",
        password="P@ssw0rd123",
        username="user@example.com",
    )


@pytest.mark.django_db
class TestLoginEndpoint:
    def test_login_success(self, api_client, create_user):
        """Перевірка успішного входу: 200 OK + access, refresh та user payload."""
        url = reverse("users:login")
        payload = {
            "email": "user@example.com",
            "password": "P@ssw0rd123",
            "remember": True,
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "user@example.com"
        assert response.data["user"]["id"] == create_user.id

    def test_login_invalid_credentials(self, api_client, create_user):
        """Перевірка невірного пароля: 401 Unauthorized та абстрактна помилка."""
        url = reverse("users:login")
        payload = {"email": "user@example.com", "password": "WrongPassword"}
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Invalid credentials"

    def test_login_missing_fields(self, api_client):
        """Перевірка помилки валідації: 400 Bad Request при відсутності полів."""
        url = reverse("users:login")
        payload = {"email": "user@example.com"}
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_rate_limiting(self, api_client, create_user):
        """Перевірка throttling захисту: 429 Too Many Requests після 5 спроб."""
        url = reverse("users:login")
        payload = {"email": "user@example.com", "password": "WrongPassword"}

        for _ in range(5):
            api_client.post(url, payload, format="json")

        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
