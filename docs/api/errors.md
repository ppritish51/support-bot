# API Error Codes

## What does HTTP 400 Bad Request mean?
A 400 means the request was malformed — invalid JSON, a missing required field, or a
wrong parameter type. The response body includes an `error.field` and `error.message`
pointing to the exact problem. Fix the request shape and retry; 400s are never retryable
as-is.

## What does 401 Unauthorized vs 403 Forbidden mean?
401 means the API key is missing, malformed, or revoked — send it as
`Authorization: Bearer <key>`. 403 means the key is valid but lacks permission for that
action (wrong scope or role). For 403, check the key's scopes in Dashboard → API → Keys.

## What does HTTP 413 Payload Too Large mean?
Request bodies are capped at 10 MB. A 413 means you exceeded that. For larger uploads use
the resumable upload endpoint (`/v1/uploads`), which splits the payload into chunks.

## What do 5xx errors mean and should I retry them?
5xx means a temporary server-side problem on our end. These are safe to retry with
exponential backoff and jitter. If 5xx persists for more than a few minutes, check the
status page (status.example.com) for an active incident before escalating.

## How do I read the error response body?
Every error returns a JSON object: `{ "error": { "code", "message", "field", "request_id" } }`.
Always log the `request_id` — support can trace any request end-to-end from it, which
makes debugging far faster than pasting stack traces.
