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


## BLS no-key recovery verified design

A hosted real one-shot on the primary Tower revealed BLS HTTP 200 with non-success
application status and no source series, while Treasury and OpenFIGI returned
source-bound observations. A 200 alone never establishes usable economic data.

The CPI-U reader first uses the fixed unregistered BLS v1 exact series GET.
If the official API returns documented non-success request status
(REQUEST_NOT_PROCESSED / REQUEST_FAILED), or an HTTP/network transport hold,
it attempts one independent fixed, official BLS flat-file download:
https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems . This is
BLS's own publication, not a third-party price feed or an invented cached
value. Its full exact source URL replaces the API-documentation citation on
the resulting owner card and reviewed Soulaana fact/comparison. The fallback
is exact-series-only for CUUR0000SA0, 5 MB maximum, no redirects, two valid
distinct monthly observations, decimal/future-date/duplicate validation,
and same owner-use and per-source AI permissions. Unknown provider failures,
bad sources and stale snapshots remain HOLD. The original CPI index period and
retrieval time remain distinct; no live securities quote, brokerage order,
model API call, commercial credential or source-rights inheritance.

BLS's published v1 signature and Python example show both singleton-list
and object Results wrappers, so both are strictly normalized on successful
API responses; a non-success envelope is NEVER reinterpreted as successful.
No extra recurring worker, cron, paid Render service or provider login is
introduced. This repair still requires an actual hosted source receipt after
deployment before being called operationally verified.
