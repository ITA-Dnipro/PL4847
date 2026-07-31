from rest_framework import status
from rest_framework.test import APIClient


def test_get_landing_content_structure():
    """Test GET /api/content/landing/ returns 200 OK and valid JSON schema."""
    client = APIClient()
    response = client.get("/api/content/landing/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Top-level keys check
    assert "hero" in data
    assert "for_whom" in data
    assert "why_worth" in data
    assert "footer_links" in data

    # Detailed schema assertions
    assert isinstance(data["hero"]["hero_images"], list)

    assert isinstance(data["for_whom"], list)
    assert all({"icon", "title", "desc"} <= item.keys() for item in data["for_whom"])

    assert isinstance(data["why_worth"], list)
    assert all({"title", "desc"} <= item.keys() for item in data["why_worth"])

    assert "left" in data["footer_links"]
    assert "right" in data["footer_links"]

    for side in ("left", "right"):
        assert isinstance(data["footer_links"][side], list)
        assert all(
            {"name", "url"} <= link.keys() for link in data["footer_links"][side]
        )
