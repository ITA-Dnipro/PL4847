import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


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
    thumbnail_url = models.URLField(
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
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="startup_profiles",
    )
    tags = models.ManyToManyField(Tag, related_name="startups", blank=True)

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


class Subscription(models.Model):
    startup = models.ForeignKey(
        "StartupProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="startup_subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["startup", "user"],
                name="unique_subscription_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.startup}"
