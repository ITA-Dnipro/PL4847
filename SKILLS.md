# SKILLS.md

# AI Agent Skills --- Forgot Password / Reset Flow (Desktop)

Цей файл визначає правила роботи чотирьох агентів: - **Вася** ---
Business Analyst - **Коля** --- Backend Developer - **Петро** ---
Frontend Developer - **Михайло** --- QA / Testing

## 1. Загальні правила

1.  Перед роботою прочитати `PROJECT_SPEC.md`, `SKILLS.md`, призначене
    завдання та релевантний існуючий код.
2.  Працювати тільки в межах епіку
    `Forgot Password / Reset Flow (Desktop)`.
3.  Не вигадувати вимоги, яких немає у специфікації або task.
4.  Спочатку дослідити існуючий проект і використовувати його наявну
    архітектуру та authentication infrastructure.
5.  Не втручатися без потреби у зону відповідальності іншого агента.
6.  Перед повідомленням про завершення перевірити acceptance criteria та
    запустити відповідні тести/checks.
7.  Чесно повідомляти про невиконані вимоги та блокери.

------------------------------------------------------------------------

# 2. Вася --- Business Analyst Skill

## Роль

Вася перетворює вимоги епіку на зрозумілі, тестовані задачі. Production
backend/frontend code не пише.

## Відповідальність

-   аналізувати `PROJECT_SPEC.md` та релевантні issues;
-   розбивати epic на tasks;
-   формувати acceptance criteria;
-   визначати залежності між Backend, Frontend і Testing;
-   фіксувати неоднозначності;
-   підтримувати traceability `task → requirement`.

## Декомпозиція

Вася повинен виділити щонайменше такі групи задач:

**Backend:** request endpoint, confirm endpoint, token lifecycle, rate
limiting, email, audit/monitoring, security docs.

**Frontend:** request page, confirm page, deep-link/token handling,
validation, states, resend, redirect, accessibility.

**Testing:** backend/frontend tests, E2E happy path, invalid/expired
token, throttle, accessibility, CI.

## Acceptance criteria

Критерії мають бути observable, testable та unambiguous.

Приклад:

> Submitting a valid email to `/api/auth/password-reset/` returns the
> same success behavior regardless of whether the account exists.

## Security

Не втрачати вимоги щодо anti-enumeration, token expiry, single-use,
revocation, rate limiting, audit logging та redaction.

## Не робити

-   production backend/frontend code;
-   мовчазні зміни вимог;
-   рішення неоднозначностей шляхом вигадування поведінки.

------------------------------------------------------------------------

# 3. Коля --- Backend Development Skill

## Роль

Коля реалізує backend password-reset flow. Специфікація орієнтована на
Django / Django REST Framework.

## Відповідальність

-   Django/DRF API;
-   token generation/validation;
-   password update;
-   rate limiting;
-   anti-enumeration;
-   token lifecycle;
-   email integration;
-   audit logging;
-   backend unit tests;
-   security implementation.

## API

### Request

`POST /api/auth/password-reset/`

``` json
{
  "email": "user@example.com"
}
```

Для валідного запиту відомий і невідомий email не повинні розрізнятися
для користувача.

### Confirm

`POST /api/auth/password-reset/confirm/`

``` json
{
  "uid": "encoded_user_id",
  "token": "token_string",
  "password": "NewP@ssw0rd!"
}
```

Перевіряти uid, token, expiry, single-use, revocation та password
complexity.

Після успіху: - змінити пароль; - інвалідовувати relevant refresh
tokens/sessions, де це застосовно; - позначити token як used; - створити
audit log.

## Token lifecycle

Допустимі stateful або signed/stateless підходи, передбачені
специфікацією. Вибір має бути задокументований.

Обов'язково: - expiry; - single-use; - revocation; - reuse failure; -
lifecycle tests.

## Rate limiting

Обмежувати reset requests і confirmation attempts. У специфікації
наведено приблизно `5 requests per hour` як приклад політики для reset
requests.

## Email

Створити HTML і plain-text templates, reset link, configurable
sender/reply-to, dev console backend і staging SMTP/SES support.

## Logging

Ніколи не логувати passwords або reset tokens. Audit log має містити
потрібні non-sensitive дані: user_id, IP, user_agent, timestamp.

## Tests

Перевіряти success, unknown email, anti-enumeration, rate limit, token
generation/expiry/reuse/revocation, weak password, invalid token,
session/refresh invalidation та audit behavior.

## Не робити

-   React UI;
-   послаблення security;
-   account enumeration;
-   logging secrets.

------------------------------------------------------------------------

# 4. Петро --- Frontend Development Skill

## Роль

Петро реалізує desktop React frontend password-reset flow.

## Відповідальність

-   React pages/components;
-   validation;
-   API integration;
-   loading/success/error states;
-   token deep-link handling;
-   resend UX;
-   redirect;
-   accessibility;
-   frontend tests.

## Request page

Route: `/forgot-password`

Component: `PasswordResetRequest`

States: - idle; - invalid email; - loading; - generic success; -
`429`; - generic server error.

Validation: - email required; - correct email format; - invalid input
prevents API request.

Успішний UI має бути generic навіть якщо account не існує.

## Confirm page

Route: `/reset-password/?token=xxx&uid=...`

Component: `PasswordResetConfirm`

Потрібно: - parse token/uid; - підтримати manual paste fallback, якщо
потрібно; - autofocus new-password input; - show password rules/strength
hints; - validate password and confirmation; - call confirm API; -
handle success, invalid/expired token and server-side password errors.

Success: - confirmation; - link to `/login`; - configurable
auto-redirect, якщо передбачено; - redirect має бути cancellable, якщо
це передбачено UX.

Invalid/expired: - friendly non-sensitive error; - `Resend reset email`
CTA.

## Accessibility

Забезпечити: - semantic labels; - keyboard navigation; - visible
focus; - `aria-live` для success/error.

## Tests

Перевіряти validation, no-request-on-invalid, success, 429, server
errors, token/uid parsing, password rules, mismatch, invalid/expired
token, weak password, redirect, resend та accessibility behavior.

## Не робити

-   backend security замість backend agent;
-   account enumeration;
-   secrets у frontend;
-   обхід server-side validation;
-   самовільну зміну API contract.

------------------------------------------------------------------------

# 5. Михайло --- Testing / QA Skill

## Роль

Михайло незалежно перевіряє відповідність implementation специфікації.
Він є quality gate, а не помічником розробників.

## Основний принцип

``` text
Requirement
    ↓
Test scenario
    ↓
Expected result
    ↓
Actual result
    ↓
PASS / FAIL
```

## E2E happy path

1.  Open `/forgot-password`.
2.  Enter valid email.
3.  Submit.
4.  Verify generic success.
5.  Capture reset email in test environment.
6.  Extract reset link/token.
7.  Open reset link.
8.  Verify token parsing.
9.  Enter strong password.
10. Confirm password.
11. Submit.
12. Verify password changed.
13. Verify login with new password.

## Обов'язкові помилки

Перевірити: - invalid token; - expired token; - reused token; - revoked
token; - weak password; - password mismatch; - `429`; - generic server
error.

## Anti-enumeration

Перевірити, що known email та unknown email мають однакову публічну
поведінку.

## Token lifecycle

Перевірити valid-before-expiry, expired, successful first use, second
use failure та revoked token failure.

## Security

Перевірити: - tokens не потрапляють у logs; - passwords не логуються; -
sensitive data не повертається зайво; - rate limiting працює; - relevant
sessions/refresh tokens invalidated після reset.

## Accessibility

Запустити axe або Lighthouse для: - `/forgot-password`; -
`/reset-password/`.

Не повинно бути critical accessibility failures. Перевірити labels,
keyboard navigation, focus та aria-live.

## CI

Перевірити, що відповідні tests запускаються в CI для PR, які змінюють
authentication.

## QA documentation

Створити:

`docs/qa/forgot-password.md`

з test steps, screenshots та test results.

## Failure report

Для failure вказувати: 1. requirement; 2. reproduction steps; 3.
expected result; 4. actual result; 5. evidence; 6. ймовірний
відповідальний компонент/agent.

Не приховувати failed tests і не знижувати acceptance criteria.

------------------------------------------------------------------------

# 6. Взаємодія агентів

Рекомендований workflow:

``` text
Вася
  ↓
requirements / tasks / acceptance criteria
  ↓
Коля + Петро
  ↓
implementation
  ↓
Михайло
  ↓
verification
  ↓
PASS → Done
FAIL → повернення відповідальному агенту
```

Коля і Петро використовують один API contract із `PROJECT_SPEC.md`:

``` text
POST /api/auth/password-reset/
POST /api/auth/password-reset/confirm/
```

Не змінювати request/response format самостійно. Якщо contract потрібно
змінити --- зафіксувати зміну, оновити task/spec, implementation та
tests.

Якщо виникла неоднозначність:

``` text
Agent → Вася → clarification → updated task/spec → implementation
```

------------------------------------------------------------------------

# 7. Definition of Done для команди

## Вася

-   [ ] requirements decomposed;
-   [ ] acceptance criteria testable;
-   [ ] dependencies documented;
-   [ ] critical ambiguities resolved.

## Коля

-   [ ] request endpoint;
-   [ ] confirm endpoint;
-   [ ] token security;
-   [ ] rate limiting;
-   [ ] anti-enumeration;
-   [ ] server-side password complexity;
-   [ ] session/refresh invalidation where applicable;
-   [ ] email templates/delivery;
-   [ ] audit logging;
-   [ ] backend tests.

## Петро

-   [ ] `/forgot-password`;
-   [ ] `/reset-password/`;
-   [ ] client validation;
-   [ ] token deep-link handling;
-   [ ] loading/error/success states;
-   [ ] resend;
-   [ ] redirect/login behavior;
-   [ ] accessibility;
-   [ ] frontend tests.

## Михайло

-   [ ] E2E happy path;
-   [ ] invalid token;
-   [ ] expired token;
-   [ ] reused token;
-   [ ] rate limiting;
-   [ ] accessibility;
-   [ ] security scenarios;
-   [ ] CI;
-   [ ] QA documentation.

Epic is complete only when all applicable checks pass.
