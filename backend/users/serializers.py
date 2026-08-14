import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from startups.models import Tag

User = get_user_model()
logger = logging.getLogger(__name__)


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
        token = data.get("token")
        password = data.get("password")


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


class ProfileStatsField(serializers.DictField):
    child = serializers.FloatField(min_value=0)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                "Stats must be an object of numeric values."
            )
        if len(data) > 20:
            raise serializers.ValidationError(
                "Stats cannot contain more than 20 entries."
            )
        return super().to_internal_value(data)


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    contact = serializers.EmailField(
        source="contact_email", required=False, allow_blank=True
    )
    tags = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        required=False,
        queryset=Tag.objects.all(),
    )
    stats = ProfileStatsField(required=False)
    visibility = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "slug",
            "about_html",
            "short_description",
            "contact",
            "website",
            "tags",
            "stats",
            "visibility",
            "is_active",
        ]
        read_only_fields = ["id"]

    def get_visibility(self, obj) -> str:
        return "public" if obj.is_active_profile else "hidden"

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def update(self, instance, validated_data):
        activate = validated_data.pop("is_active", None)
        tags = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if activate is None or activate:
            instance.touch()
        else:
            instance.deactivate()

        instance.save()

        if tags is not None:
            instance.tags.set(tags)
        return instance
