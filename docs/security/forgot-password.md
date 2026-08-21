# Password reset security and operations

## Controls

- Requests return the same success response for known and unknown valid email
  addresses. No reset email is sent for an unknown or inactive account.
- Django's `default_token_generator` is used with `PASSWORD_RESET_TIMEOUT=3600`
  (one hour). A stateful `PasswordResetToken` stores only an HMAC hash,
  timestamps, and lifecycle state. Duplicate Django token hashes are allowed;
  confirmation consumes all equivalent outstanding records atomically.
- Tokens are single-use, expire, and can be revoked from Django admin. Password
  reset invalidates outstanding SimpleJWT refresh tokens and Django sessions.
- Audit events contain only user id when known, IP, user agent, timestamp,
  event type, and result. Passwords, raw tokens, reset URLs, and credentials
  must never be logged or stored.
- Reset requests are limited to 5/minute per IP and 5/hour per normalized
  email. Confirmation attempts are limited to 5/minute per IP.

## Deployment configuration

Set `SECRET_KEY`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`,
`DEFAULT_FROM_EMAIL`, and optionally `DEFAULT_REPLY_TO` through deployment
secrets/environment configuration. Development uses Django's console email
backend. Staging should use SMTP or an SES-compatible backend with provider
credentials supplied only by the secret manager; never commit them.

The frontend origin must be explicitly listed in `CORS_ALLOWED_ORIGINS`; do
not use a wildcard with authenticated APIs. Reset requests use an Authorization-
free endpoint and the browser does not store the reset token in localStorage,
sessionStorage, cookies, or application state beyond the current form submit.

If cookie authentication is introduced, keep cookies `Secure`, `HttpOnly`, and
appropriate `SameSite`, enforce Django CSRF tokens on state-changing requests,
and restrict trusted origins. Current reset endpoints do not use auth cookies.

## Monitoring and incident response

Monitor `password_reset_event` audit events for issued, confirmed, failed,
expired, reused, and revoked operations. Alert on spikes in issuance, repeated
failed confirmations, reuse attempts, or sustained 429 responses. To respond
to suspected abuse, revoke outstanding tokens for the affected users in admin,
review provider delivery logs without exposing URLs, and rotate provider
credentials if compromise is suspected. Preserve only the non-sensitive audit
metadata needed for investigation.
