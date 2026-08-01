import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class StartupProfile(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="startup_profile",
    )
    company_name = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
    )
    description = models.TextField(
        blank=True,
    )
    website = models.URLField(
        max_length=500,
        blank=True,
    )
    contact_email = models.EmailField(
        blank=True,
    )
    logo_url = models.URLField(
        max_length=500,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company_name"]

    def clean(self) -> None:
        super().clean()

        if self.user_id and not self.user.can_have_startup_profile():
            raise ValidationError(
                {
                    "user": (
                        "Only users with startup or both role "
                        "can have a startup profile."
                    ),
                },
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.company_name
