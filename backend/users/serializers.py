import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        raw_token = data.get("token")
        password = data.get("password")

        # 1. Перевірка наявності роздільника ':' між uidb64 та token
        if not raw_token or ":" not in raw_token:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        uidb64, token = raw_token.split(":", 1)

        # 2. Декодування base64 та пошук користувача
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"token": "Invalid or expired token."}
            ) from None

        # 3. Перевірка валідності токена
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        # 4. Перевірка складності пароля
        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["password"]

        # Збереження нового пароля
        user.set_password(password)
        user.save()

        # Аудит-лог (без PII - тільки user.pk)
        logger.info("AUDIT: Password successfully reset for user ID: %s", user.pk)
        return user
