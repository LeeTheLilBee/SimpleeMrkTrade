# OBSEC001 — Free official SEC EDGAR research connector

## Scope and verified upstream terms

SEC public submissions and companyfacts JSON APIs require **no SEC account,
authentication or API key**. This is a read-only backend collector, not an
EDGAR filer API. Source documentation:
https://www.sec.gov/search-filings/edgar-application-programming-interfaces
and fair access: https://www.sec.gov/about/developer-resources .
The SEC's published aggregate maximum is 10 requests/second per user; this
implementation serializes at **at most 2 requests/sec per process**. When
the active collector topology cannot be bounded to the explicitly reviewed two
single-worker owner services below, independent aggregate throttling is
mandatory before enabling another instance or shared-identity SEC collector. It requests at most 3 official JSON documents per
symbol investigation, never follows redirects, never takes a URL from a user,
does not scrape HTML and does not persist the received raw data.

**September 29 fixed-topology source activation:** exactly the two owner-only
Free Tower/OB deployments are permitted, each with the checked-in startup
enforcing one Gunicorn worker. At no more than two requests/second in each
single process, their maximum combined SEC collector rate is below four
requests/second, under the SEC's ten-per-second aggregate ceiling. No scheduled
SEC polling is installed. This bounded topology assumption does not account
for unrelated SEC automation using the same user identity. Do not enable this
collector on any third service, autoscale, increase worker count, or introduce
other SEC jobs without first installing a shared cross-deployment fair-access
budget/throttle. Upstream 403/429 stays a HOLD, never a fixture fallback.
Both services require the separately reviewed use/display/AI flags and monitored
contact; this does not create a new credential or broker capability.

## Activation (not automatic)

Install/configure a real monitored contact mailbox through the backend secret
environment, not GitHub, browser JavaScript, screenshots or chat.

    OB_SEC_PUBLIC_RESEARCH_ENABLED=1
    OB_SEC_CONTACT_EMAIL=<your monitored business contact email>
    OB_SEC_PUBLIC_USE_REVIEWED=1
    OB_SEC_OWNER_DISPLAY_REVIEWED=1
    OB_SEC_AI_EXPLANATION_REVIEWED=1  # Optional, only after independent review

The three review flags are **operator assertions** following a source-rights
review, not a substitute for it. Omit the AI flag to withhold numerical
financial facts from Soulaana while retaining permitted owner display.
No environment values are included in the published app responses.

When disabled, hosted Tower registers the same optional research context
processor with NO resolver and no additional routes. When explicitly enabled,
the owner-protected, step-up-gated exact Symbol room can request official
ticker -> CIK -> submissions -> companyfacts data. Other rooms do not use
query-string-selected symbols: their research panel remains unpopulated until
a separately trusted server-side symbol selector is integrated. SEC data
never replaces /ob/engine-feed-snapshot.json, unlocks Manual Live, asserts a
live stock/option price or validates a Nasdaq listing/option series.

## Manual, read-only proof

After setting reviewed environment variables, from repo root:

    python -m scripts.ob_sec_public_research_check --symbol AAPL

This makes three bounded live SEC JSON requests and prints a normalized owner
research packet with official source references, published SEC facts where
the acceptance dates are independently proven, and Soulaana's permission-
filtered deterministic brief. Nothing is written to disk. A 403, 429, invalid
format, redirect, oversized response or identity disagreement is a sanitized
failure; there is no fixture fallback.

No need to obtain an EDGAR account, API key, brokerage token, paid Render
service or live market-data subscription for public company filings.

## Boundaries and limitations

- Official SEC ticker->CIK association is not proof of exchange listing or
  optionability. Unmatched or conflicting identities do not get guessed.
- Financial facts are selected unmodified from supported US-GAAP concepts.
  Each fact requires an exact independent SEC submission accession and
  acceptance timestamp. Future or unverifiable facts are omitted.
- No historical equities OHLCV, option-chain pricing, news, automated company
  event interpretation or actual trade P&L comes from EDGAR.
- Current companyfacts parser only selects supported concepts and bounds
  ingestion to 200 qualifying rows; it is not a complete audited financial
  statement interpreter.
- The client downloads only on a real opted-in owner request. No automatic
  cron/polling or data retention was activated.
- Hosted response is subject to existing Tower authenticated owner, step-up
  and operational OB gate. Public API availability does not override Tower.
- SEC fair access is shared across all traffic from the deployment/user; the
  per-process throttle is not sufficient for horizontally scaled instances.
- Production release still needs an actual owner browser walkthrough and
  provider-response verification; offline synthetic CI does not prove SEC
  connectivity from the hosted environment.

## Source tests

    python -m pytest -q tests/test_obsec_public_edgar_research.py

The test response fixtures are synthetic, clearly distinct from SEC live data.
The real-data manual owner test is intentionally not run by CI or deployment.
