import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_landing_content_success(client):
    """
    Перевірка ендпоінту GET /api/content/landing/ та відповідності структури JSON.
    """
    url = reverse("landing-content")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "hero" in data
    assert "for_whom" in data
    assert "why_worth" in data
    assert "footer_links" in data

    assert "title" in data["hero"]
    assert "subtitle" in data["hero"]
    assert "cta_text" in data["hero"]
    assert "hero_images" in data["hero"]

    assert isinstance(data["for_whom"], list)
    assert isinstance(data["why_worth"], list)
    assert "left" in data["footer_links"]
    assert "right" in data["footer_links"]
