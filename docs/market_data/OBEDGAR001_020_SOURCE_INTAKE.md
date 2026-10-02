# OBEDGAR001–020 · Official SEC research intake and protected OB integration

**State:** source branch only. No market/broker account, no paid resource, no real SEC request, no automatic scheduler, no market-data or trading-mode unlock. New source records are not visible on hosted OB until a vetted backend owner resolver is explicitly attached to the existing Tower guard.

## Official sources and what each contributes

| Official feed | Exact route/product | OB lane |
| --- | --- | --- |
| SEC issuer cross-reference | `https://www.sec.gov/files/company_tickers_exchange.json` | SEC CIK/name/ticker **cross-check** of independent listing directory; never proves price, listing or optionability alone |
| SEC submissions | `https://data.sec.gov/submissions/CIK##########.json` | Bounded filings, 8-K/10-K/10-Q/20-F/6-K and selected disclosures, acceptance provenance, official primary filing document |
| SEC companyfacts | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | Selected US-GAAP financial values, original concept and units, period, form and accession, joined to the **same** reviewed CIK and submissions receipt |

SEC says its public submissions and XBRL APIs need no authentication/API key and are updated as disclosures are disseminated. The SEC also calls for an identifying automated client and limits aggregate requests to **no more than 10/second** under fair access. Our owner collector is intentionally slower (**at most one request/second per run**, maximum 20 explicitly chosen issuer CIKs, no parallelism/scheduler). User-agent must be an actual operator/business contact, not invented or checked into GitHub. Official references:
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/about/developer-resources
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

SEC documents older submissions via `filings.files`. This initial bounded integration uses the recent segment and flags **RECENT_ONLY_OLDER_PAGES_NOT_IMPORTED** where older segments exist. It does not claim a complete multi-decade filing archive. Companyfacts contains selected facts extracted from SEC reports, not every narrative disclosure or full statement table; it may not cover all issuers equally. Do not interpret reported annual-versus-quarterly flow periods as comparable without period/start metadata.

## Flow and permissions

SEC feed → isolated owner-invoked collector → exact official URL + CIK/shape validation → atomic local cached JSON plus URL, timestamp, SHA-256 and conditional HTTP headers → independent listing directory + SEC CIK mapping → source-reported accession acceptance map → 8-K/10-Q/10-K etc. issuer events + selected original financial concepts → existing `SymbolResearchInputs` → `symbol_research_snapshot` → **existing** `project_research` → read-only Symbol Page/Market Map/Trade/Review and separately licensed Soulaana context.

Files:
- `scripts/obscan_public_edgar_fetch.py` — zero-network dry run by default; owner opt-in, three official endpoints, bounded response, no redirect following, 304 digest verification, 429 HOLD, no rate-evasion.
- `engine/market_intake/edgar_research.py` — issuer/CIK/acceptance/right-bound join. Creates **no duplicate scanner** and has no HTTP.
- `engine/market_intake/edgar_cache.py` — digest-and-origin checked offline SEC products and optional trusted Tower resolver. Source receipt times remain distinct from later review time.
- `scripts/ob_edgar_research.py` — offline operator report after explicit external rights review; requires both independent Nasdaq/other listing directory inputs and SEC cross-reference.
- `web/templates/ob_research_context_partial.html` — existing protected read-only disclosure panel now displays source-cited SEC concepts. Market Data Desk continues to list SEC EDGAR as a reference/event source, not a quote.

**Rights are NOT automatically created by free public availability.** Event/internal non-display/owner display and financial/internal/owner display are individually supplied after actual policy/use review. AI explanation and long-term retention are independent, default false. Invitee display, resale, raw vendor data redistribution and broker permissions are not inferred or granted. The hosted app still has no automatic research resolver; before any real owner display, Tower must provide a reviewed, owner-only backend identity registry and reviewed cache/directory receipts to `make_owner_edgar_resolver`, then inject it into its existing `register_protected_symbol_research_context` per deployment review. It must not take a ticker/CIK from untrusted query parameters or bypass owner session + step-up.

**Timestamp and replay limit:** `acceptanceDateTime` is retained as source-reported SEC JSON evidence, not independently compared with the original filing SGML header. We mark `SEC_JSON_REPORTED_NOT_RAW_HEADER_VERIFIED`, decline malformed, timezone-naive, future or inconsistent stamps; no exact intraday backtest or trading trigger is licensed by this record. SEC itself notes there is no separate publication-availability timestamp for filing content. For point-in-time research requiring minute-level certainty, retrieve and verify the original filing header before claiming that precision. A historical filing date does not make its later-downloaded financial facts available to a simulated earlier decision.

## Operator commands

1. Preview, **no request**:
```bash
python scripts/obscan_public_edgar_fetch.py --output ./local-obscan --ciks 0000320193
```
2. Only when a valid real research name/email has been supplied and SEC policy reviewed, explicitly run:
```bash
python scripts/obscan_public_edgar_fetch.py --enable-network \
  --user-agent "YOUR ACTUAL RESEARCH NAME real-contact@yourdomain.com" \
  --output ./local-obscan --ciks 0000320193
```
Use a dedicated local folder outside source control. Each issuer creates a submissions JSON and `.companyfacts.json`, each with its own verified HTTP metadata. Rate limits, broken content or incorrect CIK result in HOLD; no fabricated replacement.
3. Independently obtain/review `nasdaqlisted.txt` and `otherlisted.txt`, then make a separate owner-internal rights evidence record outside the repo:
```json
{
  "scope": "owner_internal",
  "event": {
    "permission_reference": "YOUR_REVIEWED_EVENT_USE_RECORD",
    "verified_at": "2026-09-29T14:00:00+00:00",
    "internal_research": true,
    "automated_non_display": true,
    "owner_display": true
  },
  "fundamentals": {
    "reference": "YOUR_REVIEWED_FINANCIAL_USE_RECORD",
    "reviewed_at": "2026-09-29T14:00:00+00:00",
    "internal_research": true,
    "owner_display": true,
    "ai_explanation": false,
    "long_term_retention": false
  }
}
```
These references are examples of required evidence fields, **not proof that any rights were approved**. Replace only after genuine review. The CLI does not permit a past-dated or missing rights flag to act as owner approval or change Tower session state.
4. Generate an offline, source-bound report:
```bash
python scripts/ob_edgar_research.py \
  --nasdaq ./nasdaqlisted.txt --other ./otherlisted.txt \
  --crossref ./local-obscan/company_tickers_exchange.json \
  --cache ./local-obscan --symbol AAPL \
  --rights-review ./private-reviewed-edgar-rights.json
```

No direct browser calls to data.sec.gov (which does not support CORS); no API key is needed. Nothing in this workflow starts a cron, purchases hosting, writes to active `data/market_universe.json`, creates an order, or silently unlocks Manual Live.

## Acceptance gates

- SEC identity must match exact CIK from independently cross-referenced directory; a ticker-only JSON or mismatch is HOLD.
- SEC parallel filing arrays must agree in length; only exact accepted accessions bind facts, and conflicting/future/naive timestamps are excluded.
- Official HTTPS origin, bounded JSON, stable cached source checksum and retrieval time; invalid/replaced cache or 304 mismatch is HOLD.
- True owner-reviewed rights for each type, owner/invitee/AI/retention kept independent.
- Existing Tower authorization and source-only research projection; synthetic fixtures never run as real feed.
- Real licensed equity and OPRA options observations still require **separate** feed, upstream lineage, canonical market time, confidence/risk/admission checks. SEC events and fundamentals cannot fill a missing market price.

### Tested locally by CI (mock transport only)

`python -m pytest -q tests/test_obscan_public_edgar_fetch.py tests/test_obscan001_025_sovereign_intake.py tests/test_obscan026_040_universal_gateway.py tests/test_obscan041_055_market_data_desk.py tests/test_obintel001_030_symbol_research.py tests/test_tower_ob_market_data_desk_selective.py tests/test_tower_ob_symbol_research_selective.py`

Production enablement additionally requires an actual operator User-Agent, reviewed rights, real source receipt, authenticated owner browser walkthrough and explicit hosted release authorization.
