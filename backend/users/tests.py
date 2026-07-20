from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from investors.models import InvestorProfile, SavedStartup
from projects.models import Project
from startups.models import StartupProfile


User = get_user_model()


class InitialModelsTests(TestCase):
    def setUp(self):
        self.startup_user = User.objects.create_user(
            username="startup-user",
            email="startup@example.com",
            password="test-password",
            role=User.Role.STARTUP,
        )
        self.investor_user = User.objects.create_user(
            username="investor-user",
            email="investor@example.com",
            password="test-password",
            role=User.Role.INVESTOR,
        )

        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name="Test Startup",
            slug="test-startup",
        )
        self.investor = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name="Test Investor",
            min_investment=Decimal("1000.00"),
            max_investment=Decimal("10000.00"),
        )

    def test_user_fields_exist(self):
        field_names = {
            field.name
            for field in User._meta.fields
        }

        expected_fields = {
            "id",
            "email",
            "role",
            "created_at",
            "updated_at",
        }

        self.assertTrue(expected_fields.issubset(field_names))

    def test_one_user_can_have_both_profiles(self):
        user = User.objects.create_user(
            username="both-user",
            email="both@example.com",
            password="test-password",
            role=User.Role.BOTH,
        )

        startup_profile = StartupProfile.objects.create(
            user=user,
            company_name="Both Startup",
            slug="both-startup",
        )
        investor_profile = InvestorProfile.objects.create(
            user=user,
            company_name="Both Investor",
        )

        self.assertEqual(
            user.startup_profile,
            startup_profile,
        )
        self.assertEqual(
            user.investor_profile,
            investor_profile,
        )

    def test_startup_can_have_multiple_projects(self):
        Project.objects.create(
            startup=self.startup,
            title="First project",
            slug="first-project",
        )
        Project.objects.create(
            startup=self.startup,
            title="Second project",
            slug="second-project",
        )

        self.assertEqual(
            self.startup.projects.count(),
            2,
        )

    def test_project_slug_is_unique_for_startup(self):
        Project.objects.create(
            startup=self.startup,
            title="First project",
            slug="same-slug",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Project.objects.create(
                    startup=self.startup,
                    title="Second project",
                    slug="same-slug",
                )

    def test_saved_startup_pair_is_unique(self):
        SavedStartup.objects.create(
            investor=self.investor,
            startup=self.startup,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SavedStartup.objects.create(
                    investor=self.investor,
                    startup=self.startup,
                )

    def test_saved_startup_has_added_date(self):
        saved_startup = SavedStartup.objects.create(
            investor=self.investor,
            startup=self.startup,
        )

        self.assertIsNotNone(saved_startup.added_at)

    def test_max_investment_cannot_be_less_than_min(self):
        user = User.objects.create_user(
            username="invalid-investor",
            email="invalid-investor@example.com",
            password="test-password",
            role=User.Role.INVESTOR,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                InvestorProfile.objects.create(
                    user=user,
                    company_name="Invalid Investor",
                    min_investment=Decimal("10000.00"),
                    max_investment=Decimal("1000.00"),
                )

    def test_funding_goal_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Project.objects.create(
                    startup=self.startup,
                    title="Invalid project",
                    slug="invalid-project",
                    funding_goal=Decimal("-1.00"),
                )