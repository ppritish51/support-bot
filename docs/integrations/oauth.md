# OAuth & Connected Apps

## How does the OAuth flow work?
We support the standard OAuth 2.0 authorization-code flow. Redirect the user to
`/oauth/authorize` with your `client_id`, `redirect_uri`, and `scope`; on approval we
redirect back with a `code`; exchange that code at `/oauth/token` for an `access_token`
and `refresh_token`.

## How long do tokens last and how do I refresh them?
Access tokens expire after 1 hour. Use the `refresh_token` at `/oauth/token` with
`grant_type=refresh_token` to get a new access token without user interaction. Refresh
tokens are long-lived but are revoked if the user disconnects your app or changes their
password.

## What scopes are available?
Scopes are granular, e.g. `read:invoices`, `write:webhooks`, `read:usage`. Request the
minimum scopes your integration needs — users see the exact list on the consent screen,
and over-broad scope requests reduce approval rates. The full scope list is in the
developer docs.

## Why am I getting invalid_grant on token exchange?
`invalid_grant` almost always means the authorization code was already used, expired
(codes are valid for 60 seconds), or the `redirect_uri` on the token request doesn't
exactly match the one used to obtain the code. Re-run the authorize step and exchange the
fresh code immediately.
