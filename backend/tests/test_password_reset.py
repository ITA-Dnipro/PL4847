import base64

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="OldPassword123!",
    )


@pytest.mark.django_db
class TestPasswordReset:

    def test_request_reset_existing_email_returns_200_and_sends_email(
        self, api_client, test_user
    ):

        url = reverse("users:password-reset-request")
        response = api_client.post(url, {"email": "test@example.com"})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert "Скидання пароля" in mail.outbox[0].subject
        assert "test@example.com" in mail.outbox[0].to

    def test_request_reset_non_existing_email_returns_200_and_no_email(
        self, api_client
    ):

        url = reverse("users:password-reset-request")
        response = api_client.post(url, {"email": "nonexistent@example.com"})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_confirm_reset_success(self, api_client, test_user):
        uidb64 = (
            base64.urlsafe_b64encode(force_bytes(test_user.pk)).decode().rstrip("=")
        )
        token = default_token_generator.make_token(test_user)
        combined_token = f"{uidb64}:{token}"

        url = reverse("users:password-reset-confirm")
        data = {
            "token": combined_token,
            "password": "NewStrongP@ssword2026",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.check_password("NewStrongP@ssword2026")

    def test_confirm_reset_invalid_token_returns_400(self, api_client, test_user):
        uidb64 = (
            base64.urlsafe_b64encode(force_bytes(test_user.pk)).decode().rstrip("=")
        )
        combined_token = f"{uidb64}:invalid-token-123"

        url = reverse("users:password-reset-confirm")
        data = {
            "token": combined_token,
            "password": "NewStrongP@ssword2026",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data
