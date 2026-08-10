# SDKs & Client Libraries

## Which official SDKs do you provide?
We maintain official SDKs for Python, Node.js/TypeScript, Go, and Ruby. Each wraps
authentication, retries with backoff, and pagination so you don't hand-roll them. Install
instructions and versioned reference docs are in the developer portal.

## How do I authenticate with an SDK?
Set your API key via the `API_KEY` environment variable or pass it to the client
constructor. The SDK sends it as `Authorization: Bearer <key>` automatically. Never
hardcode keys in source — use environment variables or a secrets manager.

## Do the SDKs handle rate limits automatically?
Yes. All official SDKs read the `Retry-After` header and retry 429 and 5xx responses with
exponential backoff and jitter by default. You can tune the max retry count in the client
config, or disable auto-retry if you want to handle it yourself.

## How do I pin or upgrade the API version with an SDK?
Each SDK release targets a specific API version. Pin the SDK version in your dependency
file to lock behavior; upgrade deliberately and read the changelog for the version jump.
The SDK sends the version it targets, which you can confirm via the `X-API-Version`
response header.
