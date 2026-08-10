# API Keys

## How do I create an API key?
Dashboard → API → Keys → "Create key". Give it a name and select its scopes, then copy the
key — it is shown only once at creation and cannot be retrieved later. Store it in a
secrets manager or environment variable, never in source control.

## How do I rotate an API key safely?
Create a new key, deploy it to your integration, verify traffic is flowing on the new key
in Dashboard → API → Usage, then revoke the old key. Because you can run both keys in
parallel during the switch, rotation causes zero downtime. There is no fixed rotation
schedule enforced, but rotating every 90 days is a common practice.

## What is the difference between sandbox and production keys?
Sandbox keys (created in a sandbox workspace) hit the same API surface but operate on
isolated test data and never trigger real billing or customer emails. Production keys work
only against production and vice versa — a 401 often means you used the wrong environment's
key.

## What happens when I revoke a key?
Revocation is immediate and irreversible. Any request using a revoked key returns 401
right away. Revoke a key the moment you suspect it's leaked; there is no grace period, so
make sure your integration is already on a new key first.

## Can I scope a key to specific permissions?
Yes. Each key is assigned scopes at creation (e.g. `read:invoices`, `write:webhooks`). A
key can only perform actions its scopes allow; anything else returns 403. Use narrowly
scoped keys per integration to limit blast radius if one leaks.
