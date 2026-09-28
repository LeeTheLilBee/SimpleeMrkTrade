# OBDATA009 — Why the beautiful live Observatory is empty, and the real data-source boundary

Owner reported zero market data after the September 28 whole-room visual release, while the Tower-protected rooms render successfully.

## Root cause actually verified
1. The modern V25 browser adapter fetches `GET /ob/engine-feed-snapshot.json` with same-origin credentials, no-store.
2. Tower's `ob_web_route_enforcement.PROTECTED_EXACT_OB_ROUTES` originally omitted that data endpoint, causing default-deny 403 before a valid authenticated read could reach the handler.
3. Inspection of the **actual registered** `web.app.ob_engine_feed_snapshot_v25` via CI shows that the handler only reads static `data/market_universe.json` and `data/pipeline_status.json`. It derives candidate tiers from static `hot`, invents MU/AMD/INTC fallback position previews, constructs imaginary next-month call labels in `manual_live_queue`, and computes a marketing-like market-health score from category counts. It returns `source=guarded_json_snapshot` but NO independent provider/as-of quote timestamp. These static materials are **not** current market truth, actual position evidence or permission to trade. Existing OBDATA001–005 policies correctly made the frontend reject missing provenance rather than fill in demo symbols.
4. Therefore merely permitting the endpoint is necessary for network wiring but does not establish any authentic quote, option chain, current candidate, alert, capital or broker data.

## This patch, before provider approval
- Adds **only** the exact canonical GET/HEAD endpoint to Tower's same authenticated owner-session, step-up and operational OB boundary. Unknown `/ob/*` remains default-denied; POST to the data endpoint returns 405.
- For hosted Tower ONLY, preserves the obsolete handler privately for audit and replaces its exact view function with a no-store JSON `provider_not_configured` response. All source/capital/market evidence, sectors, symbols, candidates, positions, options, manual-live queue and synthesized scores are explicitly absent. Never return old fixture data as the solution. If the expected historical handler changes, startup fails closed instead of replacing a separately integrated provider.
- The canonical JS adapter maps this response to `unavailable`, `display_eligible=false`, `current_eligible=false` and an explicit source-unconnected explanation. It does not turn response-generation time into quote as-of.
- Regression tests cover exact protected route, anonymous denied, valid owner with step-up in isolated guard harness, read-only method, source-pending JSON and headers, old handler not exposed, and a maliciously populated source-pending payload still projecting no fake symbols/candidates/trades.
- No billing upgrade, credentials, exchange agreement, new market fetch, trading enablement, broker API or new public path is introduced.

## Separate work required for actual real data
An explicitly approved *market-data provider and permitted usage* must be selected. The first useful schema is a read-only **Survey/Paper market research snapshot**: provider/data-product/exchange, immutable source id, actual provider-supplied market as-of per quote, clock/time zone, quote quality/known delays, symbol and sector membership only, source freshness, server-side credentials and bounded cache/rate budget. One provider request must not be interpreted as proof of contractual redistribution rights. Unavailable, rate-limited or malformed provider response fails closed with a human reason and no last-known-as-current substitution.

A distinct later product contract is needed for **options quotes/chain** (expiration, right, strike, bid/ask, open-interest/volume with timestamps and licenses); it is not generated from a stock price. **Broker actual balances/positions/fills** require independent authenticated broker evidence; a public market-data provider never supplies them. Any future NOW/Watch/Not Yet classification must be sourced from the canonical OB engine and may not be synthesized from decorative Map geometry. Manual Live remains separately HOLD.

Do not silently enable or redistribute Yahoo/yfinance: yfinance explicitly says the Yahoo API is personal-use/research/educational and it is not an exchange-grade licensed production data provider. Owner authorization and provider terms are required before integrating a quote source. The owner has not yet supplied or approved one. This status-first patch is honest repair, **not** data activation.

## Owner acceptance criteria after source selection
1. Authenticated Tower→OB session returns 200 from exactly the protected data endpoint, anonymous denies without data exposure, unknown routes deny.
2. Actual approved provider quote returned with source, per-symbol provider as-of and quality/delay; no generated current timestamps or seed provenance.
3. The Dashboard, Living Market Sky and Symbol Page display *only* the source-authorized subset; failures say why in Soulaana language. No false pending provider if actual valid provider integration exists.
4. Test source expiry, provider outage/rate limit, malformed response, malformed future timestamps, disagreement with local time, and cross-account source permissions.
5. Owner device walkthrough with source/time labeling and clear Survey/Paper limitations. Paper records are independently marked simulation; Live remains locked.
