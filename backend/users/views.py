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
from rest_framework.views import APIView

from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email__iexact=email, is_active=True)
                uidb64 = (
                    base64.urlsafe_b64encode(force_bytes(user.pk)).decode().rstrip("=")
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
                msg.send()

                logger.info(
                    f"AUDIT: Password reset email requested and sent for email: {email}"
                )
            except User.DoesNotExist:
                # Захист від Account Enumeration: якщо email відсутній у системі,
                # повертаємо 200 OK з абстрактним повідомленням.
                logger.info(
                    f"AUDIT: Password reset requested for non-existent email: {email}"
                )

        return Response(
            {
                "detail": "If an account with this email exists, a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
