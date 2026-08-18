import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


class InvestorProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investor_profile",
    )
    company_name = models.CharField(
        max_length=255,
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
    contact_phone = models.CharField(max_length=13, blank=True)
    investment_focus = models.CharField(
        max_length=255,
        blank=True,
    )
    min_investment = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    max_investment = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company_name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(min_investment__isnull=True) | Q(min_investment__gte=0)),
                name="investor_min_investment_nonnegative",
            ),
            models.CheckConstraint(
                condition=(Q(max_investment__isnull=True) | Q(max_investment__gte=0)),
                name="investor_max_investment_nonnegative",
            ),
            models.CheckConstraint(
                condition=(
                    Q(min_investment__isnull=True)
                    | Q(max_investment__isnull=True)
                    | Q(max_investment__gte=F("min_investment"))
                ),
                name="investor_max_investment_gte_min",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.user_id and not self.user.can_have_investor_profile():
            raise ValidationError(
                {
                    "user": (
                        "Only users with investor or both role "
                        "can have an investor profile."
                    ),
                },
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.company_name


class SavedStartup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        related_name="saved_startups",
    )
    startup = models.ForeignKey(
        "startups.StartupProfile",
        on_delete=models.CASCADE,
        related_name="saved_by_investors",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["investor", "startup"],
                name="unique_saved_startup",
            ),
        ]
        indexes = [
            models.Index(
                fields=["investor", "-added_at"],
                name="saved_investor_added_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.investor} saved {self.startup}"
