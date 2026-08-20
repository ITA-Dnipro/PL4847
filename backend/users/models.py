import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STARTUP = "startup", "Startup"
        INVESTOR = "investor", "Investor"
        BOTH = "both", "Startup and investor"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STARTUP,
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def can_have_startup_profile(self) -> bool:
        return self.role in {
            self.Role.STARTUP,
            self.Role.BOTH,
        }

    def can_have_investor_profile(self) -> bool:
        return self.role in {
            self.Role.INVESTOR,
            self.Role.BOTH,
        }

    def __str__(self) -> str:
        return self.email


class PasswordResetToken(models.Model):
    """Persist non-sensitive lifecycle metadata for a password reset token."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token_hash = models.CharField(
        max_length=64,
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return str(self.id)


class PasswordResetAuditEvent(models.Model):
    """Store only non-sensitive metadata about password reset operations."""

    class EventType(models.TextChoices):
        ISSUED = "issued", "Issued"
        CONFIRMED = "confirmed", "Confirmed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        REUSED = "reused", "Reused"
        REVOKED = "revoked", "Revoked"

    class Result(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="password_reset_audit_events",
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
    )
    result = models.CharField(
        max_length=10,
        choices=Result.choices,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.CharField(
        max_length=512,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.result}"
