<<<<<<< HEAD
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
=======
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
>>>>>>> 256fc30d6dce87d032c70a51314edeae2577dec4

from .emails import send_verification_email
from .tokens import verify_verification_token

<<<<<<< HEAD
=======
logger = logging.getLogger(__name__)

>>>>>>> 256fc30d6dce87d032c70a51314edeae2577dec4
User = get_user_model()


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get("token")
        if not isinstance(token, str) or not token:
            return Response(
                {"detail": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verify_verification_token(token)
        if user is None:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        return Response({"detail": "Email verified."}, status=status.HTTP_200_OK)


class ResendVerificationView(APIView):

    permission_classes = (AllowAny,)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "resend"

    def post(self, request):
        email = request.data.get("email")

        if email:
            user = User.objects.filter(email__iexact=email).first()
            if user is not None and not user.is_active:

                def _send_email_safely():
                    try:
                        send_verification_email(user)
                    except Exception:
                        logger.exception(
                            "Failed to send verification email to user ID %s", user.pk
                        )

                transaction.on_commit(_send_email_safely)

        return Response(status=status.HTTP_200_OK)
