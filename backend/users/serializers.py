import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

try:
    from startups.models import Tag
except ImportError:
    try:
        from .models import Tag
    except ImportError:
        Tag = None

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for POST /api/auth/login/.
    Accepts email + password (+ optional remember flag) and returns
    JWT access & refresh tokens along with user payload.
    """

    username_field = "email"
    remember = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed("Invalid credentials", code="bad_credentials")

        self.user = user

        refresh = self.get_token(self.user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        user_role = getattr(self.user, "role", "startup")
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": user_role,
        }
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset email."""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming and setting a new password via reset token."""

    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        raw_token = data.get("token")
        password = data.get("password")

        if not raw_token or ":" not in raw_token:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        uidb64, token = raw_token.split(":", 1)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"token": "Invalid or expired token."}
            ) from None

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["password"]

        user.set_password(password)
        user.save()

        logger.info("AUDIT: Password successfully reset for user ID: %s", user.pk)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile detail and updates."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all() if Tag is not None else [],
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "tags",
        ]
        read_only_fields = ["id", "email"]
