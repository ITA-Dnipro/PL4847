import base64
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = "5/min"


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
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uidb64 = (
                    base64.urlsafe_b64encode(force_bytes(user.pk)).decode().rstrip("=")
                )
                combined_token = f"{uidb64}:{token}"

                frontend_url = getattr(
                    settings, "FRONTEND_URL", "http://localhost:3000"
                )
                reset_link = f"{frontend_url}/reset-password?token={combined_token}"

                context = {
                    "user": user,
                    "reset_url": reset_link,
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
                        [email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except TemplateDoesNotExist:
                    send_mail(
                        subject=subject,
                        message=f"Password reset link: {reset_link}",
                        from_email=from_email,
                        recipient_list=[email],
                    )

                logger.info("AUDIT: Password reset requested for user_id=%s", user.pk)
            except User.DoesNotExist:
                logger.info("Password reset requested for non-existing email.")

            return Response(
                {
                    "detail": "If this email exists, a password reset link has been sent."
                },
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
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
