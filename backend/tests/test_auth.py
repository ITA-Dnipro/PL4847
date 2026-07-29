import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestTokenRefreshAndLogout:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token_str = str(self.refresh)

        self.refresh_url = "/api/auth/refresh/"
        self.logout_url = "/api/auth/logout/"

    def test_refresh_token_success(self):
        """Перевірка успішного отримання нового access токена"""
        response = self.client.post(
            self.refresh_url, {"refresh": self.refresh_token_str}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_logout_and_token_blacklist(self):
        """Перевірка успішного виходу та блокування refresh токена"""

        logout_response = self.client.post(
            self.logout_url, {"refresh": self.refresh_token_str}
        )
        assert logout_response.status_code == status.HTTP_204_NO_CONTENT

        refresh_response = self.client.post(
            self.refresh_url, {"refresh": self.refresh_token_str}
        )

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
