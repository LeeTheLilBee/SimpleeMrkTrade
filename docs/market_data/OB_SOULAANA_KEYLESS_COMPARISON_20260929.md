# Soulaana keyless source examination — 2026-09-29

## What changed
The keyless public context now preserves **two source-reported observations** where available in each existing official BLS CPI-U and Treasury Debt-to-the-Penny request. Soulaana's independently AI-use-reviewed evidence lane computes the exact change and period-relative percentage with `Decimal`, shows both source periods and the original citation, and explains missing evidence and non-causal boundaries. A source's latest value without an earlier valid point still appears as a single source-bound observation with no invented comparison. OpenFIGI remains a one-symbol identifier mapping, not a price series. SEC EDGAR issuer/filing content remains in its separately reviewed Symbol Research corridor; the keyless card does not invent a filing receipt.

The common owner-only keyless rail in Market Data Desk, Dashboard, Market Map, Symbol Page, Trade Center, Review Center, Owner Dashboard and Owner Console renders the same server-produced, validated source comparisons. Its browser does not call providers, invoke an AI model, persist raw data or touch positions/orders. It uses the already protected `GET /ob/research/keyless.json` route.

## Rights and operational boundaries
- The three independently reviewed keyless sources are BLS, Treasury and OpenFIGI. No new external login/API key/brokerage account, cost, streaming connection or provider is introduced.
- Soulaana content processing requires the existing `OB_KEYLESS_SOULAANA_CONTENT_ENABLED=1` plus the **individual** source's `OB_KEYLESS_<SOURCE>_AI_USE_REVIEWED=1`, alongside source-use and owner-display flags. Owner-display is not silently treated as an AI grant. Turning a flag off suppresses the corresponding comparison even if another source remains reviewed.
- BLS official API terms: https://www.bls.gov/developers/termsOfService.htm . Include access date and the required BLS non-vouching attribution already displayed.
- Treasury Fiscal Service API terms: https://treasurydirect.gov/legal-information/developers/web-api-terms/ permit search/display/analysis with source acknowledgement and no implied endorsement.
- OpenFIGI FAQ: https://www.openfigi.com/about/faq states FIGI symbology has no licensing or re-use restrictions; API docs: https://www.openfigi.com/api/documentation . Do not claim proprietary third-party identifiers are unencumbered.
- BLS's current CPI value is an **index level**, not a rate or inflation percentage; comparisons report the percent change of the two published index levels only. Treasury data is a dated federal-debt stock, not a Treasury yield. Their periods/units differ, so Soulaana never claims one caused the other, or that either establishes a stock/option quote/trade signal.
- The calculations are a useful **deterministic research examination**, not a generative-model call. No autonomous research agent, scheduled polling, AI API secret, price feed, capital authorization or public invitee dissemination is implied.

## Technical verification
Synthetic tests cover: previous source observation retained in the same BLS/Treasury request, no added HTTP call, strict ordering, invalid/missing prior values, source-specific AI reviews, no unreviewed comparisons, source revocation, HTML/JS safe rendering and already existing owner/Tower no-login routes. Reconfirm deployment states separately from CI; CI fixtures do not constitute a real BLS/Treasury/OpenFIGI response.
