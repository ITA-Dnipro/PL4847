import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(
        username="testuser",
        password="testpassword123",
    )
    assert user.username == "testuser"
    assert user.is_active is True


def test_startup_profile_baseline_stub():
    assert True
