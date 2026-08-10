# Usage & Quotas

## Where do I see my current API usage?
Dashboard → API → Usage shows requests this minute, this day, and this billing period,
broken down per API key. You can also fetch it programmatically from `GET /v1/usage`,
which returns the same counters plus your plan limits.

## What is the difference between rate limits and monthly quotas?
Rate limits cap requests per minute (a burst control). Monthly quotas cap total included
requests per billing period (a volume control). You can be well under your rate limit and
still exhaust your monthly quota, or vice versa — the Usage panel tracks both separately.

## What happens when I exceed my monthly quota?
Growth and Enterprise plans allow overage: requests keep succeeding and overage is billed
at the per-request rate shown on the Pricing page. Starter plans block further requests
with HTTP 429 and an `error.code` of `quota_exceeded` until the next period or an upgrade.

## Can I set usage alerts?
Yes. Dashboard → API → Usage → "Alerts" lets you set thresholds (e.g. 80% and 100% of
quota). When crossed, we send an email and fire the `usage.threshold_reached` webhook so
you can react automatically.

## Is usage counted per key or per account?
Rate limits are enforced per API key, but monthly quota is pooled across the whole
account. Creating more keys does not raise your quota — it only distributes rate-limit
headroom across separate keys.
