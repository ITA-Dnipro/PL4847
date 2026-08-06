from django.conf import settings
from django.core.mail import send_mail

from .tokens import generate_verification_token, get_max_age


def build_verification_url(token: str) -> str:
    frontend_url = getattr(settings, "FRONTEND_URL", "").rstrip("/")
    path = getattr(settings, "EMAIL_VERIFICATION_PATH", "/verify-email")
    return f"{frontend_url}{path}?token={token}"


def send_verification_email(user) -> None:
    token = generate_verification_token(user)
    verification_url = build_verification_url(token)
    hours = max(get_max_age() // 3600, 1)

    subject = "Confirm your email address"
    message = (
        f"Hi {user.username},\n\n"
        "Please confirm your email address by opening the link below:\n"
        f"{verification_url}\n\n"
        f"This link expires in {hours} hour(s).\n"
        "If you didn't create an account, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )