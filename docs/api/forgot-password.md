# Password reset API

The reset flow uses Django's `default_token_generator` with a one-hour TTL.
The raw token is only carried in the emailed URL and the confirm request; it
is never persisted or written to logs.

## Request a reset

`POST /api/auth/password-reset/`

```json
{"email":"user@example.com"}
```

For a syntactically valid email the response is always `200`, regardless of
whether an active account exists:

```json
{"detail":"If the email exists, you will receive reset instructions."}
```

Known users receive a multipart email containing
`/reset-password/?uid=<encoded-user-id>&token=<token>`. Requests are limited by
IP (5/minute) and normalized email (5/hour). A limit returns `429` without
account information.

## Confirm a reset

`POST /api/auth/password-reset/confirm/`

```json
{"uid":"encoded_user_id","token":"token_string","password":"NewP@ssw0rd!"}
```

Success returns `200`:

```json
{"detail":"Password changed successfully."}
```

Invalid, expired, revoked, or already-used credentials return `400`:

```json
{"detail":"Invalid or expired token."}
```

Password policy failures return `400` with DRF field errors, for example
`{"password":["This password is too short."]}`. Confirmation attempts are
limited to 5/minute per IP and return `429` when exceeded.

