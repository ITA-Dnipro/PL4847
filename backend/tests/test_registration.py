import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_payload():
    return {
        "email": "alice@example.com",
        "password": "P@ssw0rd123",
        "password_confirm": "P@ssw0rd123",
        "role": "startup",
        "company_name": "Handmade Co",
        "first_name": "Alice",
        "last_name": "Smith",
    }


@pytest.mark.django_db
class TestRegistrationEndpoint:

    @pytest.mark.django_db(transaction=True)
    def test_create_user_startup_returns_201(self, api_client, valid_payload):
        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "alice@example.com"

        user = User.objects.get(email="alice@example.com")
        assert user.is_active is False
        assert user.role == "startup"

        startup = user.startup_profile
        assert startup.company_name == "Handmade Co"
        assert startup.slug == "handmade-co"

        assert len(mail.outbox) == 1
        assert "alice@example.com" in mail.outbox[0].to

    @pytest.mark.django_db(transaction=True)
    def test_create_user_investor_returns_201(self, api_client, valid_payload):
        valid_payload["role"] = "investor"

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "alice@example.com"

        user = User.objects.get(email="alice@example.com")
        assert user.is_active is False
        assert user.role == "investor"

        investor = user.investor_profile
        assert investor.company_name == "Handmade Co"

        assert len(mail.outbox) == 1
        assert "alice@example.com" in mail.outbox[0].to

    @pytest.mark.django_db
    def test_duplicate_email_returns_409(self, api_client, valid_payload):
        User.objects.create_user(
            email="alice@example.com", password="StrongPassword", username="Real"
        )

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "detail" in response.data

        assert User.objects.filter(email="alice@example.com").count() == 1

    @pytest.mark.django_db
    def test_password_missmatch_returns_400(self, api_client, valid_payload):
        valid_payload["password_confirm"] = "wrong"

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data
        assert not User.objects.filter(email="alice@example.com").exists()

    @pytest.mark.django_db
    def test_weak_password_returns_400(self, api_client, valid_payload):
        valid_payload["password"] = "weak"
        valid_payload["password_confirm"] = "weak"

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert not User.objects.filter(email="alice@example.com").exists()

    @pytest.mark.django_db
    def test_missing_required_field_returns_400(self, api_client, valid_payload):
        del valid_payload["password_confirm"]

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data
        assert not User.objects.filter(email="alice@example.com").exists()

    @pytest.mark.django_db
    def test_invalid_role_returns_400(self, api_client, valid_payload):
        valid_payload["role"] = "no_role"

        url = reverse("users:register")
        response = api_client.post(url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data
        assert not User.objects.filter(email="alice@example.com").exists()

    def test_no_slug_collision(self, api_client, valid_payload):
        url = reverse("users:register")
        response_1 = api_client.post(url, valid_payload)

        valid_payload["email"] = "bob@example.com"

        response_2 = api_client.post(url, valid_payload)

        assert response_1.status_code == status.HTTP_201_CREATED
        assert response_2.status_code == status.HTTP_201_CREATED

        startup_1 = User.objects.get(email="alice@example.com").startup_profile
        startup_2 = User.objects.get(email="bob@example.com").startup_profile

        assert startup_1.slug == "handmade-co"
        assert startup_2.slug == "handmade-co-2"
