import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from rest_framework import serializers

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Серіалізатор для запиту на скидання пароля за вказаним email.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Серіалізатор для підтвердження скидання пароля та встановлення нового.
    """

    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        combined_token = attrs.get("token", "")
        password = attrs.get("password", "")

        if ":" not in combined_token:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        uidb64, token = combined_token.split(":", 1)

        try:
            uid = force_str(base64.urlsafe_b64decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):

            raise serializers.ValidationError(
                {"token": "Invalid or expired token."}
            ) from None

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        validate_password(password, user=user)

        attrs["user"] = user
        return attrs
