import base64
import hashlib
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .password_reset import issue_reset_token, request_metadata
from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class PasswordResetThrottle(AnonRateThrottle):
    rate = "5/min"


class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = "5/min"


class PasswordResetEmailThrottle(SimpleRateThrottle):
    """Limit reset mail volume per normalized email without revealing state."""

    scope = "password_reset_email"
    rate = "5/hour"

    def get_cache_key(self, request, view):
        email = str(request.data.get("email", "")).strip().lower()
        if not email:
            return None
        digest = hashlib.sha256(email.encode("utf-8")).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": digest}


class PasswordResetConfirmThrottle(AnonRateThrottle):
    rate = "5/min"


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Endpoint to blacklist refresh token and logout user.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetRequestView(APIView):
    """
    POST /api/auth/password-reset/
    Endpoint to request a password reset email.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRequestThrottle, PasswordResetEmailThrottle]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            user = User.objects.filter(email__iexact=email, is_active=True).first()

            if user:
                try:
                    uidb64 = (
                        base64.urlsafe_b64encode(force_bytes(user.pk))
                        .decode()
                        .rstrip("=")
                    )
                    token = default_token_generator.make_token(user)
                    issue_reset_token(user, token, request_metadata(request))

                    frontend_url = getattr(
                        settings, "FRONTEND_URL", "http://localhost:3000"
                    )
                    reset_url = (
                        f"{frontend_url}/reset-password/?uid={uidb64}&token={token}"
                    )

                    context = {
                        "user": user,
                        "user_name": user.get_full_name() or user.username,
                        "reset_link": reset_url,
                        "reset_url": reset_url,
                        "expiry_minutes": getattr(
                            settings, "PASSWORD_RESET_TIMEOUT", 3600
                        )
                        // 60,
                    }
                    subject = "Скидання пароля"
                    from_email = getattr(
                        settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
                    )

                    try:
                        text_content = render_to_string(
                            "emails/password_reset_email.txt", context
                        )
                        html_content = render_to_string(
                            "emails/password_reset_email.html", context
                        )

                        msg = EmailMultiAlternatives(
                            subject,
                            text_content,
                            from_email,
                            [user.email],
                            headers=(
                                {"Reply-To": getattr(settings, "DEFAULT_REPLY_TO", "")}
                                if getattr(settings, "DEFAULT_REPLY_TO", "")
                                else None
                            ),
                        )
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    except TemplateDoesNotExist:
                        send_mail(
                            subject=subject,
                            message=f"Password reset link: {reset_url}",
                            from_email=from_email,
                            recipient_list=[user.email],
                        )

                    logger.info(
                        "AUDIT: Password reset email sent for user ID: %s",
                        user.pk,
                    )
                except Exception:
                    logger.exception(
                        "AUDIT: Failed to process password reset email for user ID: %s",
                        user.pk,
                    )
            else:
                logger.info(
                    "AUDIT: Password reset requested for a non-existent or inactive account."
                )

            return Response(
                {"detail": "If the email exists, you will receive reset instructions."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    POST /api/auth/password-reset/confirm/
    Endpoint to validate reset token, apply password complexity rules, and update user password.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            try:
                user = serializer.save()
            except serializers.ValidationError as error:
                errors = error.detail
                if isinstance(errors, dict) and "detail" in errors:
                    detail = errors["detail"]
                    if isinstance(detail, (list, tuple)):
                        errors = {"detail": detail[0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            logger.info(
                "AUDIT: Password reset successfully completed for user ID: %s",
                user.pk,
            )
            return Response(
                {"detail": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )

        if "detail" in serializer.errors:
            return Response(
                {"detail": serializer.errors["detail"][0]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
