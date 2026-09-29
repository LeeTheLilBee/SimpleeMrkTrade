# OBSCAN026–040 — Universal Multi-Provider Market Gateway

**State: source-only draft. Not deployed. No market-data credentials, subscriptions,
broker sessions, TCP/WebSockets, API calls, or live orders were activated.**
Stacked on OBSCAN001–025 (PR #205), not on the independently deployed Tower branch.
This is an additive Gateway over the existing independent OB scanner, **not another scanner**.

## Owner decision restored

The Observatory must be able to integrate as many *authorized* market-data providers
as useful. IBKR stays the preferred brokerage for eventual separately gated execution.
Alpaca and Tradier are potential market-data and development connectors; direct
contracted SIP/OPRA and other future feeds require only new product mappings, not a
replacement of the scanner. Free directories and filings improve discovery but
**cannot replace a genuine live equities or options entitlement.**

Product catalog (integration possibilities, not entitlements):

| Connector | Product lanes | Critical limitation |
| --- | --- | --- |
| Tradier | Production equity and options | Brokerage/partner eligibility and use rights; sandbox delayed. |
| Alpaca | IEX equity, separately entitled SIP equity and OPRA option; indicative options | IEX is not SIP; indicative options are NOT current quote authority. |
| IBKR | Subscription-defined equity and options | The actual venue/product and API market-data type must be verified; delayed/frozen ticks are not live. |
| Licensed SIP / OPRA | Future contracted direct equity/options | Neither is an assumed free quote source. |
| Nasdaq listed directory / OCC reports / SEC EDGAR | Security identity, series reports, issuer events | Research and reference only, no substitute for current quote truth. |
| Future provider | Independent optional product registration | Explicit mapping, source lineage, rights review and real provider limits required. |

Official documentation is recorded with each product in
`engine/market_intake/provider_catalog.py`. Catalog names alone do NOT certify
feed quality, business-use rights, redistribution, an approved account or a vendor
subscription. Upstream families such as SIP/OPRA must come from separately reviewed
rights, not a user-visible dropdown or untrusted API payload.

## Implementation

- `UniversalMarketGateway.install()` binds one unique exact product/source ID to
  reviewed `SourceRights`, separately mapped equity/option `FeedAdapter`, and
  optionally confirmed per-provider quotas. Owner, invitee, automated non-display,
  redistribution, expiry and instrument permissions stay independent.
- `ingest()` accepts **already obtained** source payloads from a future trusted
  authenticated transport. It checks source event timestamp, receipt time, expiry,
  market-session proof, stale/future/invalid observations and out-of-order replay.
  Arbitrary raw claims of source ID or license are ignored. It returns a redacted
  decision, not a quote or trading instruction.
- `owner_research_packet()` uses only separately current **owner-display-permitted**
  observations and the existing `inspect_symbol()` engine. Two vendors sourcing
  one upstream family are not counted as independent corroboration; independent
  conflicting last prices produce CONFLICT_HOLD. Options cannot satisfy research
  without separately eligible underlying evidence.
- `TrafficPlanner` now accommodates options-only subscriptions: exact product
  quotas, batch size, cooldown, backoff and explicitly bounded stream selections.
  No request is sent by the planner; verified underlying symbols must come from
  an independent upstream gate before options proposals.
- `provider_status()` reports every catalog product as NOT_CONFIGURED,
  REFERENCE_ONLY, SOURCE_ONLY_READY or RIGHTS_HOLD, with no invented live connection.
- `revoke()` drops installed rights and purges cached quotes. Re-onboarding a
  revoked source must use a fresh exact source identity and independent review.
- Feed options volume normalization now rejects fractions rather than truncating.

## Connection boundaries and phased acceptance

1. **Current source-only phase:** run offline regression tests; no credentials
   or paid resources. Existing OB and Tower deployed behavior remains unchanged.
2. **Owner-approved live ingress:** independently review business/non-display,
   internal analysis, owner-screen display, future invitee redistribution, source
   attribution/retention, each instrument/feed subscription, product-specific
   request limits and account status. Put secrets in approved backend secret
   references, never repo or browser. Implement narrow vetted network adapters.
   A Tradier sandbox response is delayed and must not be promoted to current.
   IBKR's data-type indicator and Alpaca's explicit IEX/SIP/OPRA/indicative feed
   selection must be inspected at the actual transport. There is no assumed
   cross-provider proof from identical upstream family data.
3. **Tower integration review:** selectively connect read-only result receipts to
   canonical market-time, source provenance, observation temporal validity,
   evidence quality, candidate sufficiency and existing protected room data seams.
   Do NOT open generic routes, expose raw non-display prices or replace hosted
   source truth by an offline fixture.
4. **Beta and future scale:** invitee display and redistribution require additional
   explicit provider authorization; direct feeds are optional and contractual.
   Separate manual, hybrid and automated brokerage execution remain locked until
   independently approved mode/risk/broker/Tower gates.

Nothing here provisions Render, automatically signs up for vendors, creates paid
data accounts, grants Manual Live, submits broker orders, moves capital, or claims
current market-price coverage. A connection outage or stale/revoked data leads to
HOLD, never silent delayed/historical/synthetic substitution.

## Validation

Run: `python -m pytest -q tests/test_obscan001_025_sovereign_intake.py tests/test_obscan026_040_universal_gateway.py tests/test_obscan_public_edgar_fetch.py`

The dedicated source-only CI job also performs syntax checks and static network,
broker and hosting boundary assertions. Synthetic test symbols and prices are
test fixtures, not actual market observations.
