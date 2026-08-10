# Webhooks

## Why is my webhook not receiving events?
Check three things: (1) the endpoint URL in Settings → Webhooks is publicly reachable over
HTTPS, (2) it returns a 2xx within 5 seconds, and (3) the event type is subscribed. Failed
deliveries retry with backoff for 24 hours; the Webhooks → Deliveries log shows every
attempt and the response code we received.

## How do I verify webhook signatures?
Every webhook includes an `X-Signature` header — an HMAC-SHA256 of the raw request body
using your webhook signing secret (Settings → Webhooks → Signing secret). Recompute the
HMAC over the exact raw bytes and compare. Do not parse-then-reserialize the body before
verifying, or the signature will not match.

## Which events can I subscribe to?
Common events include `invoice.paid`, `invoice.failed`, `user.created`,
`usage.threshold_reached`, and `api.deprecation`. The full list is in Settings → Webhooks
→ Event types, where you choose exactly which events each endpoint receives.

## How are webhook retries and ordering handled?
A non-2xx or timeout is retried with exponential backoff for up to 24 hours. Events are
delivered at-least-once and are NOT strictly ordered, so make your handler idempotent —
dedupe on the event `id`, which is stable across retries.

## My webhook endpoint was disabled automatically — why?
Endpoints are auto-disabled after ~20 consecutive failed deliveries, or immediately if the
URL starts returning redirects or resolves to a private IP. Fix the endpoint and re-enable
it in Settings → Webhooks; past events during the disabled window are not replayed
automatically but can be resent from the Deliveries log.
