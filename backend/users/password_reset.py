import hashlib
import hmac
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from .models import PasswordResetAuditEvent, PasswordResetToken

logger = logging.getLogger(__name__)


class PasswordResetLifecycleError(Exception):
    """Raised when a reset token cannot be used."""

    def __init__(self, event_type, message="Invalid or expired token."):
        super().__init__(message)
        self.event_type = event_type


def hash_reset_token(raw_token):
    """Return a keyed digest suitable for persistent token lookup."""

    return hmac.new(
        str(settings.SECRET_KEY).encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def request_metadata(request):
    """Extract only the non-sensitive request metadata allowed for audit."""

    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return {
        "ip_address": request.META.get("REMOTE_ADDR"),
        "user_agent": user_agent.replace("\r", " ").replace("\n", " ")[:512],
    }


def _audit_event(user, event_type, result, metadata):
    event = PasswordResetAuditEvent.objects.create(
        user=user,
        event_type=event_type,
        result=result,
        ip_address=metadata.get("ip_address"),
        user_agent=metadata.get("user_agent", "")[:512],
    )
    logger.info(
        "password_reset_event",
        extra={
            "event_type": event_type,
            "result": result,
            "user_id": str(user.pk) if user is not None else None,
            "ip_address": metadata.get("ip_address"),
            "user_agent": metadata.get("user_agent", "")[:512],
        },
    )
    return event


def record_password_reset_event(user, event_type, result, metadata=None):
    """Persist one redacted audit and monitoring event."""

    with transaction.atomic():
        return _audit_event(user, event_type, result, metadata or {})


def issue_reset_token(user, raw_token, metadata=None, now=None):
    """Persist an issuance record without persisting the raw token."""

    metadata = metadata or {}
    now = now or timezone.now()
    expires_at = now + timedelta(
        seconds=getattr(settings, "PASSWORD_RESET_TIMEOUT", 3600)
    )

    with transaction.atomic():
        record = PasswordResetToken.objects.create(
            user=user,
            token_hash=hash_reset_token(raw_token),
            expires_at=expires_at,
        )
        _audit_event(
            user,
            PasswordResetAuditEvent.EventType.ISSUED,
            PasswordResetAuditEvent.Result.SUCCESS,
            metadata,
        )
    return record


def _failure_event_type(records, now):
    if records and all(record.revoked_at is not None for record in records):
        return PasswordResetAuditEvent.EventType.REVOKED
    if records and all(record.used_at is not None for record in records):
        return PasswordResetAuditEvent.EventType.REUSED
    if records and all(record.expires_at <= now for record in records):
        return PasswordResetAuditEvent.EventType.EXPIRED
    return PasswordResetAuditEvent.EventType.FAILED


def _invalidate_refresh_tokens(user):
    for outstanding_token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding_token)


def _invalidate_sessions(user, now):
    user_id = str(user.pk)
    for session in Session.objects.filter(expire_date__gt=now):
        if session.get_decoded().get("_auth_user_id") == user_id:
            session.delete()


def _complete_password_reset(user, raw_token, password, metadata, now):
    token_hash = hash_reset_token(raw_token)
    records = list(
        PasswordResetToken.objects.select_for_update().filter(
            user=user,
            token_hash=token_hash,
        )
    )

    if not records:
        raise PasswordResetLifecycleError(PasswordResetAuditEvent.EventType.FAILED)

    available_records = [
        record
        for record in records
        if record.used_at is None
        and record.revoked_at is None
        and record.expires_at > now
    ]
    if not available_records:
        raise PasswordResetLifecycleError(_failure_event_type(records, now))

    if not default_token_generator.check_token(user, raw_token):
        raise PasswordResetLifecycleError(PasswordResetAuditEvent.EventType.FAILED)

    user.set_password(password)
    user.save(update_fields=["password", "updated_at"])

    PasswordResetToken.objects.filter(
        user=user,
        token_hash=token_hash,
        used_at__isnull=True,
        revoked_at__isnull=True,
    ).update(used_at=now)

    _invalidate_refresh_tokens(user)
    _invalidate_sessions(user, now)
    _audit_event(
        user,
        PasswordResetAuditEvent.EventType.CONFIRMED,
        PasswordResetAuditEvent.Result.SUCCESS,
        metadata,
    )
    return user


def complete_password_reset(user, raw_token, password, metadata=None, now=None):
    """Atomically validate, consume, and complete a password reset."""

    metadata = metadata or {}
    now = now or timezone.now()
    try:
        with transaction.atomic():
            return _complete_password_reset(
                user,
                raw_token,
                password,
                metadata,
                now,
            )
    except PasswordResetLifecycleError as error:
        _audit_event(
            user,
            error.event_type,
            PasswordResetAuditEvent.Result.FAILURE,
            metadata,
        )
        raise


def revoke_reset_token(record_id, metadata=None, now=None):
    """Revoke one outstanding reset record without exposing its token."""

    metadata = metadata or {}
    now = now or timezone.now()
    with transaction.atomic():
        record = PasswordResetToken.objects.select_for_update().get(pk=record_id)
        if record.used_at is not None or record.revoked_at is not None:
            return False
        equivalent_records = PasswordResetToken.objects.select_for_update().filter(
            user=record.user,
            token_hash=record.token_hash,
            used_at__isnull=True,
            revoked_at__isnull=True,
        )
        equivalent_records.update(revoked_at=now)
        _audit_event(
            record.user,
            PasswordResetAuditEvent.EventType.REVOKED,
            PasswordResetAuditEvent.Result.SUCCESS,
            metadata,
        )
    return True
