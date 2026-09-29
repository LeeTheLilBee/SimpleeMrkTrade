# OB public reference API expansion — September 29, 2026

This additive implementation is stacked on Tower's official SEC PR #217. It does **not** merge stale #205/#206/#207 branches over the hosted OB application, touch broker execution, unlock Manual Live, subscribe to paid data, open a public route, or deploy.

## Source truth

| Source | Transport in this branch | Setup | Actual authority |
| --- | --- | --- | --- |
| BLS Public API v1 | Opt-in backend GET of one official series | No API key; unregistered v1 has 25 daily requests/25 series per query per official FAQ | Dated macro series, **not** live quotes |
| BEA NIPA | Opt-in backend GET with owner-supplied key; typed table/frequency/line | Free BEA registration/key OB_BEA_API_KEY required | Official economic row and reported time period, not source-release time or quote |
| OpenFIGI | Opt-in backend POST of ticker mapping | Key optional; unauthenticated lower quota; OB_OPENFIGI_API_KEY optional | Instrument identifier candidate, no independent issuer or price verification |
| FRED | Catalog / rights HOLD, **no transport added** | Explicit legal review first | FRED current terms prohibit FRED API connection with AI development/training and storage/cache/archiving; never inject into Soulaana or keep in OB DB by default |
| Public Business API | Candidate catalog only | Account acceptance and actual product/data/display/use rights still unverified | Free API calls do not prove free live feed entitlement or broker integration |
| Existing SEC EDGAR | Separate Tower PR #217 | Owner business contact configured server-side | Filings/companyfacts; never live stock/options quotes |

Official docs: https://www.bls.gov/developers/api_FAQs.htm ; https://apps.bea.gov/api/signup/ ; https://www.openfigi.com/api/documentation ; https://fred.stlouisfed.org/legal/terms/ ; https://public.com/api/docs .

**Source boundaries:** All new catalog products are reference and cannot be installed by the UniversalMarketGateway as real-time equity or option quotes. Each output carries provider, source period, retrieval timestamp, official documentation, false quote/execution authority, and separately reviewed AI flag. Retrieval time is not the official publication/release timestamp. Sources are not combined to fake independent live quote corroboration. Conflicting/ambiguous FIGI results HOLD. Backend GET/POST fixed official host/path, HTTPS only, redirects disabled, 8-second timeout, bounded JSON (1 MB). No source raw data is persisted, no keys in output/browser source, no automation in Market Data Desk GET.

## Owner smoke checks, after rights review

No check runs until all three operator env flags are exactly 1:
- OB_PUBLIC_RESEARCH_ENABLED=1
- OB_PUBLIC_RESEARCH_USE_REVIEWED=1
- OB_PUBLIC_RESEARCH_OWNER_DISPLAY_REVIEWED=1

In addition to the global flags, the *selected* provider requires independent backend review flags, e.g. for BLS: `OB_PUBLIC_RESEARCH_BLS_USE_REVIEWED=1` and `OB_PUBLIC_RESEARCH_BLS_OWNER_DISPLAY_REVIEWED=1`. For BEA and OpenFIGI, use the same pattern with `BEA` and `OPENFIGI` respectively. No global reviewed flag silently grants another source. Optional AI use requires **both** `OB_PUBLIC_RESEARCH_AI_USE_REVIEWED=1` and the selected provider's `OB_PUBLIC_RESEARCH_<SOURCE>_AI_USE_REVIEWED=1`; otherwise `ai_use_approved=False`. Set optional OB_BEA_API_KEY / OB_OPENFIGI_API_KEY as backend secrets, not command-line arguments or git files.

Run one explicit command in the approved backend environment:
- python -m scripts.ob_public_research_check --source bls --series LNS14000000
- python -m scripts.ob_public_research_check --source openfigi --ticker MSFT
- python -m scripts.ob_public_research_check --source bea

These are operator-triggered network checks, not live deployed background connections. Values printed are official reference/historical context only. The Market Data Desk lists source possibilities but continues to say no runtime health/credentials/live quotes verified until separate authorized server-side connection receipts and deployment exist.

## Separate activation and remaining work

1. Review exact BLS, BEA and OpenFIGI commercial/internal use, display, retention, AI, request quotas, and current provider documentation. FRED remains out of Soulaana/storage without an independent legal path. Review Public's actual Business API enrollment and market-data rights separately.
2. Configure operator env flags and backend BEA key; run optional real smoke checks in the selected runtime; record sanitized verification outcome, source timestamps, rate-limit response, and request quota.
3. Wire reviewed macro/identifier research into exact protected owner Symbol/Market Map research source contract through Tower, with source-specific AI/display permissions; do not conflate it with price/option/position truth. Persistent audit/revocation and aggregate multi-instance traffic budgets need Tower integration.
4. Independently connect entitled actual stock/options prices via the established gateway and canonical time/entitlement corridor. Owner-only Manual Live remains a different explicit approval gate. No delayed/synthetic fallback pretending to be current.

Validation: python -m pytest -q tests/test_ob_public_research_sources.py tests/test_obscan026_040_universal_gateway.py tests/test_tower_ob_market_data_desk_selective.py. CI uses synthetic fixtures; successful CI never asserts a real third-party API was reached.


## Tower selective integration review

The original #218 was based on the source head of already merged #217. Tower must use a separate current-hosted-branch integration rather than replacing current `web/hosted_tower.py`, auth/step-up or OB UI with old branch content. In the selective integration, no hosted read endpoint is mounted and no provider is started on import: only the reference-only catalog and backend operator-run source modules are present. The staged client additionally enforces source-specific approved-use and AI grants, exact official URL/method matching, type-safe BEA query HOLDs, and regression tests against current Tower Desk and route contracts. CI cannot establish external provider terms, aggregate quota or a real official data receipt; real network checks remain an owner-controlled separate step.
