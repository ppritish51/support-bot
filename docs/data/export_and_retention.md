# Data Export & Retention

## How do I export my data?
Settings → Data → "Export" generates a downloadable archive of your workspace data as JSON
(and CSV for tabular records). For programmatic export, `GET /v1/exports` starts a job and
returns a download URL when it's ready. Exports include your records but not other
workspaces' data.

## How long is my data retained?
Active data is retained for the life of the account. Time-series and log data follow your
plan's retention window: 30 days on Starter, 1 year on Growth, and configurable on
Enterprise. Data older than your window is aggregated or removed automatically.

## What happens to my data if I cancel?
After cancellation, data is retained in read-only form for 30 days so you can export or
reactivate. After 30 days it is scheduled for permanent deletion. Export anything you need
before the grace period ends.

## Where is my data stored and is it encrypted?
Data is stored in our primary cloud region and encrypted at rest (AES-256) and in transit
(TLS 1.2+). Enterprise customers can request a specific data residency region. Details are
in the Security & Compliance section of the docs.
