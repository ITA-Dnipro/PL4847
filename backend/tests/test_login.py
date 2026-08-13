from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


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
    assert response.data["user"]["role"] == "startup"  # <-- Додано перевірку role
