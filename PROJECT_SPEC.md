# PROJECT_SPEC.md

# Forgot Password / Reset Flow (Desktop)

**Scope:** тільки епік `Forgot Password / Reset Flow (Desktop)`  
**Source:** `issues4847.json`  
**Status:** Open

---

## 1. Purpose

Implement the full desktop **Forgot Password / Password Reset** experience from the project mockups.

The flow must cover:

1. Requesting a password reset by email.
2. Sending a reset email containing a time-limited token/link.
3. Opening the desktop “Set new password” page from the link.
4. Setting a new password.
5. Handling invalid, expired and other error states.
6. Resend/reset-email UX.
7. Secure token handling, rate limiting, anti-enumeration, logging and auditability.
8. Automated unit, E2E and accessibility testing.

The scope is limited to this password-reset epic and does not include the other authentication epics.

---

# 2. Scope

## 2.1 In Scope

### Frontend

- Desktop Password Reset Request page.
- Desktop Password Reset Confirm page.
- Client-side validation.
- Loading, success and error states.
- Token and `uid` parsing from URL.
- Deep-link handling.
- Password strength hints.
- Password confirmation.
- Invalid/expired token UX.
- Resend reset email action.
- Success confirmation and redirect/link to login.
- Accessibility markup and announcements.
- Frontend unit tests.
- E2E tests.

### Backend

- Password reset request endpoint.
- Password reset confirm endpoint.
- Secure, time-limited reset tokens.
- Token lifecycle / revocation support.
- Single-use token enforcement.
- Rate limiting.
- Anti-account-enumeration behavior.
- Password complexity validation.
- Password update.
- Refresh-token/session invalidation where applicable.
- Audit logging.
- Email templates and email delivery integration.
- Monitoring recommendations.
- Unit tests.

### Email

- HTML reset email.
- Plain-text fallback.
- Reset link.
- Configurable sender/reply-to.
- Local console backend.
- Staging provider integration such as SMTP/SES.
- Testable email rendering.

### QA / Security

- E2E happy path.
- Invalid-token scenario.
- Expired-token scenario.
- Throttle/429 scenario.
- Accessibility checks.
- Security checklist.
- CORS/CSRF guidance where applicable.
- Token/log redaction guidance.
- Production email-provider configuration guidance.

---

## 2.2 Out of Scope

The following are not part of this specification:

- General login implementation.
- Registration.
- Email verification.
- Protected routes.
- General user profile functionality.
- Saved lists.
- Landing page.
- Project management.
- Search.
- Other authentication flows except where the password-reset flow must interact with them.

---

# 3. Epic Description

Implement the full desktop “Forgot password” experience from the mockups:

- request reset;
- email with token/link;
- set new password;
- resend;
- error states.

Backend must provide:

- secure token handling;
- rate limiting;
- logging;
- email templates.

Frontend must provide:

- desktop pages;
- client-side validation;
- graceful UX for edge states.

---

# 4. Epic-Level Acceptance Criteria

The epic is complete when all of the following are satisfied:

- Desktop “Forgot password” request page exists and matches the required mockup states.
- Desktop “Set new password” page exists and matches the required mockup states.
- Required backend endpoints exist, are documented and covered by unit tests.
- Request, confirm, token handling and resend behavior work.
- Rate limiting and anti-enumeration protections are implemented.
- E2E tests cover the main happy path and at least two error scenarios.
- E2E tests run in CI.
- Email templates exist and are testable locally and in staging.
- Accessibility checks produce no critical failures.
- Security requirements and production configuration guidance are documented.

---

# 5. User Flow

## 5.1 Request Password Reset

```text
User
  |
  | opens /forgot-password
  v
Password Reset Request Page
  |
  | enters email
  v
Client-side validation
  |
  | valid
  v
POST /api/auth/password-reset/
  |
  +-----------------------------+
  |                             |
  | known email                 | unknown email
  v                             v
send reset email              do not reveal
  |                             |
  +-------------+---------------+
                |
                v
       Show generic success
       message to the user
```

The UI must not reveal whether the submitted email belongs to an existing account.

---

## 5.2 Follow Reset Link

```text
Reset Email
    |
    | click reset link
    v
/reset-password/?uid=...&token=...
    |
    v
Parse uid/token
    |
    v
Set New Password page
```

The token should be applied from the URL. The reset form should focus the new-password input.

---

## 5.3 Set New Password

```text
User enters:
- New password
- Confirm password
        |
        v
Client-side validation
        |
        v
POST /api/auth/password-reset/confirm/
        |
    +---+---------------------+
    |                         |
  valid                 invalid/expired
    |                         |
    v                         v
Change password        Show friendly error
    |                  + Resend reset email
    v
Success confirmation
    |
    v
Login link / optional
configurable redirect
```

---

# 6. Frontend Specification

## 6.1 Password Reset Request Page

### Route

```text
/forgot-password
```

### Component

```text
PasswordResetRequest
```

### Required UI States

- Idle.
- Invalid email.
- Loading/submitting.
- Generic success.
- Rate-limit error (`429`).
- Generic server error.

### Form

Input:

```text
email
```

Client-side validation:

- required;
- valid email format.

### Submit

```http
POST /api/auth/password-reset/
```

The success UI must be shown regardless of whether the submitted email belongs to an existing account.

### Accessibility

- Proper form labels.
- Keyboard accessibility.
- `aria-live` for success/error messages.

### Tests

React Testing Library tests for:

- invalid email;
- prevention of API call for invalid input;
- successful submission;
- success-message rendering;
- rate-limit/error state.

---

# 7. Password Reset Confirm Page

## 7.1 Route

```text
/reset-password/?token=xxx&uid=...
```

Hash-based token input may also be supported as described in the issue.

## 7.2 Component

```text
PasswordResetConfirm
```

## 7.3 Token Handling

The page must:

- parse `token`;
- parse `uid`;
- support a manual paste fallback if required;
- keep token handling out of visible password fields;
- focus the new-password field when the reset link is opened.

## 7.4 Form

Fields:

```text
New password
Confirm password
```

## 7.5 Client Validation

Validate:

- required password;
- password strength/complexity;
- confirmation password matches;
- minimum length;
- mixed-character/password-strength requirements described by the issue.

## 7.6 Confirm API

```http
POST /api/auth/password-reset/confirm/
```

Request:

```json
{
  "uid": "encoded_user_id",
  "token": "token_string",
  "password": "NewP@ssw0rd!"
}
```

Expected responses from the issue:

### Success

```http
200 OK
```

```json
{
  "detail": "Password changed successfully."
}
```

### Invalid / expired token

```http
400 Bad Request
```

```json
{
  "detail": "Invalid or expired token."
}
```

### Weak password

```http
422 Unprocessable Entity
```

```json
{
  "password": [
    "Password too weak."
  ]
}
```

## 7.7 Success State

After successful reset:

- display confirmation;
- provide a link to `/login`;
- optionally auto-redirect to `/login` after a configurable number of seconds;
- allow the user to navigate/cancel the redirect manually.

## 7.8 Invalid / Expired Token State

Display:

- clear, non-sensitive error;
- explanation that the reset link is no longer valid;
- CTA to request a new reset email.

The resend action should open `/forgot-password` and pre-fill the email when it is safely available.

## 7.9 Accessibility

- Semantic labels.
- Keyboard navigation.
- `aria-live` announcements for success and server errors.
- Visible focus behavior.

## 7.10 Tests

Unit tests must cover:

- URL token parsing;
- `uid` parsing;
- validation;
- success state;
- invalid token;
- expired token;
- weak password;
- redirect behavior;
- resend behavior.

---

# 8. Backend API Specification

## 8.1 Request Reset

### Endpoint

```http
POST /api/auth/password-reset/
```

### Request

```json
{
  "email": "user@example.com"
}
```

### Response

```http
200 OK
```

```json
{
  "detail": "If the email exists, you will receive reset instructions."
}
```

### Security Requirement

The endpoint must always return a success response for valid request syntax, regardless of whether the email exists.

This prevents account enumeration.

### Required Behavior

For a known user:

1. Generate a secure, time-limited reset token.
2. Record minimal token issuance metadata for monitoring/revocation.
3. Send the reset email.
4. Return the same generic success response.

For an unknown user:

1. Do not send an email.
2. Return the same generic success response.

### Token

The source suggests:

- Django `PasswordResetTokenGenerator`; or
- signed token with a short TTL.

The token should expire, with the issue giving approximately **1 hour** as an example.

### Rate Limiting

Throttle by:

- IP;
- email.

The issue gives approximately:

```text
5 requests per hour
```

as an example policy.

---

# 9. Password Reset Confirm API

### Endpoint

```http
POST /api/auth/password-reset/confirm/
```

### Request

```json
{
  "uid": "encoded_user_id",
  "token": "token_string",
  "password": "NewP@ssw0rd!"
}
```

### Required Behavior

1. Validate `uid` and token.
2. Check token expiry.
3. Check token has not already been used.
4. Check token has not been revoked.
5. Validate password complexity server-side.
6. Set the new password.
7. Revoke/rotate refresh tokens or active sessions where applicable.
8. Mark the reset token as used.
9. Create an audit-log entry.
10. Return a non-sensitive response.

### Rate Limiting

Confirm attempts must be rate-limited to reduce token brute-force attempts.

### Acceptance

Valid token + strong password:

```text
200
Password changed
User can log in with new password
```

Invalid/expired/used token:

```text
400
No password change
```

---

# 10. Token Lifecycle

The implementation must support:

- expiration;
- single-use;
- revocation;
- auditability;
- monitoring.

The source allows two implementation approaches:

### Stateful

A `PasswordResetToken` model may contain:

```text
user
token_hash
created_at
expires_at
used_at
revoked
```

### Stateless

If signed/stateless tokens are used:

- record issuance events;
- use a unique nonce;
- check the nonce during confirmation;
- prevent token reuse.

### Required Acceptance

- Token works once.
- Second use fails.
- Revoked token fails.
- Expired token fails.
- Admin can inspect/revoke outstanding tokens.
- Lifecycle tests exist.

---

# 11. Email Specification

## 11.1 Templates

Create:

- HTML email;
- plain-text fallback.

The email must contain:

- clear reset CTA;
- reset link;
- user name where available;
- expiry duration.

Template context:

```text
user_name
reset_link
expiry_minutes
```

## 11.2 Configuration

Support:

```text
EMAIL_BACKEND
sender
reply-to
template variables
```

## 11.3 Environments

### Development

Use a console email backend so developers can inspect the email locally.

### Staging

Support a configured provider such as:

- SMTP;
- SES.

Provider credentials must come from environment configuration/secrets.

## 11.4 Email Tests

Verify:

- HTML rendering;
- plain-text rendering;
- reset link;
- token presence;
- template context.

---

# 12. Security Requirements

## 12.1 Anti-Enumeration

`POST /api/auth/password-reset/` must not reveal whether an email exists.

Both known and unknown emails receive the same success response.

## 12.2 Token Security

Tokens must be:

- secure;
- time-limited;
- single-use;
- revocable;
- protected from reuse.

## 12.3 Logging

Do not expose sensitive reset tokens in logs.

Reset operations must be auditable.

Audit information described in the source includes:

```text
user_id
IP
user_agent
timestamp
```

## 12.4 CSRF

If cookies are used for authentication/token handling, document and apply appropriate CSRF protections, including the relevant `SameSite` and `HttpOnly` settings.

## 12.5 CORS

Document allowed CORS origins and ensure authentication endpoints allow only the intended frontend origin.

## 12.6 Email Security

Consider XSS-safe email rendering and secure provider configuration.

---

# 13. Monitoring

The implementation should provide monitoring/metrics for:

- reset requests;
- reset confirmations;
- expired-token attempts;
- token-reuse attempts;
- elevated reset request volume;
- failed confirmation attempts.

Security guidance should recommend alerts for suspicious activity.

---

# 14. QA and E2E

## 14.1 Main E2E Flow

Test:

```text
Request reset
    ↓
Capture/intercept email
    ↓
Extract reset token
    ↓
Open reset URL
    ↓
Set new password
    ↓
Login using new password
```

## 14.2 Error Scenarios

At minimum:

1. Invalid token.
2. Expired token.
3. Rate-limited request (`429`).

The issue also requires coverage for accessibility.

## 14.3 Accessibility

Use:

- axe; or
- Lighthouse.

Check both reset pages.

Critical accessibility failures must be fixed.

## 14.4 CI

E2E tests must run in CI for PRs affecting authentication.

## 14.5 QA Documentation

The source specifies:

```text
docs/qa/forgot-password.md
```

The document should contain:

- test steps;
- screenshots;
- test results.

---

# 15. Security Documentation

The source specifies:

```text
docs/security/forgot-password.md
```

It must contain:

- anti-enumeration checklist;
- token expiry/single-use requirements;
- CORS configuration;
- CSRF guidance when cookies are used;
- token/log redaction guidance;
- email-provider configuration;
- production secrets guidance;
- token TTL;
- monitoring/alerting recommendations.

---

# 16. Architecture

The issue set describes a React frontend and Django/DRF-style backend.

High-level flow:

```text
┌───────────────────────────┐
│       React Desktop       │
│                           │
│ /forgot-password          │
│ /reset-password/          │
└─────────────┬─────────────┘
              │
              │ HTTP API
              ▼
┌───────────────────────────┐
│       Django / DRF        │
│                           │
│ password-reset/           │
│ password-reset/confirm/   │
│ token lifecycle           │
│ rate limiting             │
│ audit logging             │
└───────┬───────────┬───────┘
        │           │
        ▼           ▼
   User/Token      Email
   data            service
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Console/dev       SMTP/SES
```

The source does not prescribe a final database/token architecture beyond the stateful/stateless options described above. The implementation choice must be documented.

---

# 17. Dependencies

The reset flow depends on existing authentication/user infrastructure for:

- user accounts;
- password storage;
- login;
- refresh/session handling where applicable;
- email delivery configuration.

The reset flow itself must not expand into implementation of unrelated authentication features.

---

# 18. Definition of Done

The epic is considered done only when:

### Frontend

- [ ] `/forgot-password` implemented.
- [ ] `/reset-password/` implemented.
- [ ] Desktop UI states implemented.
- [ ] Client validation implemented.
- [ ] Token deep-link handling implemented.
- [ ] Resend UX implemented.
- [ ] Success/redirect behavior implemented.
- [ ] Accessibility requirements implemented.
- [ ] Frontend unit tests pass.

### Backend

- [ ] `POST /api/auth/password-reset/` implemented.
- [ ] `POST /api/auth/password-reset/confirm/` implemented.
- [ ] Anti-enumeration implemented.
- [ ] Token expiry implemented.
- [ ] Single-use implemented.
- [ ] Revocation implemented.
- [ ] Rate limiting implemented.
- [ ] Password complexity enforced server-side.
- [ ] Password update implemented.
- [ ] Relevant sessions/refresh tokens revoked where applicable.
- [ ] Audit logging implemented.
- [ ] Backend unit tests pass.

### Email

- [ ] HTML template implemented.
- [ ] Plain-text template implemented.
- [ ] Console/dev delivery works.
- [ ] Staging provider configuration supported.
- [ ] Email template tests pass.

### QA / Security

- [ ] E2E happy path passes.
- [ ] Invalid-token E2E passes.
- [ ] Expired-token E2E passes.
- [ ] Throttle scenario is tested.
- [ ] Accessibility scan has no critical failures.
- [ ] E2E runs in CI.
- [ ] `docs/qa/forgot-password.md` exists.
- [ ] `docs/security/forgot-password.md` exists.

---

# 19. Source Traceability

This specification was created only from the relevant `Forgot Password / Reset Flow (Desktop)` epic and its associated `forgot password` tasks in `issues4847.json`.

Relevant source items include:

- `Forgot Password / Reset Flow (Desktop)` — epic.
- `Frontend: Password Reset Request Page (desktop) — UI + client validation`.
- `Frontend: Reset Confirm Page (desktop) — set new password UI & token handling`.
- `Frontend: UX details — deep-link behavior, auto-redirects & friendly copy`.
- `Backend: Password reset request endpoint POST /api/auth/password-reset/`.
- `Backend: Password reset confirm endpoint POST /api/auth/password-reset/confirm/`.
- `Backend: Email templates & delivery integration (dev & staging)`.
- `Backend: Token lifecycle, revocation and monitoring`.
- `Security review & docs: anti-enumeration, CSRF, CORS, token storage guidance`.
- `QA & E2E: End-to-end tests and accessibility for forgot/reset flows`.

No requirements from unrelated epics are intentionally included.
