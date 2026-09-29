# OB keyless public research lane — September 29, 2026

No external provider login, registration, API key, account-linking, paid resource, brokerage connection or Public Business API change is needed for this lane. It is additive to the existing protected /ob/data-desk catalog and separately opt-in SEC EDGAR symbol research. The authenticated access required is Tower's existing owner session, not a third-party provider login.

## Four official sources and their roles

| Source | Exact backend call / authority | Account? | Explicit boundaries |
|---|---|---|---|
| SEC EDGAR | Existing separately reviewed SECOfficialResearchResolver: ticker-to-CIK, submissions and companyfacts. New shared context links to this separate corridor; it does NOT claim another SEC fetch or a new filing receipt. | No API key. SEC requires monitored descriptive User-Agent contact under existing flags. | Original filing / acceptance time, not live quote or company identity independently verified by FIGI. |
| BLS | Existing unregistered v1 fixed GET CUUR0000SA0 (CPI-U all items NSA), once/day/process success TTL | No | Value is CPI index at series publication period (YYYY-M##); not percent inflation, release timestamp or stock price. Official unregistered budget 25 requests/day. |
| US Treasury | New fixed GET FiscalData v2/accounting/od/debt_to_penny, sorted latest by record_date, amount tot_pub_debt_out_amt; 6-hour success TTL | No | Record-dated total outstanding federal public debt in USD, not a Treasury bond yield, intraday price or economic forecast. |
| OpenFIGI | Existing fixed POST /v3/mapping, unauthenticated ticker/exchange mapping, owner-specified ticker only; 1-hour cache and local five-symbol/min ceiling | No | FIGI is an identifier candidate, not issuer verification, broker symbol eligibility or live options chain. Ambiguities hold. |

Official documentation: https://www.sec.gov/search-filings/edgar-application-programming-interfaces ; https://www.sec.gov/about/developer-resources ; https://www.bls.gov/developers/api_signature.htm ; https://www.bls.gov/developers/api_FAQs.htm ; https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/ ; https://www.openfigi.com/api/documentation .

## Exact server-owned read and consumers

- GET /ob/research/keyless.json and optional validated ?symbol=MSFT. Every request requires actual Tower owner session, fresh step-up and admitted OB launch via tower.ob_market_data_desk_integration and the independent exact route map. No POST, HEAD, wildcard routes or public CORS.
- The endpoint returns only schema OB_KEYLESS_PUBLIC_CONTEXT_V1, fixed official source references, values/periods where fetched, retrieved timestamps, and status codes for unavailable/rights/ambiguous results. Its entire contract explicitly denies prices, options chains, live quotes, order authority, AI-use and candidate admission. Nothing is pushed into the canonical engine price feed, scanner admission, broker or Teller.
- The same endpoint populates an independent dark-glass context rail on Market Data Desk, Dashboard, Market Map, Symbol Page, Trade Center, Review Center, Owner Dashboard and Owner Console. On Symbol Page the URL symbol is used for OpenFIGI; all rooms provide a manually entered ticker input. No raw provider response, token, arbitrary URLs or HTML from vendors reach the browser. No browser calls official providers directly.
- All source requests start after the owner-only JSON request, not on import or normal HTML rendering. The server uses bounded fixed endpoints, timeout/no redirect, safe value/shape checks and in-process short cache. Empty or invalid source data shows HOLD, not a synthetic fallback.

## Deployment and separate source-by-source review

Default OFF: without OB_KEYLESS_RESEARCH_ENABLED=1, all three backend fetches are held and the card explains this rather than showing invented data. Independent operator-reviewed internal owner-display flags are required for each source:

- OB_KEYLESS_BLS_USE_REVIEWED=1 and OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED=1
- OB_KEYLESS_TREASURY_USE_REVIEWED=1 and OB_KEYLESS_TREASURY_OWNER_DISPLAY_REVIEWED=1
- OB_KEYLESS_OPENFIGI_USE_REVIEWED=1 and OB_KEYLESS_OPENFIGI_OWNER_DISPLAY_REVIEWED=1

These flags are backend configuration only, cannot be selected by browser/query, do not imply legal rights for downstream redistribution/AI, and require exact source and quota review. No provider keys are configured in this lane. The SEC row says DELEGATED only if existing OB_SEC_PUBLIC_RESEARCH_ENABLED, OB_SEC_PUBLIC_USE_REVIEWED, OB_SEC_OWNER_DISPLAY_REVIEWED and real OB_SEC_CONTACT_EMAIL are present; the historical SEC route remains its own authority. Do not set or change its use rights just to fill the card. Public Business account discovery is an unrelated hold and stays untouched. FRED, BEA, Alpaca, Tradier and any key/login-required source are excluded from this implementation.

## Verification and limitations

Offline tests use wholly synthetic responses and test denied Tower roles, malformed ticker/shape/value/date, individual source review, revoked cache, quota hold, absence of browser secrets, fixed endpoint requests, and eight HTML consumers. They do not establish real deployed successful responses or any live price feed. Production verification requires a genuine authenticated owner GET of /ob/research/keyless.json, inspecting displayed source period/retrieval time and sanitized Render response logs. Render network failure remains HOLD; do not silently manufacture a value.

Provider request allowances may be shared across users/instances. The current per-process cache/budgets are suitable for this one-owner test, not a horizontally scaled production ingestion platform; implement shared quota coordination before wider deployment.
