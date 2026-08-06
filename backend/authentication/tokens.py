from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing

TOKEN_SALT = "authentication.email-verification"

DEFAULT_MAX_AGE = 60 * 60 * 24


def _signer() -> signing.TimestampSigner:
    return signing.TimestampSigner(salt=TOKEN_SALT)


def generate_verification_token(user) -> str:
    payload = {"uid": str(user.pk), "email": user.email}
    return _signer().sign_object(payload)


def get_max_age() -> int:
    value = getattr(settings, "EMAIL_VERIFICATION_TOKEN_MAX_AGE", None)
    if value is None:
        return DEFAULT_MAX_AGE
    try:
        parsed_value = int(value)
        if parsed_value <= 0:
            return DEFAULT_MAX_AGE
        return parsed_value
    except (TypeError, ValueError):
        return DEFAULT_MAX_AGE


def verify_verification_token(token: str, max_age: int | None = None):
    User = get_user_model()
    max_age = get_max_age() if max_age is None else max_age

    try:
        payload = _signer().unsign_object(token, max_age=max_age)
    except (signing.BadSignature, signing.SignatureExpired):
        return None

    try:
        return User.objects.get(pk=payload["uid"], email=payload["email"])
    except (User.DoesNotExist, KeyError, ValueError):
        return None
