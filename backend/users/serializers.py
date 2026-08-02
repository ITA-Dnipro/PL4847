import base64
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):

        validate_password(value)
        return value

    def validate(self, data):
        raw_token = data["token"]

        if ":" not in raw_token:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        uidb64, token = raw_token.split(":", 1)

        try:

            padding = "=" * (-len(uidb64) % 4)
            uid = force_str(base64.urlsafe_b64decode(uidb64 + padding))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()

        logger.info(
            f"AUDIT: Password successfully reset for user ID: {user.pk}, Email: {user.email}"
        )
        return user
