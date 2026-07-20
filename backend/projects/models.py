import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        FUNDED = "funded", "Funded"
        ARCHIVED = "archived", "Archived"

    class Stage(models.TextChoices):
        IDEA = "idea", "Idea"
        MVP = "mvp", "MVP"
        EARLY_STAGE = "early_stage", "Early stage"
        GROWTH = "growth", "Growth"

    class Currency(models.TextChoices):
        UAH = "UAH", "UAH"
        USD = "USD", "USD"
        EUR = "EUR", "EUR"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    startup = models.ForeignKey(
        "startups.StartupProfile",
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(
        max_length=255,
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
    )
    description = models.TextField(
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.IDEA,
    )
    funding_goal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.UAH,
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["startup", "slug"],
                name="unique_startup_project_slug",
            ),
            models.CheckConstraint(
                condition=(
                    Q(funding_goal__isnull=True)
                    | Q(funding_goal__gte=0)
                ),
                name="project_funding_goal_nonnegative",
            ),
        ]
        indexes = [
            models.Index(
                fields=["startup", "status"],
                name="project_startup_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.title