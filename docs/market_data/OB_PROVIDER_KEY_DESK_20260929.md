# OB owner API Key Desk (Finnhub / Alpha Vantage)

Source integration branch: tower-ob-general-provider-keys-20260929.

## Purpose and present scope
Exact protected GET/POST \`/ob/data-desk/api-keys\` next to existing Public-specific flow.
It accepts two *reviewed provider IDs*, not arbitrary URLs or unknown authentication
formats. Finnhub and Alpha Vantage can be entered independently. SEC EDGAR requires
no API key and remains on its separate official public research collector.

This is **temporary credential intake**, not a durable API-key vault:
- raw keys stay in a private server-worker RAM store for 30 minutes, or until
  Tower logout, owner Forget, or process restart, whichever occurs first;
- only masked *status* (present/not tested/read-only verification pass) is rendered;
- no key is placed into session cookies, browser storage, logs, URLs on the
  browser side, source-controlled config, source ledger, or existing Tower
  Secrets Vault metadata registry;
- on multi-worker hosting, one worker cannot use another worker's RAM copy.
  Do not treat this as a production durable connection. Later durable storage
  requires an independently reviewed secret-store/rotation/revocation adapter.
- keep \`OB_PROVIDER_KEY_DESK_ENABLED\` absent or \`0\` until owner security review;
  set exactly \`1\` to permit protected POST after authorized deployment.
- hosted reverse proxy requires \`OB_PUBLIC_OWNER_CANONICAL_ORIGIN\` to equal the
  exact public HTTPS origin (no trailing slash), using the existing Public form
  trusted-origin configuration. Do not infer origin from proxy Host metadata.
- use Tower login → fresh step-up → authorized OB launch. No new external route.

## Read-only verification
No network request on page view or key input. Owner explicitly selects **Test
read-only access** to issue one fixed provider request. Verification is rate-limited
to one attempt per provider per session per 60 seconds; results never display
provider response bodies or raw exceptions.

Finnhub: HTTPS profile2 lookup for AAPL with \`X-Finnhub-Token\` header.
Alpha Vantage: HTTPS \`TIME_SERIES_DAILY\` compact look-up for IBM with its
provider-required \`apikey\` query parameter, server-side only. Vendor APIs
could also rate-limit, return no data or require additional product access.
A successful response means **only** a harmless authenticated research request
returned the expected shape. It does not prove any license, OPRA, SIP, non-display,
AI analysis, retention, business/trust eligibility, source freshness or trade
permission. A refused/limited response is classified through the shared secret-safe provider diagnostic contract. The owner can distinguish rate limiting, access rejection, provider availability, network failure, redirect hold, parse/shape failure and bounded provider-message cases without receiving the raw upstream response.\n
No automatic scanner registration, historical-series ingestion, market quote
admission, Live unlock, account selection, purchase, broker order or capital
action is introduced. Future adapter must reconcile reviewed rights with the
existing UniversalMarketGateway and historical Symbol Intelligence source
contracts; do not promote Alpha Vantage end-of-day free quote to real-time.

## Security acceptance
- Exact Tower route map + HTTP allowlist, authenticated owner, fresh step-up,
  valid OB launch, POST origin/CSRF checks, exact HTTPS browser origin.
- Unknown \`/ob/data-desk/*\` paths default deny; unlisted providers rejected.
- No key data in browser response, cookies, source registry, audit, Jinja.
- Back-end-only credential handling and fixed official provider endpoints;
  no user-controlled URL and no automatic retries on API failure.
- Separate Public OAuth and EDGAR public identity workflows unchanged.
- No paid resources or deployment implied by merging this source PR.

Run:
\`\`\`sh
python -m pytest -q tests/test_tower_ob_provider_key_desk.py tests/test_ob_public_owner_connection.py tests/test_tower_ob_market_data_desk_selective.py tests/test_tower_ob_web_route_enforcement.py
\`\`\`


## 2026-09-30 diagnostic upgrade
The Key Desk now imports the shared contract in `tower/ob_provider_diagnostics.py`.
Finnhub and Alpha Vantage are the first migrated connectors. Future provider/plugin
connection surfaces must reuse the fixed vocabulary rather than emit arbitrary upstream
text or a single undifferentiated verification failure. See
`docs/market_data/OB_PROVIDER_PLUGIN_DIAGNOSTIC_CONTRACT_20260930.md`.
