# API Versioning & Pagination

## How is the API versioned?
The API is versioned in the URL path (e.g. `/v1/...`). Breaking changes ship under a new
version; additive changes (new fields, new endpoints) ship within the current version.
Always ignore unknown JSON fields so additive changes don't break your integration.

## What is your deprecation policy?
When a version is deprecated we announce it on the changelog and via the
`api.deprecation` webhook, and we support it for at least 12 months afterward. Responses
from a deprecated version include a `Sunset` header with the retirement date.

## How does pagination work?
List endpoints use cursor pagination. Each response includes `next_cursor` (null when
there are no more pages). Pass it as `?cursor=<value>` on the next request. Page size
defaults to 50 and can be set with `?limit=` up to a maximum of 200.

## Why am I seeing duplicate or missing items while paginating?
This usually happens when items are created or deleted mid-pagination. Cursor pagination
is stable against this for existing items, but to get a fully consistent snapshot of a
changing dataset, filter by a fixed `created_before` timestamp while you page through.

## How do I know which API version I'm calling?
Every response includes an `X-API-Version` header echoing the version that served it. If
it doesn't match the version in your request path, you're likely being redirected by an
old SDK — upgrade the SDK to pin the intended version.
