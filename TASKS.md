# Epic #30 — Forgot Password / Reset Flow (Desktop): Task Breakdown

## 1. Epic overview

Deliver the desktop password-reset flow defined in `PROJECT_SPEC.md`:

1. A user requests reset instructions at `/forgot-password`.
2. The backend returns the same generic success response for known and unknown
   valid emails and sends a time-limited reset link only for an eligible user.
3. The email opens `/reset-password/?uid=...&token=...`.
4. The user sets and confirms a strong new password.
5. The system handles invalid, expired, reused, revoked, throttled, and other
   error states without exposing sensitive information.
6. The implementation is secure, tested, accessible, documented, and covered
   in CI.

Scope is limited to this epic. General login, registration, and email
verification are not implementation tasks unless directly required to validate
the reset integration.

## 2. Current implementation baseline

### Reusable existing functionality

| Area | Existing files/modules | Current behavior that can be reused |
|---|---|---|
| API routing | `backend/users/urls.py`, `backend/project/urls.py` | Both reset endpoints are already exposed as `/api/auth/password-reset/` and `/api/auth/password-reset/confirm/`. |
| Request API | `backend/users/views.py`, `backend/users/serializers.py` | Validates email; for active known users creates a Django `default_token_generator` token and sends email; valid known and unknown emails receive HTTP 200. |
| Confirm API | `backend/users/views.py`, `backend/users/serializers.py` | Validates a Django reset token, uses Django password validators, calls `set_password()`, and returns HTTP 200 on success. |
| Basic IP throttle | `PasswordResetRequestThrottle`, `PasswordResetConfirmThrottle` in `backend/users/views.py` | Both APIs currently use `AnonRateThrottle` at `5/min`. |
| Email delivery | `backend/users/templates/emails/password_reset_email.{html,txt}`, `backend/project/settings/base.py`, `backend/.env.example` | HTML/text email templates, console mail backend default, and SMTP-style environment settings already exist. |
| JWT/logout infrastructure | `backend/project/settings/base.py`, `backend/users/views.py` | SimpleJWT token blacklist app is installed and the existing logout view blacklists a supplied refresh token. |
| Backend tests | `backend/tests/test_password_reset.py` | Covers known/unknown request response status, email dispatch, successful confirmation, and invalid token. |
| Frontend foundation | `frontend/src/main.jsx`, `frontend/src/App.jsx`, `frontend/vite.config.js`, `frontend/src/setupTests.js` | React Router, Vite `/api` proxy, Vitest/jsdom, and Testing Library setup are present. |

### Gaps requiring work

- The email currently creates `/password-reset/confirm?token=<uidb64>:<token>`;
  the approved epic contract requires `/reset-password/?uid=...&token=...`.
- Confirm currently accepts a combined token field rather than separate `uid`
  and `token` fields; response keys/messages and weak-password status do not
  match `PROJECT_SPEC.md`.
- There is no explicit reset-token TTL configuration, persistent lifecycle
  record, revocation, admin inspection/revocation, issuance audit event, or
  monitoring metric.
- The existing throttle is IP-only and `5/min`; no per-email throttle or
  documented reset policy exists.
- Refresh-token invalidation after reset is not implemented.
- Templates do not receive the specified `user_name`, `reset_link`, and
  `expiry_minutes` context; reply-to and provider guidance/tests are absent.
- No reset frontend routes/components/tests exist. `Login.jsx` is a placeholder.
- There are no reset E2E tests, accessibility scans, reset QA/security docs, or
  CI execution for frontend tests/E2E.

## 3. Backend tasks — Коля

### K-01 — Align and complete the reset API contract

**Owner:** Коля — Backend Developer

**Description:** Bring the existing request and confirm APIs into alignment with
the API contract in `PROJECT_SPEC.md` without creating unrelated auth endpoints.

**Reason / specification relation:** Sections 8 and 9 require the documented
request/confirm payloads, response bodies, status behavior, and non-sensitive
error handling. The current confirm payload/link format differs from that
contract.

**Existing code to reuse or modify:** `backend/users/urls.py`,
`backend/users/views.py`, `backend/users/serializers.py`,
`backend/tests/test_password_reset.py`.

**Scope:** Extend the existing request/confirm views and serializers; do not
create unrelated authentication endpoints.

**Work:**

- Retain the existing endpoint paths.
- Make request success conform to the specified generic HTTP 200 `detail`
  response for every syntactically valid email, whether or not the account
  exists.
- Make confirm accept the specified separate `uid`, `token`, and `password`
  payload and return the specified non-sensitive success and invalid/expired
  responses.
- Return server-side password validation in the approved HTTP 400 DRF
  validation-error format.
- Update backend tests for the approved contract while retaining existing
  known/unknown behavior coverage.

**Acceptance criteria:**

- `POST /api/auth/password-reset/` accepts `{ "email": "user@example.com" }`
  and returns the same specified HTTP 200 response body for known and unknown
  valid emails.
- `POST /api/auth/password-reset/confirm/` accepts separate `uid`, `token`,
  and `password`; a valid payload changes the password and returns the
  specified HTTP 200 response.
- Invalid or expired credentials cause no password change and return a
  non-sensitive HTTP 400 response.
- Contract tests cover response bodies, status codes, and payload shape.

**Dependencies:** Resolved decisions Q-02 and Q-03.

**Testing expectations:** Add/adjust backend API tests for known/unknown valid
emails, request and confirm response bodies, separate `uid`/`token` payload,
valid reset, and invalid/expired token with no password change.

### K-02 — Implement reset-token lifecycle, security controls, and auditability

**Owner:** Коля — Backend Developer

**Description:** Add the lifecycle capability missing from the current Django
token-only implementation: one-hour expiry, token reuse prevention, revocation
support, durable auditability, admin inspection/revocation, monitoring events,
and post-reset session/refresh handling while keeping Django's default token
generator.

**Reason / specification relation:** Sections 9, 10, 12, and 13 require
expiry, reuse prevention, revocation, audit records, monitoring, and relevant
session/refresh invalidation. The current implementation has no lifecycle
record or revocation mechanism.

**Existing code to reuse or modify:** `backend/users/views.py`,
`backend/users/serializers.py`, `backend/users/models.py`,
`backend/users/admin.py`, `backend/project/settings/base.py`,
`backend/tests/test_password_reset.py`; existing SimpleJWT blacklist support.

**Scope:** Backend token persistence/generation/validation, migrations, admin,
audit events, settings, and backend tests.

**Work:**

- Keep Django `default_token_generator` and configure the approved one-hour
  token lifetime.
- Ensure issued tokens expire, are protected from reuse, and become invalid
  after the password changes.
- Record only non-sensitive issuance/confirmation/revocation audit metadata:
  user ID when known, IP, user agent, timestamp, and event type/result.
- Provide an admin view or management capability to inspect and revoke
  outstanding reset tokens, as required by the source task.
- Add monitoring counters/events for reset requests, confirmations, failed
  confirmations, expired tokens, and reuse attempts; document intended alerts.
- Invalidate relevant SimpleJWT refresh tokens and applicable sessions on a
  successful password reset.

**Acceptance criteria:**

- A valid reset token works before expiry; expired, reused, and revoked tokens
  fail with no password change.
- An administrator can inspect and revoke outstanding tokens.
- No raw password or reset token is stored in lifecycle/audit data or logs.
- Existing refresh tokens/sessions are handled according to the approved
  policy, with automated verification.
- Tests cover issue, expiry, first use, reuse, revocation, audit content,
  refresh/session invalidation, and monitoring events.

**Dependencies:** Resolved decisions Q-01 and Q-05; K-01 must consume the
approved token contract.

**Testing expectations:** Add lifecycle unit/integration tests for issuance,
expiry, first use, reused and revoked tokens, no sensitive audit/log data,
admin revocation, relevant session/refresh invalidation, and monitoring events.

### K-03 — Apply reset-specific anti-abuse throttling

**Owner:** Коля — Backend Developer

**Description:** Replace or extend the existing IP-only reset throttles with
the approved request and confirmation anti-abuse policy.

**Reason / specification relation:** Sections 8, 9, and 12 require throttling
by IP and email for reset requests and throttled confirmation attempts. Current
code only applies `AnonRateThrottle` at `5/min`.

**Existing code to reuse or modify:** `PasswordResetRequestThrottle`,
`PasswordResetConfirmThrottle`, and reset views in `backend/users/views.py`;
DRF throttle settings in `backend/project/settings/base.py`; reset tests.

**Scope:** Reset request and confirmation throttling only.

**Work:**

- Replace/extend the current IP-only `5/min` behavior with the approved
  per-IP `5/min` and per-email `5/hour` request throttling policy, and
  confirmation-attempt throttling at `5/min` per IP.
- Keep throttled responses non-sensitive and compatible with frontend 429 UX.
- Add deterministic automated tests for each throttle.

**Acceptance criteria:**

- Requests are throttled by both IP and email under the approved policy.
- Confirmation attempts are rate limited.
- A throttled call returns HTTP 429 without revealing account/token state.
- Tests demonstrate request and confirmation throttling.

**Dependencies:** Resolved decision Q-04; K-01 for consistent API error
behavior.

**Testing expectations:** Add deterministic tests for request per-IP and
per-email limits, confirm-attempt limit, HTTP 429, and non-enumerating/non-
sensitive throttle responses.

### K-04 — Complete reset email delivery, configuration, and tests

**Owner:** Коля — Backend Developer

**Description:** Complete the existing multipart reset email integration and
configuration around the approved reset-link contract.

**Reason / specification relation:** Section 11 requires both template formats,
specified rendering context, reset link, configurable sender/reply-to,
development console delivery, staging-provider support, and email tests.

**Existing code to reuse or modify:** `backend/users/views.py`,
`backend/users/templates/emails/password_reset_email.html`,
`backend/users/templates/emails/password_reset_email.txt`,
`backend/project/settings/base.py`, `backend/.env.example`, and
`backend/tests/test_password_reset.py`.

**Scope:** Existing reset email templates/service and email configuration.

**Work:**

- Reuse the existing HTML/text templates but update context to include
  `user_name`, `reset_link`, and `expiry_minutes`.
- Generate the approved frontend reset URL using separate `uid` and `token`.
- Keep console delivery for development; add/configure sender and reply-to;
  document environment-based SMTP/SES-compatible staging configuration without
  committing credentials.
- Add rendering tests for both parts, link/path/query values, token presence,
  expiry text, recipient, sender, and reply-to.
- Document local email inspection and provider configuration in the security
  documentation task.

**Acceptance criteria:**

- Both rendered formats have a clear reset CTA, working approved reset link,
  user name where available, and expiry duration.
- Console backend remains usable locally; staging provider configuration comes
  from environment variables/secrets.
- Sender and reply-to are configurable.
- Email rendering/delivery tests pass.

**Dependencies:** K-01 and K-02 for approved `uid`/`token` generation and
expiry; Resolved decision Q-01.

**Testing expectations:** Add tests that render HTML/text parts and verify
context values, approved URL/query format, token presence, expiry text,
recipient, configured sender/reply-to, and console-backend delivery.

### K-05 — Backend security and operations documentation

**Owner:** Коля — Backend Developer

**Description:** Create the reset-specific production/security guidance
required by the epic.

**Reason / specification relation:** Sections 12, 13, and 15 explicitly require
`docs/security/forgot-password.md` covering security decisions, deployment
configuration, monitoring, and alerts.

**Existing code to reuse or modify:** `backend/project/settings/base.py`,
`backend/project/settings/dev.py`, `backend/.env.example`, reset implementation
and audit/monitoring design produced by K-01 through K-04.

**Scope:** Create `docs/security/forgot-password.md`; no frontend production
code.

**Work:**

- Document the chosen token architecture/TTL, anti-enumeration behavior,
  revocation and single-use semantics, token/password log redaction,
  CORS allowed-origin configuration, CSRF guidance if cookies are used, secure
  email-provider secrets, monitoring/alert recommendations, and incident
  response guidance.

**Acceptance criteria:**

- `docs/security/forgot-password.md` exists and contains every item required
  by PROJECT_SPEC sections 12, 13, and 15.
- Its claims match the implemented backend settings and behavior.

**Dependencies:** K-01 through K-04 and Resolved decisions Q-01, Q-04, and
Q-05.

**Testing expectations:** Verify every documented setting and control against
the implemented configuration; Михайло independently checks the document in
Q-02.

### K-06 — Document the developer-facing reset API contract

**Owner:** Коля — Backend Developer

**Description:** Add the developer-facing API reference for the password-reset
flow so backend, frontend, and QA share one canonical contract.

**Reason / specification relation:** Section 8 and Section 9 require the
required backend endpoints to be documented, including request/response bodies,
errors, and the reset-link token format.

**Existing code to reuse or modify:** `backend/users/views.py`,
`backend/users/serializers.py`, `backend/users/urls.py`,
`backend/project/urls.py`, `backend/tests/test_password_reset.py`, and the
final backend behavior produced by K-01 through K-04.

**Scope:** Create `docs/api/forgot-password.md`; no production code.

**Work:**

- Document `POST /api/auth/password-reset/` and
  `POST /api/auth/password-reset/confirm/`.
- Document request/response payloads, HTTP 200 success, HTTP 400 validation
  behavior, HTTP 429 throttling behavior, and the `uid`/`token` URL format.
- Include the non-enumerating request behavior and the confirm error states
  expected by the approved contract.

**Acceptance criteria:**

- `docs/api/forgot-password.md` exists and documents both reset endpoints.
- The document matches the approved request/response formats and status
  behavior.
- The document covers `uid`/`token` reset-link format and the 400/429 cases.

**Dependencies:** K-01, K-03, and K-04.

**Testing expectations:** Review the document against the implemented backend
contract and the backend tests for the same endpoints.

## 4. Frontend tasks — Петро

### P-01 — Build the desktop password-reset request page

**Owner:** Петро — Frontend Developer

**Description:** Add the request-reset route and desktop UI with client
validation, endpoint integration, required states, accessibility, and tests.

**Reason / specification relation:** Section 6 requires `PasswordResetRequest`
at `/forgot-password` with the listed validation, status states, accessibility,
and React Testing Library coverage. No such page or route exists.

**Existing code to reuse or modify:** `frontend/src/App.jsx`,
`frontend/src/main.jsx`, `frontend/src/index.css`, `frontend/src/setupTests.js`,
`frontend/vite.config.js`, and the existing component-test style.

**Scope:** New frontend page/component, route, styles, API call, and unit tests.

**Work:**

- Add `PasswordResetRequest` and route `/forgot-password` to the existing
  React Router application.
- Implement email-required/email-format validation that prevents a request
  when invalid.
- POST to the existing reset request endpoint using the approved API contract.
- Implement idle, invalid, loading, generic-success, HTTP-429, and generic
  server-error states. Success copy must not reveal account existence.
- Add semantic labels, keyboard operation, visible focus, and `aria-live`
  announcements.

**Acceptance criteria:**

- Invalid email displays an inline error and triggers no API request.
- A valid submission shows the generic inbox/reset-instructions success state.
- HTTP 429 shows a retry-later message; other failures show a generic error.
- The form is labeled, keyboard accessible, and announces success/errors.
- React Testing Library tests cover each required state.

**Dependencies:** K-01 for the stable request response contract; K-03 for
final HTTP-429 behavior; Resolved decision Q-04.

**Testing expectations:** Add React Testing Library tests for required/invalid
email, no request on invalid form, loading, generic success, 429, generic
server error, labels, keyboard operation, focus visibility, and `aria-live`.

### P-02 — Build the desktop reset-confirm page and deep-link UX

**Owner:** Петро — Frontend Developer

**Description:** Add the reset-confirm route and desktop UI that reads the
approved reset link, validates a new password and confirmation, calls the
confirm API, and presents all required success/error/resend UX.

**Reason / specification relation:** Section 7 requires `PasswordResetConfirm`
at `/reset-password/`, URL parsing, focus, validation, password hints, resend,
success/login behavior, accessibility, and unit tests. None exists today.

**Existing code to reuse or modify:** `frontend/src/App.jsx`,
`frontend/src/main.jsx`, `frontend/src/index.css`, `frontend/src/setupTests.js`,
`frontend/vite.config.js`, and the existing test tooling.

**Scope:** New frontend page/component, route, styles, approved API call, and
unit tests.

**Work:**

- Add `PasswordResetConfirm` and `/reset-password/` route.
- Parse `uid` and `token` query parameters; keep them out of visible password
  fields and autofocus the new-password field when a link opens.
- Implement new-password and confirmation inputs, required/minimum-length/
  mixed-character strength hints from the existing backend validator policy,
  mismatch validation, loading state, and server-side password errors.
- POST the approved `{ uid, token, password }` payload.
- Show success confirmation with an explicit `/login` action and no timed
  auto-redirect; show invalid/expired token copy with a resend CTA to
  `/forgot-password`.
- Do not implement manual token/UID paste fallback.
- Add semantic labels, keyboard support, visible focus, and `aria-live` status
  announcements.

**Acceptance criteria:**

- A valid URL supplies the API payload and focuses the new-password input.
- Invalid input, weak password, and mismatched confirmation prevent/handle
  submission with accessible errors.
- Valid confirmation shows the success state and explicit login navigation.
- Invalid/expired server response shows a non-sensitive resend action.
- Unit tests cover parsing, focus, validation, API success/error states,
  weak-password handling, resend, redirect behavior, and accessibility behavior.

**Dependencies:** K-01 for confirm payload/errors; K-02 for final invalid,
expired, reused, and revoked behavior; K-03 for 429 handling; K-04 for URL
format; Resolved decisions Q-02, Q-03, Q-06, Q-07, and Q-08.

**Testing expectations:** Add React Testing Library tests for `uid`/`token`
query parsing, initial input focus, no visible token field, password rules,
mismatch, server weak-password response, invalid/expired response, success,
resend navigation without prefill, redirect behavior, labels, keyboard, and
live announcements.

### P-03 — Implement reset-flow frontend integration tests and handoff

**Owner:** Петро — Frontend Developer

**Description:** Integrate the request and confirm test suites with the current
Vitest setup and hand their executable UI contract to QA.

**Reason / specification relation:** Sections 6 and 7 require frontend unit
tests; `SKILLS.md` requires handoff of reliable setup/state behavior to QA.

**Existing code to reuse or modify:** `frontend/package.json`,
`frontend/vite.config.js`, `frontend/src/setupTests.js`, and newly created
P-01/P-02 tests.

**Scope:** Frontend test files and frontend test configuration only.

**Work:**

- Use the existing Vitest/Testing Library setup to add reset component tests.
- Ensure tests mock only the approved endpoint contracts and do not introduce
  secrets or token persistence.
- Provide the QA handoff: routes, client states, mocked response shapes, and
  frontend test command.

**Acceptance criteria:**

- `npm test` includes both reset-page test suites and passes.
- Tests establish that reset token values are used only for the confirmation
  request and are not persisted or printed.
- QA can reproduce the documented frontend states from the handoff.

**Dependencies:** P-01 and P-02; K-01 contract decisions.

**Testing expectations:** Run `npm test`, frontend lint, and build; document
the commands, fixtures/mocks, and all expected request/confirm response states
for Q-01 and Q-02.

## 5. QA/Test tasks — Михайло

### Q-01 — Create independent reset-flow E2E coverage

**Owner:** Михайло — QA/Test Engineer

**Description:** Establish independent automated browser coverage for the full
reset journey and required error/lifecycle scenarios, then make it run in CI.

**Reason / specification relation:** Section 14 and the source QA task require
happy-path E2E, invalid/expired/throttled scenarios, CI execution, and email
capture. The repository contains no E2E runner or reset E2E tests.

**Existing code to reuse or modify:** `.github/workflows/ci.yml`,
`frontend/package.json`, existing backend test/email facilities, and handoffs
from K-01 through K-04 and P-01 through P-03.

**Scope:** E2E test framework/configuration, E2E tests, and CI integration;
do not change production behavior.

**Work:**

- Select and configure an E2E runner compatible with the repository.
- Implement the full flow: request reset, capture test email, extract approved
  link, open it, set a strong password, verify the password change, verify the
  user can log in with the new password, and verify the old password no longer
  works.
- Cover invalid token, expired token, throttled request, and at least the other
  required lifecycle cases available through the approved backend test setup
  (reused and revoked tokens).
- Add E2E execution to CI for authentication-affecting pull requests.

**Acceptance criteria:**

- CI runs and passes the reset happy-path E2E plus invalid-token, expired-token,
  429, and login-verification scenarios.
- E2E data uses test-only accounts/email capture and does not publish tokens.
- Reuse/revocation results are verified where the test environment provides the
  lifecycle controls.

**Dependencies:** K-01 through K-04, P-01 through P-03, and Resolved decision
Q-05.

**Testing expectations:** Execute the added E2E suite locally and in CI against
test-only data; retain evidence for request success, email link extraction,
password update, invalid, expired, reused, revoked, and 429 flows as supported
by the approved environment.

### Q-02 — Perform accessibility and security verification

**Owner:** Михайло — QA/Test Engineer

**Description:** Independently assess accessibility, security controls, API
contract behavior, and security documentation for the completed reset flow.

**Reason / specification relation:** Sections 12 and 14 require accessibility
checks, anti-enumeration and other security verification, and no critical
accessibility failures.

**Existing code to reuse or modify:** Completed K-01 through K-05 and P-01
through P-03 deliverables; `PROJECT_SPEC.md`; `docs/security/forgot-password.md`.

**Scope:** Automated accessibility checks and independent security/contract
verification; production fixes remain assigned to the relevant owner.

**Work:**

- Run axe or Lighthouse on `/forgot-password` and `/reset-password/`.
- Verify labels, tab order, focus visibility, initial focus on reset confirm,
  keyboard operation, and `aria-live` behavior.
- Independently verify anti-enumeration, API contract, rate limits, no
  sensitive response data, token/password log redaction, refresh/session
  invalidation, CORS, and CSRF guidance where applicable.
- File reproducible failures with requirement, steps, expected/actual result,
  evidence, and probable owner.

**Acceptance criteria:**

- No critical accessibility failures remain on either reset route.
- The security checklist has evidence for every PROJECT_SPEC section-12 item.
- Any failure is reported rather than waived or hidden.

**Dependencies:** K-01 through K-05, P-01 and P-02, and the QA environment
from Q-01.

**Testing expectations:** Run axe or Lighthouse against both routes; execute
security/API checks for known-versus-unknown response equivalence, throttling,
lifecycle results, redaction, session/refresh behavior, CORS, and applicable
CSRF guidance. Produce reproducible failure reports.

### Q-03 — Produce QA evidence and final quality-gate report

**Owner:** Михайло — QA/Test Engineer

**Description:** Document the independently verified result and issue the final
quality-gate status for the epic.

**Reason / specification relation:** Section 14.5 and `SKILLS.md` require
`docs/qa/forgot-password.md` with steps, screenshots, results, and transparent
PASS/FAIL reporting.

**Existing code to reuse or modify:** Test evidence from Q-01/Q-02, CI output,
and completed backend/frontend/API-doc test results.

**Scope:** Create `docs/qa/forgot-password.md` and quality report artifacts.

**Work:**

- Record requirement-to-test traceability, test environment/setup, steps,
  expected and actual outcomes, sanitized screenshots/evidence, automated test
  commands, CI results, accessibility outcome, and outstanding risks.
- Confirm that backend, frontend, E2E, and documentation acceptance criteria
  are complete before reporting PASS.

**Acceptance criteria:**

- `docs/qa/forgot-password.md` exists with required test steps, screenshots,
  and results.
- Final report marks each requirement PASS/FAIL/BLOCKED with evidence.

**Dependencies:** Q-01, Q-02, K-01 through K-06, and P-01 through P-03.

**Testing expectations:** Confirm all required backend, frontend, E2E,
accessibility, CI, email, documentation, and security checks have recorded
results before issuing PASS; otherwise report FAIL/BLOCKED with evidence.

## 6. Dependencies between tasks

| Dependency | Reason |
|---|---|
| Resolved decisions Q-01 to Q-09 → K-01, K-02, K-03, K-04, P-01, P-02, Q-01 | API payload/status, lifecycle defaults, throttle policy, password policy, login verification, redirect behavior, manual fallback, resend behavior, and API docs are fixed before implementation. |
| K-01 + K-04 → P-01/P-02 | Frontend needs stable request/confirm response formats and the reset-link URL/query contract. |
| K-02 + K-03 → P-02/Q-01/Q-02 | Confirm UX and E2E/security tests depend on lifecycle and 429 behavior. |
| P-01 + P-02 → Q-01/Q-02 | E2E and accessibility checks require both rendered routes. |
| K-05 → Q-02 | QA verifies documentation claims against deployed settings/behavior. |
| K-01–K-06 + P-01–P-03 + Q-01/Q-02 → Q-03 | Final quality gate requires all implementation and verification work. |

## 7. Requirement → task traceability

| PROJECT_SPEC requirement | Tasks |
|---|---|
| Request route, validation, states, accessibility, unit tests (section 6) | P-01, P-03, Q-01, Q-02 |
| Confirm route, URL parsing, password fields/validation, resend, redirect, accessibility, unit tests (section 7) | P-02, P-03, Q-01, Q-02 |
| Request API, generic response, known/unknown behavior (section 8) | K-01, K-03, K-04, K-06, Q-02 |
| Confirm API, server validation, password change, session/refresh invalidation (section 9) | K-01, K-02, K-06, Q-01, Q-02 |
| Expiry, single-use, revocation, admin inspection, lifecycle tests (section 10) | K-02, Q-01, Q-02 |
| HTML/text email, URL, context, console/staging settings, rendering tests (section 11) | K-04, K-05, Q-01 |
| Anti-enumeration, token security, audit redaction, CSRF/CORS/email security (section 12) | K-01, K-02, K-03, K-05, Q-02 |
| Monitoring and alerts (section 13) | K-02, K-05, Q-02 |
| E2E, error scenarios, accessibility, CI, QA documentation (section 14) | Q-01, Q-02, Q-03 |
| Security documentation (section 15) | K-05, Q-02 |
| Developer-facing API documentation (sections 8 and 9) | K-06, Q-03 |

## 8. Definition of Done

Epic #30 is done only when:

- K-01 through K-06, P-01 through P-03, and Q-01 through Q-03 satisfy their
  acceptance criteria.
- The backend and frontend implement the approved shared contract.
- Existing reusable behavior remains covered and all newly required unit,
  integration, E2E, and accessibility checks pass in CI.
- `docs/api/forgot-password.md`, `docs/security/forgot-password.md`, and
  `docs/qa/forgot-password.md` exist, accurately describe the implementation,
  and contain no secrets/tokens.
- Михайло’s final report has no unresolved FAIL or BLOCKED requirement.

## 9. Resolved decisions

1. **Token architecture and TTL:** Keep Django `default_token_generator`, use a
   one-hour token lifetime, and rely on password change to invalidate the
   token. Do not introduce a custom persistent reset-token model unless the
   existing architecture makes it necessary to satisfy the spec.
2. **Password-policy contract:** Use the existing Django
   `AUTH_PASSWORD_VALIDATORS` as the source of truth. Do not add separate
   password-reset-only rules.
3. **Weak-password status:** Return HTTP 400 Bad Request for password
   validation errors and keep the existing DRF validation-error approach.
4. **Throttling:** Apply 5 requests/minute per IP and 5 requests/hour per email
   for reset requests, plus 5 attempts/minute per IP for confirmation. Return
   HTTP 429 when a limit is exceeded and preserve anti-enumeration behavior.
5. **Post-reset authentication:** The E2E happy path must continue after reset
   to verify that the user can log in with the new password and that the old
   password no longer works.
6. **Success redirect:** After successful reset, show an explicit `Go to Login`
   action and do not auto-redirect.
7. **Manual token/UID fallback:** Do not implement manual paste fallback.
   Invalid or expired links should point users to request a new reset link.
8. **Resend:** The `Request a new reset link` action navigates to
   `/forgot-password` without pre-filling the email automatically.
9. **API documentation:** Add `docs/api/forgot-password.md` as the developer-
   facing reference for both reset endpoints, request/response formats, errors,
   400/429 behavior, and the `uid`/`token` format.

## 10. Open questions requiring user approval

None.
