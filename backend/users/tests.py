from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from investors.models import InvestorProfile, SavedStartup
from projects.models import Project
from rest_framework import status
from rest_framework.test import APITestCase
from startups.models import StartupProfile, Tag

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
        field_names = {field.name for field in User._meta.fields}

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

        with self.assertRaises(ValidationError):
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

    def test_investor_cannot_have_startup_profile(self):
        with self.assertRaises(ValidationError):
            StartupProfile.objects.create(
                user=self.investor_user,
                company_name="Invalid Startup",
                slug="invalid-startup",
            )

    def test_startup_cannot_have_investor_profile(self):
        with self.assertRaises(ValidationError):
            InvestorProfile.objects.create(
                user=self.startup_user,
                company_name="Invalid Investor",
            )


class ProfileAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass12345",
            name="Owner Co",
            slug="owner-co",
            short_description="We do things",
            website="https://example.com",
            contact_email="owner@example.com",
        )
        cls.owner.touch()
        cls.owner.save()

        cls.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass12345"
        )

        cls.craft_tag = Tag.objects.create(name="Craft", slug="craft")
        cls.owner.tags.add(cls.craft_tag)

    def url(self, user):
        return reverse("users:profile-detail", kwargs={"id": user.id})

    def test_get_public_profile_returns_expected_payload(self):
        response = self.client.get(self.url(self.owner))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {
            "id",
            "name",
            "slug",
            "about_html",
            "short_description",
            "contact",
            "website",
            "tags",
            "stats",
            "visibility",
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertEqual(response.data["visibility"], "public")
        self.assertIn("craft", response.data["tags"])

    def test_get_inactive_profile_hidden_from_public(self):
        self.owner.deactivate()
        self.owner.save()

        response = self.client.get(self.url(self.owner))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_profile_visible_to_owner(self):
        self.owner.deactivate()
        self.owner.save()

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url(self.owner))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visibility"], "hidden")

    def test_owner_can_patch_profile(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            self.url(self.owner), {"short_description": "Updated"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["short_description"], "Updated")
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.name, "Owner Co")
        self.assertIsNotNone(self.owner.updated_at)

    def test_patch_deactivate_sets_updated_at_null(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.url(self.owner), {"is_active": False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visibility"], "hidden")
        self.owner.refresh_from_db()
        self.assertIsNone(self.owner.updated_at)

    def test_put_missing_required_field_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.url(self.owner), {"slug": "owner-co"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_put_invalid_website_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            self.url(self.owner),
            {
                "name": "Owner Co",
                "slug": "owner-co",
                "website": "not-a-url",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("website", response.data)

    def test_put_unknown_tag_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            self.url(self.owner),
            {
                "name": "Owner Co",
                "slug": "owner-co",
                "tags": ["does-not-exist"],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tags", response.data)

    def test_put_invalid_stats_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            self.url(self.owner),
            {
                "name": "Owner Co",
                "slug": "owner-co",
                "stats": {"team_size": "not-a-number"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stats", response.data)

    def test_put_full_replace_success(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            self.url(self.owner),
            {
                "name": "New Name",
                "slug": "owner-co",
                "short_description": "Brand new",
                "website": "https://new.example.com",
                "stats": {"team_size": 5},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_patch_returns_401(self):
        response = self.client.patch(
            self.url(self.owner), {"short_description": "Hack"}
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_non_owner_patch_returns_403(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.url(self.owner), {"short_description": "Hack"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
