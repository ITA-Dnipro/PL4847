# Authentication token storage

## Current approach

The access token is stored only in React memory inside `AuthProvider`.

The refresh token is also kept in memory during the current session.

If the user enables the "Remember me" option, the refresh token is additionally stored in `localStorage` so the session can be restored after reopening the application.

The access token is never stored in `localStorage`.

## Token refresh

The access token expiration time is read from the JWT payload.

`AuthProvider` schedules a refresh request approximately 60 seconds before the access token expires.

The refresh request is sent to:

`POST /api/auth/refresh/`

If the refresh request fails or the refresh token is invalid, the authentication state is cleared automatically.

## Logout

Logout sends the refresh token to:

`POST /api/auth/logout/`

After logout, access and refresh tokens are removed from the application state and the saved refresh token is removed from `localStorage`.

## Security trade-off

Storing a refresh token in `localStorage` can expose it if the application has an XSS vulnerability.

The preferred production approach is to store the refresh token in a backend-set HttpOnly, Secure, SameSite cookie.

For the current sprint the backend returns access and refresh tokens in JSON, so the frontend uses in-memory access-token storage and optional `localStorage` persistence for the "Remember me" feature.