import uuid

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
