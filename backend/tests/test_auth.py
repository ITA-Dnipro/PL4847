import pytest
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestAuthRefreshLogout:
    def setup_method(self):
        self.client = APIClient()
        self.password = get_random_string(12)
        self.user = User.objects.create_user(
            username="testuser", password=self.password
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token_str = str(self.refresh)
        self.access_token_str = str(self.refresh.access_token)

    def test_refresh_token_success(self):
        """Перевірка успішного отримання нового access токена"""
        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": self.refresh_token_str},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_logout_and_token_blacklist(self):
        """Перевірка виходу та блокування refresh токена"""

        logout_res = self.client.post(
            "/api/auth/logout/",
            {"refresh": self.refresh_token_str},
            format="json",
        )
        assert logout_res.status_code == status.HTTP_204_NO_CONTENT

        refresh_res = self.client.post(
            "/api/auth/refresh/",
            {"refresh": self.refresh_token_str},
            format="json",
        )
        assert refresh_res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_invalid_or_missing_token(self):
        """Негативні тести: відсутній або недійсний refresh токен"""

        res_missing = self.client.post("/api/auth/logout/", {}, format="json")
        assert res_missing.status_code == status.HTTP_400_BAD_REQUEST

        res_invalid = self.client.post(
            "/api/auth/logout/",
            {"refresh": "invalid_token_string"},
            format="json",
        )
        assert res_invalid.status_code == status.HTTP_400_BAD_REQUEST
