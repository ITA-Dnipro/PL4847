from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Location, StartupProfile, Tag

User = get_user_model()


def make_user(username, email):
    user = User.objects.create_user(
        username=username,
        email=email,
        password="testpass123",
    )
    if hasattr(user, "role"):
        user.role = "startup"
        user.save(update_fields=["role"])
    return user


class StartupListAPITests(APITestCase):
    url = reverse("startup-list")

    @classmethod
    def setUpTestData(cls):
        cls.craft_tag = Tag.objects.create(name="Craft", slug="craft")
        cls.saas_tag = Tag.objects.create(name="SaaS", slug="saas")

        cls.chernivtsi = Location.objects.create(name="Chernivtsi", slug="chernivtsi")
        cls.lviv = Location.objects.create(name="Lviv", slug="lviv")
        cls.kyiv = Location.objects.create(name="Kyiv", slug="kyiv")

        cls.user1 = make_user("owner1", "owner1@example.com")
        cls.user2 = make_user("owner2", "owner2@example.com")
        cls.user3 = make_user("owner3", "owner3@example.com")

        cls.published_craft = StartupProfile.objects.create(
            user=cls.user1,
            company_name="Handmade Co",
            slug="handmade-co",
            short_description="Woodwork and ceramics",
            thumbnail_url="https://example.com/media/thumbs/1.jpg",
            location=cls.chernivtsi,
            status=StartupProfile.Status.PUBLISHED,
        )
        cls.published_craft.tags.add(cls.craft_tag)

        cls.published_saas = StartupProfile.objects.create(
            user=cls.user2,
            company_name="CloudLedger",
            slug="cloudledger",
            short_description="Cloud-based accounting",
            thumbnail_url="https://example.com/media/thumbs/2.jpg",
            location=cls.lviv,
            status=StartupProfile.Status.PUBLISHED,
        )
        cls.published_saas.tags.add(cls.saas_tag)

        cls.draft = StartupProfile.objects.create(
            user=cls.user3,
            company_name="Draft Startup",
            slug="draft-startup",
            short_description="Not visible yet",
            thumbnail_url="https://example.com/media/thumbs/3.jpg",
            location=cls.kyiv,
            status=StartupProfile.Status.DRAFT,
        )

        extra_users = [
            make_user(f"owner_extra_{i}", f"owner_extra_{i}@example.com")
            for i in range(7)
        ]
        for i, user in enumerate(extra_users):
            StartupProfile.objects.create(
                user=user,
                company_name=f"Extra Startup {i}",
                slug=f"extra-startup-{i}",
                short_description="Filler record",
                thumbnail_url=f"https://example.com/media/thumbs/extra-{i}.jpg",
                location=cls.kyiv,
                status=StartupProfile.Status.PUBLISHED,
            )

    def test_list_returns_only_published(self):
        response = self.client.get(self.url, {"page_size": 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_names = [item["company_name"] for item in response.data["results"]]
        self.assertNotIn(self.draft.company_name, company_names)
        self.assertEqual(response.data["count"], 9)

    def test_default_pagination_page_size_is_8(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 8)
        self.assertEqual(response.data["count"], 9)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_second_page_returns_remaining_item(self):
        response = self.client.get(self.url, {"page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_filter_by_tag(self):
        response = self.client.get(self.url, {"tag": "craft", "page_size": 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["company_name"], "Handmade Co")

    def test_search_by_company_name(self):
        response = self.client.get(self.url, {"search": "cloud", "page_size": 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["company_name"], "CloudLedger")

    def test_response_shape_matches_spec(self):
        response = self.client.get(self.url, {"tag": "craft"})
        result = response.data["results"][0]

        expected_keys = {
            "id",
            "company_name",
            "short_description",
            "thumbnail_url",
            "location",
            "tags",
        }
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result["location"], "Chernivtsi")
        self.assertIn("craft", result["tags"])

    def test_pagination_with_duplicate_company_names(self):
        user_alpha_1 = make_user("alpha_owner1", "alpha_owner1@example.com")
        user_alpha_2 = make_user("alpha_owner2", "alpha_owner2@example.com")

        StartupProfile.objects.create(
            user=user_alpha_1,
            company_name="Alpha Startup",
            slug="alpha-1",
            short_description="First alpha",
            thumbnail_url="https://example.com/media/thumbs/alpha1.jpg",
            location=self.chernivtsi,
            status=StartupProfile.Status.PUBLISHED,
        )
        StartupProfile.objects.create(
            user=user_alpha_2,
            company_name="Alpha Startup",
            slug="alpha-2",
            short_description="Second alpha",
            thumbnail_url="https://example.com/media/thumbs/alpha2.jpg",
            location=self.chernivtsi,
            status=StartupProfile.Status.PUBLISHED,
        )

        response = self.client.get(self.url, {"page_size": 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)