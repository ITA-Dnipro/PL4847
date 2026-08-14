import base64
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class PasswordResetThrottle(AnonRateThrottle):
    scope = "password_reset"
    rate = "5/min"


class PasswordResetRequestThrottle(AnonRateThrottle):
    scope = "password_reset_request"
    rate = "5/min"


class PasswordResetConfirmThrottle(AnonRateThrottle):
    scope = "password_reset_confirm"
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

            user = User.objects.filter(email__iexact=email, is_active=True).first()

            if user:
                try:
                    uidb64 = (
                        base64.urlsafe_b64encode(force_bytes(user.pk))
                        .decode()
                        .rstrip("=")
                    )
                    token = default_token_generator.make_token(user)

                    frontend_url = getattr(
                        settings, "FRONTEND_URL", "http://localhost:5173"
                    )
                    reset_url = f"{frontend_url}/password-reset/confirm?uid={uidb64}&token={token}"

                    context = {"user": user, "reset_url": reset_url}
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
                            subject, text_content, from_email, [user.email]
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
                {
                    "message": "If an account with that email exists, password reset instructions have been sent."
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

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            if "password" in errors:
                return Response(
                    {"password": errors["password"]},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user = serializer.validated_data["user"]
            password = serializer.validated_data["password"]

            with transaction.atomic():
                user.set_password(password)
                user.save()

                for outstanding_token in OutstandingToken.objects.filter(user=user):
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)

            user_ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT")

            logger.info(
                "AUDIT: Password reset successfully completed for user ID: %s, IP: %s, UA: %s",
                user.pk,
                user_ip_address,
                user_agent,
            )
            return Response(
                {"detail": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.prefetch_related("tags")
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "id"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        is_owner = self.request.user.is_authenticated and obj.id == self.request.user.id
        if not obj.is_active_profile and not is_owner:
            raise Http404

        self.check_object_permissions(self.request, obj)
        return obj
