# API Rate Limits

## What are the API rate limits?
Rate limits are per-plan and enforced per API key: Starter allows 60 requests/minute,
Growth 600 requests/minute, and Enterprise is custom. Your current limit and live usage
are shown in Dashboard → API → Usage.

## Why am I getting HTTP 429 "Too Many Requests"?
A 429 means you exceeded your plan's per-minute request limit for that API key. The
response includes a `Retry-After` header with the number of seconds to wait. Back off for
that duration and retry. Sustained 429s mean you should batch requests, spread load, or
upgrade your plan.

## How should I handle rate limits in my integration?
Respect the `Retry-After` header and use exponential backoff with jitter on 429 and 5xx
responses. Read `X-RateLimit-Remaining` on every response to slow down before you hit the
limit, cache responses where possible, and batch operations instead of one request per
item.

## Do rate limits reset on a fixed schedule?
No. Limits use a rolling 60-second window per API key — there is no fixed reset time. As
older requests age out of the window, capacity frees up continuously. This means a short
burst may 429 even if your average rate is well under the limit.

## Can I request a higher rate limit?
Growth and Enterprise customers can request a temporary or permanent limit increase from
Dashboard → API → Usage → "Request increase". Include your expected peak requests/minute
and use case. Starter plans must upgrade to raise limits.
