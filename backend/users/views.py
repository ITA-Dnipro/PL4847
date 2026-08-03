import base64
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class PasswordResetThrottle(AnonRateThrottle):
    rate = "5/min"


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
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
                    combined_token = f"{uidb64}:{token}"

                    frontend_url = getattr(
                        settings, "FRONTEND_URL", "http://localhost:3000"
                    )
                    reset_url = (
                        f"{frontend_url}/password-reset/confirm?token={combined_token}"
                    )

                    context = {"user": user, "reset_url": reset_url}
                    subject = "Скидання пароля"
                    text_content = render_to_string(
                        "emails/password_reset_email.txt", context
                    )
                    html_content = render_to_string(
                        "emails/password_reset_email.html", context
                    )

                    from_email = getattr(
                        settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost"
                    )
                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, [user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send()
                        logger.info(
                            f"AUDIT: Password reset email sent for user ID: {user.pk}"
                        )
                    except Exception:

                        logger.exception(
                            f"AUDIT: Failed to send password reset email for user ID: {user.pk}"
                        )
                except Exception:
                    logger.exception(
                        f"AUDIT: Unexpected error processing password reset for email: {email}"
                    )
            else:
                logger.info(
                    f"AUDIT: Password reset requested for non-existent email: {email}"
                )

            return Response(
                {
                    "message": "If an account with that email exists, password reset instructions have been sent."
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            password = serializer.validated_data["password"]

            user.set_password(password)
            user.save()

            logger.info(
                f"AUDIT: Password reset successfully completed for user ID: {user.pk}"
            )
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
