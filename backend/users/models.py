import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
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
