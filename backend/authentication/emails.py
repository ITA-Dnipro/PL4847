import logging
from django.conf import settings
from django.core.mail import send_mail

from .tokens import generate_verification_token, get_max_age

logger = logging.getLogger(__name__)

def build_verification_url(token: str) -> str:
    frontend_url = getattr(settings, "FRONTEND_URL", "").rstrip("/")
    path = getattr(settings, "EMAIL_VERIFICATION_PATH", "/verify-email")
    return f"{frontend_url}{path}?token={token}"


def send_verification_email(user):
    token = generate_verification_token(user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    max_age = get_max_age()
    if max_age < 3600:
        minutes = max_age // 60
        duration = f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = max_age // 3600
        duration = f"{hours} hour{'s' if hours != 1 else ''}"

    subject = "Verify your email"
    message = f"Please verify your email using the following link. This link will expire in {duration}:\n\n{verify_url}"
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("SMTP delivery failed for email %s", user.email)
        raise