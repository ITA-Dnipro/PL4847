from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from .password_reset import (
    PasswordResetLifecycleError,
    complete_password_reset,
    record_password_reset_event,
    request_metadata,
)

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset email."""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming and setting a new password via reset token."""

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        uidb64 = data.get("uid")
        password = data.get("password")
        request = self.context.get("request")
        metadata = request_metadata(request) if request is not None else {}

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"detail": "Invalid or expired token."}
            ) from None

        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            record_password_reset_event(
                user,
                "failed",
                "failure",
                metadata,
            )
            raise serializers.ValidationError({"password": list(e.messages)})

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["password"]
        request = self.context.get("request")
        metadata = request_metadata(request) if request is not None else {}

        try:
            return complete_password_reset(
                user,
                self.validated_data["token"],
                password,
                metadata,
            )
        except PasswordResetLifecycleError as error:
            raise serializers.ValidationError({"detail": str(error)}) from None
