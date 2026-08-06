import pytest
from authentication.tokens import generate_verification_token, verify_verification_token
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def disable_throttling_for_tests(settings):
    settings.REST_FRAMEWORK = {
        **getattr(settings, "REST_FRAMEWORK", {}),
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    }
    cache.clear()


@pytest.mark.django_db
def test_verify_email_activates_account():
    user = User.objects.create_user(
        username="pending-user",
        email="pending@example.com",
        password="test-password123",
        is_active=False,
    )
    token = generate_verification_token(user)

    client = APIClient()
    response = client.post("/api/auth/verify-email/", {"token": token}, format="json")

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_verify_email_rejects_missing_token():
    client = APIClient()
    response = client.post("/api/auth/verify-email/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_verify_email_rejects_invalid_token():
    client = APIClient()
    response = client.post(
        "/api/auth/verify-email/", {"token": "not-a-real-token"}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_verify_email_rejects_expired_token():
    user = User.objects.create_user(
        username="expiring-user",
        email="expiring@example.com",
        password="test-password123",
        is_active=False,
    )
    token = generate_verification_token(user)

    assert verify_verification_token(token, max_age=0) is None


@pytest.mark.django_db
def test_resend_verification_returns_200_for_unknown_email():
    client = APIClient()
    response = client.post(
        "/api/auth/resend-verification/",
        {"email": "nobody@example.com"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_resend_verification_sends_mail_for_inactive_user(mailoutbox):
    User.objects.create_user(
        username="resend-user",
        email="resend@example.com",
        password="test-password123",
        is_active=False,
    )

    client = APIClient()
    response = client.post(
        "/api/auth/resend-verification/",
        {"email": "resend@example.com"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["resend@example.com"]


@pytest.mark.django_db
def test_resend_verification_skips_already_active_user(mailoutbox):
    User.objects.create_user(
        username="active-user",
        email="active@example.com",
        password="test-password123",
        is_active=True,
    )

    client = APIClient()
    response = client.post(
        "/api/auth/resend-verification/",
        {"email": "active@example.com"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 0
