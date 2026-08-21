import base64
import hashlib
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.cache import cache
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import PasswordResetAuditEvent, PasswordResetToken
from users.password_reset import hash_reset_token, issue_reset_token

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


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
        assert response.data == {
            "detail": "If the email exists, you will receive reset instructions."
        }
        assert len(mail.outbox) == 1
        assert "Скидання пароля" in mail.outbox[0].subject
        assert "test@example.com" in mail.outbox[0].to
        assert "/reset-password/?uid=" in mail.outbox[0].body
        assert "60" in mail.outbox[0].body
        assert mail.outbox[0].alternatives
        assert "Встановити новий пароль" in mail.outbox[0].alternatives[0][0]
        assert PasswordResetToken.objects.filter(user=test_user).count() == 1
        assert (
            PasswordResetAuditEvent.objects.filter(
                user=test_user,
                event_type=PasswordResetAuditEvent.EventType.ISSUED,
            ).count()
            == 1
        )

    def test_request_reset_non_existing_email_returns_200_and_no_email(
        self, api_client
    ):

        url = reverse("users:password-reset-request")
        response = api_client.post(url, {"email": "nonexistent@example.com"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "detail": "If the email exists, you will receive reset instructions."
        }
        assert len(mail.outbox) == 0

    def test_request_reset_ignores_ambient_authentication(self, api_client):
        response = api_client.post(
            reverse("users:password-reset-request"),
            {"email": "anonymous@example.com"},
            HTTP_AUTHORIZATION="Bearer stale-client-credential",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "detail": "If the email exists, you will receive reset instructions."
        }

    def test_request_reset_throttles_by_email_across_ips(self, api_client):
        url = reverse("users:password-reset-request")
        responses = [
            api_client.post(
                url,
                {"email": "throttle@example.com"},
                REMOTE_ADDR=f"192.0.2.{index}",
            )
            for index in range(1, 7)
        ]

        assert [response.status_code for response in responses[:5]] == [200] * 5
        assert responses[5].status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "account" not in str(responses[5].data).lower()

    def test_confirm_reset_success(self, api_client, test_user):
        uidb64 = (
            base64.urlsafe_b64encode(force_bytes(test_user.pk)).decode().rstrip("=")
        )
        token = default_token_generator.make_token(test_user)
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )

        url = reverse("users:password-reset-confirm")
        data = {
            "uid": uidb64,
            "token": token,
            "password": "NewStrongP@ssword2026",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Password changed successfully."}
        test_user.refresh_from_db()
        assert test_user.check_password("NewStrongP@ssword2026")

    def test_confirm_reset_invalid_token_returns_400(self, api_client, test_user):
        uidb64 = (
            base64.urlsafe_b64encode(force_bytes(test_user.pk)).decode().rstrip("=")
        )

        url = reverse("users:password-reset-confirm")
        data = {
            "uid": uidb64,
            "token": "invalid-token-123",
            "password": "NewStrongP@ssword2026",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Invalid or expired token."}

    def test_confirm_reset_rejects_combined_uid_and_token_payload(
        self, api_client, test_user
    ):
        uidb64 = (
            base64.urlsafe_b64encode(force_bytes(test_user.pk)).decode().rstrip("=")
        )
        token = default_token_generator.make_token(test_user)

        url = reverse("users:password-reset-confirm")
        data = {
            "token": f"{uidb64}:{token}",
            "password": "NewStrongP@ssword2026",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data

    def test_reset_token_lifecycle_record_can_be_created(self, test_user):
        raw_token = "raw-reset-token"
        lifecycle_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(hours=1),
        )

        assert lifecycle_record.pk is not None
        assert lifecycle_record.user == test_user
        assert lifecycle_record.used_at is None
        assert lifecycle_record.revoked_at is None

    def test_reset_token_lifecycle_allows_duplicate_token_hashes(self, test_user):
        token_hash = hashlib.sha256(b"repeated-reset-token").hexdigest()
        expires_at = timezone.now() + timedelta(hours=1)

        first_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        second_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        assert first_record.pk != second_record.pk
        assert PasswordResetToken.objects.filter(token_hash=token_hash).count() == 2

    def test_reset_token_lifecycle_does_not_store_raw_token_or_password(
        self, test_user
    ):
        raw_token = "raw-reset-token-value"
        password = "NewStrongP@ssword2026"
        lifecycle_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        field_names = {field.name for field in lifecycle_record._meta.concrete_fields}
        stored_values = {
            str(getattr(lifecycle_record, field_name)) for field_name in field_names
        }

        assert raw_token not in stored_values
        assert password not in stored_values
        assert "password" not in field_names

    def test_password_reset_audit_event_contains_only_permitted_metadata(
        self, test_user
    ):
        audit_event = PasswordResetAuditEvent.objects.create(
            user=test_user,
            event_type=PasswordResetAuditEvent.EventType.ISSUED,
            result=PasswordResetAuditEvent.Result.SUCCESS,
            ip_address="192.0.2.10",
            user_agent="K-02.1 test client",
        )
        field_names = {field.name for field in audit_event._meta.concrete_fields}

        assert field_names == {
            "id",
            "user",
            "event_type",
            "result",
            "ip_address",
            "user_agent",
            "created_at",
        }
        assert audit_event.user == test_user
        assert audit_event.event_type == PasswordResetAuditEvent.EventType.ISSUED
        assert audit_event.result == PasswordResetAuditEvent.Result.SUCCESS
        assert audit_event.ip_address == "192.0.2.10"
        assert audit_event.user_agent == "K-02.1 test client"

    def test_reset_token_uses_one_hour_lifetime(self, test_user):
        now = timezone.now()
        record = issue_reset_token(
            test_user,
            "one-hour-reset-token",
            now=now,
        )

        assert record.expires_at == now + timedelta(hours=1)

    def test_confirm_reset_expired_token_returns_400_without_password_change(
        self, api_client, test_user
    ):
        token = default_token_generator.make_token(test_user)
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() - timedelta(seconds=1),
        )

        response = api_client.post(
            reverse("users:password-reset-confirm"),
            {
                "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                .decode()
                .rstrip("="),
                "token": token,
                "password": "NewStrongP@ssword2026",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Invalid or expired token."}
        test_user.refresh_from_db()
        assert test_user.check_password("OldPassword123!")

    def test_confirm_reset_reused_token_returns_400(self, api_client, test_user):
        token = default_token_generator.make_token(test_user)
        first_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        second_record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        data = {
            "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
            .decode()
            .rstrip("="),
            "token": token,
            "password": "NewStrongP@ssword2026",
        }

        first_response = api_client.post(reverse("users:password-reset-confirm"), data)
        second_response = api_client.post(reverse("users:password-reset-confirm"), data)

        assert first_response.status_code == status.HTTP_200_OK
        assert second_response.status_code == status.HTTP_400_BAD_REQUEST
        assert second_response.data == {"detail": "Invalid or expired token."}
        assert (
            PasswordResetToken.objects.filter(
                user=test_user,
                token_hash=hash_reset_token(token),
                used_at__isnull=False,
            ).count()
            == 2
        )
        assert first_record.pk != second_record.pk

    def test_confirm_reset_revoked_token_returns_400(self, api_client, test_user):
        token = default_token_generator.make_token(test_user)
        record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
            revoked_at=timezone.now(),
        )

        response = api_client.post(
            reverse("users:password-reset-confirm"),
            {
                "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                .decode()
                .rstrip("="),
                "token": token,
                "password": "NewStrongP@ssword2026",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Invalid or expired token."}
        test_user.refresh_from_db()
        assert test_user.check_password("OldPassword123!")
        record.refresh_from_db()
        assert record.revoked_at is not None

    def test_weak_password_confirmation_creates_failure_audit_event(
        self, api_client, test_user
    ):
        token = default_token_generator.make_token(test_user)
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )

        response = api_client.post(
            reverse("users:password-reset-confirm"),
            {
                "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                .decode()
                .rstrip("="),
                "token": token,
                "password": "123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert PasswordResetAuditEvent.objects.filter(
            user=test_user,
            event_type=PasswordResetAuditEvent.EventType.FAILED,
            result=PasswordResetAuditEvent.Result.FAILURE,
        ).exists()

    def test_reset_failure_audit_and_monitoring_do_not_expose_secrets(
        self, api_client, test_user, caplog
    ):
        raw_token = "sensitive-reset-token"
        password = "SensitivePassword123!"
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(raw_token),
            expires_at=timezone.now() - timedelta(seconds=1),
        )

        with caplog.at_level("INFO", logger="users.password_reset"):
            response = api_client.post(
                reverse("users:password-reset-confirm"),
                {
                    "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                    .decode()
                    .rstrip("="),
                    "token": raw_token,
                    "password": password,
                },
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_reset_event" in caplog.text
        assert raw_token not in caplog.text
        assert password not in caplog.text
        assert PasswordResetAuditEvent.objects.filter(
            user=test_user,
            event_type=PasswordResetAuditEvent.EventType.EXPIRED,
            result=PasswordResetAuditEvent.Result.FAILURE,
        ).exists()

    def test_admin_can_inspect_and_revoke_outstanding_token(self, test_user):
        admin_user = User.objects.create_superuser(
            username="reset-admin",
            email="reset-admin@example.com",
            password="AdminStrongP@ssword2026",
        )
        token = default_token_generator.make_token(test_user)
        record = PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        admin_client = Client()
        admin_client.force_login(admin_user)

        changelist_url = reverse("admin:users_passwordresettoken_changelist")
        inspect_response = admin_client.get(changelist_url)
        revoke_response = admin_client.post(
            changelist_url,
            {
                "action": "revoke_password_reset_tokens",
                "_selected_action": [str(record.pk)],
            },
        )

        assert inspect_response.status_code == status.HTTP_200_OK
        assert revoke_response.status_code == status.HTTP_302_FOUND
        record.refresh_from_db()
        assert record.revoked_at is not None

    def test_successful_reset_blacklists_existing_refresh_tokens(
        self, api_client, test_user
    ):
        refresh = RefreshToken.for_user(test_user)
        token = default_token_generator.make_token(test_user)
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )

        response = api_client.post(
            reverse("users:password-reset-confirm"),
            {
                "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                .decode()
                .rstrip("="),
                "token": token,
                "password": "NewStrongP@ssword2026",
            },
        )
        refresh_response = api_client.post(
            "/api/auth/refresh/",
            {"refresh": str(refresh)},
        )

        assert response.status_code == status.HTTP_200_OK
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_successful_reset_invalidates_django_sessions(self, api_client, test_user):
        session_client = Client()
        session_client.force_login(test_user)
        session_key = session_client.session.session_key
        assert Session.objects.filter(session_key=session_key).exists()

        token = default_token_generator.make_token(test_user)
        PasswordResetToken.objects.create(
            user=test_user,
            token_hash=hash_reset_token(token),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        response = api_client.post(
            reverse("users:password-reset-confirm"),
            {
                "uid": base64.urlsafe_b64encode(force_bytes(test_user.pk))
                .decode()
                .rstrip("="),
                "token": token,
                "password": "NewStrongP@ssword2026",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert not Session.objects.filter(session_key=session_key).exists()
