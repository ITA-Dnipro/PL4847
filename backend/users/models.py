import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


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
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    about_html = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.URLField(max_length=500)
    tags = models.ManyToManyField(
        "startups.Tag",
        related_name="user_profiles",
        blank=True,
    )
    stats = models.JSONField(default=dict, blank=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    newsletter_opt_in = models.BooleanField(default=False)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="unique_lower_email")
        ]

    @property
    def is_active_profile(self) -> bool:
        return self.updated_at is not None

    def touch(self) -> None:
        self.updated_at = timezone.now()

    def deactivate(self) -> None:
        self.updated_at = None

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

    def save(self, *args, **kwargs) -> None:
        if self._state.adding and self.updated_at is None:
            self.touch()
        super().save(*args, **kwargs)

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
