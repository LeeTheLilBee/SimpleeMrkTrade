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

## Soulaana explanation registration (separate source-status lane)

The exact protected keyless snapshot now includes a nested `soulaana_source_register` from
`engine/market_intake/keyless_soulaana.py`. The shared browser component
renders a source-awareness/Soulaana explanation on every listed OB consumer
room, using the same one Tower-authorized snapshot and no separate provider
requests. The register distinguishes BLS CPI context, Treasury debt context,
OpenFIGI identifier reference and the **delegated** SEC filing corridor.
It reports current source states, safe meaning/limitations, and what's missing;
source errors/revocation recompute to HOLD. It does not pretend a delegated
SEC corridor fetched a filing.

**Critical boundary:** Soulaana's deterministic source-status projection
contains no source values, FIGI IDs, issuer/fundamental payloads, provider
publication periods, private Public account values or provider response text.
It is NOT an invocation of an LLM, an authorization to send provider data into
model prompts, or a connection to the trading/decision engines. Each output
explicitly says `raw_source_values_included=false`,
`source_content_ai_authorized=false`, `quote_verified=false`,
`candidate_admitted=false` and `broker_execution_authorized=false`.
The owner still sees the independently reviewed observations in the source
cards. An actual per-source content-bearing AI integration requires separately
reviewed AI/non-display terms, Tower authorization and source/rights rechecking.
Do not reuse the owner-display flags to infer AI-use rights.

Public's future authenticated stock and option quotes will travel through
their own reviewed gateway and freshness/entitlement gates. They are not
inferred from this keyless source register and remain blocked by the unresolved
Public account discovery issue.


## Owner-authorized Soulaana source-evidence feed (separate reviewed lane)

The owner specifically authorized Soulaana to receive the public research after the basic source-status-only integration. The content-bearing handoff is a **separate, bounded and non-executing** artifact named OB_SOULAANA_KEYLESS_EVIDENCE_V1, produced alongside the existing status-only register within the same exact Tower-protected source snapshot. It is rendered on every shared keyless owner-room card. It is a deterministic verified explanatory payload, **not proof an external language model was invoked**; an external model adapter would require its own reviewed destination and consent. It cannot enter Soulaana's trading decision-engine context by accident.

- Three independently controlled AI-use grants for BLS CPI index, US Treasury reported Debt to the Penny and the public-domain FIGI identifier. Each must already have source use and owner display enabled, plus OB_KEYLESS_SOULAANA_CONTENT_ENABLED=1 and its own OB_KEYLESS_<SOURCE>_AI_USE_REVIEWED=1. An enabled source does not inherit another source's rights, and missing permission returns status/hold with no value.
- Retain exact source period, retrieval timestamp, fixed official reference and precise unit. Never call CPI an inflation percentage, debt a Treasury bond yield, or a ticker/FIGI mapping tradability proof.
- BLS attribution is shown with its retrieved date and required statement: "BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov."
- OpenFIGI payload is only the public-domain FIGI and requested ticker, not unrelated proprietary Bloomberg data, raw provider records, AI training permission or an options chain.
- SEC remains a **delegated** issuer route: keyless status alone does not contain an SEC filing; its separate existing SEC-specific content and AI permissions are left unchanged. Public authentication/quotes are still blocked on actual account linkage and independently reviewed current equity/options data rights.
- The global envelope's ai_input_approved=False is intentional: it prevents blanket forwarding of all four source rows. Only entries in the nested source-specific evidence brief are approved. Each nested observation and wrapper again denies live quote, candidate, order, capital and execution authority. No raw API response, vendor secret or third-party credential is forwarded.
- Owner can disable the single content flag or any individual review grant and redeploy: the reader then returns no newly authorized fact for that source; old in-process observations are filtered from content whenever a source is revoked. This does not install or call a third-party LLM endpoint.

Reviewed official terms (Sept 29, 2026): https://www.bls.gov/developers/termsOfService.htm (secondary use permitted, attribution and retrieval date required); https://treasurydirect.gov/legal-information/developers/web-api-terms/ (API search/display/analysis permitted without implying government endorsement); https://www.openfigi.com/docs/terms-of-service (FIGI identifiers dedicated to public domain). Business deployment beyond owner-only internal research, model-service transmission, redistributing derived reports or ingesting unrelated source fields requires separate review.
