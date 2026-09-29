# OBSCAN001–025 — Sovereign Market Intake, no-money build

Status: **source-only research implementation; not deployed, not connected to broker, no quote entitlements provisioned.** This branch is based on independent OB main, not the Tower-hosted branch or pending celestial UI drafts. It does not edit web routes, Tower authentication, capital policies, broker execution, or existing OB mode operation.

## Own the intelligence, not an imaginary exchange tape
The scanner catalogs an entire approved universe once; identity-checked filings/events guide closer inspection. Ingestion is interchangeable **lanes** instead of being hardwired to just two API vendors.

Approved exchange directory + SEC identifiers (metadata only)
→ Catalog, newly-seen/removed/changed diff
→ Public event intake (ears open; review only)
→ Traffic planner (explicit quota, events, watchlist, broad rotation, backoff)
→ Entitled provider field-mapping adapters
→ Current equity gate → separately current options gate
→ Corroboration and source-conflict HOLD
→ Read-only research packet → existing OB provenance / temporal / sufficiency / candidate admission gates.

The approved directory + filing events can produce EVENT_RESEARCH_ONLY without a price. They never prove a stock moved or is optionable. Two vendors sourcing one SIP are one upstream family, not two independent confirmations.

## Source modules delivered
- engine/market_intake/contracts.py: rights registry defaults to deny, explicitly reviewed non-display versus owner/invitee display and redistribution, event/receipt time, quote freshness, market session, equity and OCC series validation; no execution authority.
- universe.py: local Nasdaq/otherlisted parser, SEC cross-reference, identity diff, prices and options UNAVAILABLE; absence from a directory does not prove delisting.
- adapters.py: approved provider-specific field mappings, immutable entitlement/lineage from installed registry (not vendor JSON), rejects timezone-free quote timestamps and missing required fields.
- scanner.py: issuer-bound filing discovery, bounded dedup, research threshold observations, independent-feed conflict hold, separate options gate, output cannot mark a trade admitted.
- traffic.py: provider request/min, symbols/request, cooldown, event warm lane, owner watchlist priority, cold rotation, single bounded streaming-symbol selection, explicit backoff. These are PROPOSALS, never HTTP or opened streams.
- local_catalog.py: offline command prints metadata only and never overwrites legacy data/market_universe.json.

## Offline run
After individually checking source terms and downloading approved snapshots:

    python -m engine.market_intake.local_catalog --nasdaq ./nasdaqlisted.txt --other ./otherlisted.txt --sec ./company_tickers_exchange.json

SEC JSON is optional. No secrets, extra paid Render service, scheduled worker or live trade action.

## Access/rights audit (verify before using in business application)
Nasdaq directory: https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs and https://nasdaqtrader.com/Trader.aspx?id=symbollookup — free lookup/download is not necessarily a commercial non-display or redistribution license.
SEC EDGAR: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data — filings and company identifiers, not an exchange quote. Current fair-access guidance caps at 10 requests/second across machines; identify automated client with User-Agent and throttle/cache.
Tradier: https://docs.tradier.com/docs/market-data and https://docs.tradier.com/docs/faq — live brokerage data differs from delayed sandbox; personal API access is not automatically third-party distribution permission.
IBKR: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php — verify each entitlement and consolidated versus venue scope independently.
Direct options OPRA: https://www.opraplan.com/ and https://www.opraplan.com/document-library — consolidated current-data vendor, non-display, access and redistribution terms; no claim of free direct options prices.
FRED future macro: https://fred.stlouisfed.org/docs/api/terms_of_use.html — specific series licenses and disclaimer, not an equity/option feed.

## Staged release gates
1. **No budget:** offline catalog and diff, issuer-checked events, source-only research lead and testable normalized adapters. No historical/sample quote may display as current.
2. **Authorized feed:** owner establishes business and account rights, market-data display/non-display/redistribution, expiry policy and hard provider limits. Verify source lineage against web/ob_source_provenance.py, web/ob_observation_temporal_validity.py and web/ob_cross_source_corroboration.py.
3. **Connection to existing OB:** existing sufficiency/admission and Tower enforcement remain mandatory; research packet is not canonical candidate admission, broker quote, trading recommendation or capital truth. Verify on an authenticated owner session separately.
4. **Later:** select authorized direct SIP/OPRA adapter or other permitted provider, infrastructure and agreements as funded. Do not turn on real mode through this module.

Never use screen scraping, multiple sessions to bypass limits, paid-token sharing or rate evasion, Yahoo/yfinance inferred real-time for live decisions, guessed event timestamps, synthetic quotes, assumed optionability, news as price confirmation, or invite-only access as a license waiver.

This module deliberately does not replace the old engine or add a hosted route. It is valuable intelligence infrastructure; absent an authorized current feed it will not pretend to be a crisp real-time price scanner.
