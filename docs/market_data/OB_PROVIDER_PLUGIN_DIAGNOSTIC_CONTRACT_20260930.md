# Observatory Provider / Plugin Diagnostic Contract

Date: 2026-09-30

## Decision

All Observatory provider, broker, data-source, API-key and streaming adapters that expose
an owner-visible connection/verification state must use the shared secret-safe diagnostic
vocabulary in `tower/ob_provider_diagnostics.py`.

Do not collapse every failure into a generic "did not verify" state. Do not expose raw
provider responses in order to be more specific.

## Safe owner-visible states

- `NOT_CONFIGURED`
- `NOT_TESTED`
- `READ_ONLY_CHECK_PASSED`
- `RATE_LIMITED`
- `ACCESS_REJECTED`
- `REQUEST_REJECTED`
- `PROVIDER_UNAVAILABLE`
- `NETWORK_HOLD`
- `REDIRECT_HOLD`
- `RESPONSE_TOO_LARGE`
- `RESPONSE_PARSE_HOLD`
- `RESPONSE_SHAPE_HOLD`
- `PROVIDER_MESSAGE`

Each code has one fixed owner-facing explanation. Arbitrary provider strings are normalized
to `PROVIDER_MESSAGE` before reaching any browser-visible state.

## Security doctrine

A connector MAY inspect an upstream status code or bounded provider message in memory only
long enough to classify the failure family.

A connector MUST NOT persist, render, serialize, log or re-raise:
- API keys, bearer tokens, OAuth secrets or broker credentials;
- credential-bearing URLs or request objects;
- raw provider error bodies/messages;
- account identifiers returned during a failed verification;
- arbitrary upstream exception text.

HTTP 401/403 is intentionally classified as `ACCESS_REJECTED`, not "bad key", because the
same response can represent authentication, activation, subscription or entitlement failure.
HTTP 429 is `RATE_LIMITED`. HTTP 5xx is `PROVIDER_UNAVAILABLE`. Network exceptions remain
`NETWORK_HOLD`; they do not invalidate the credential.

## Provider-specific messages

Some APIs return HTTP 200 with a message object instead of requested data. The adapter may
classify generic indicators such as rate-limit language or access/entitlement language, then
must discard the source text. The raw provider wording is never returned to the owner UI.

## Scope

Finnhub, Alpha Vantage, Twelve Data and Finazon are the current Key Desk adapters using this contract. All future
connectors—including REST, WebSocket, MQTT, streaming HTTP, broker and provider-native
streaming adapters—should import and reuse the shared diagnostic contract rather than invent
new browser-visible error strings.

This diagnostic contract describes connection health only. A successful probe does not prove
commercial-use rights, display rights, non-display rights, AI-analysis rights, retention
rights, SIP/OPRA entitlement, broker execution permission, capital authority or Live-mode
authorization.

## Test requirement

Every new provider/plugin must add synthetic tests for:
1. success;
2. authentication/access rejection;
3. rate limiting when the provider supports it;
4. network/provider outage;
5. unexpected response/schema;
6. proof that raw provider text and secrets cannot reach the browser-visible status.
