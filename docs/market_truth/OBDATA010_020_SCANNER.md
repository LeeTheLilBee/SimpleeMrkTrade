# Simplee Observatory | OBDATA010–020 | First-party Market Scanner Foundation

**Status (2026-09-28):** Code/test-only stacked on private data-boundary repair PR #199. NOT merged, NOT deployed, no live feed credentials, no owner beta quote access, no paid provider, no broker execution. It is a provider-independent scanner core and strictly gated example source mappers.

## Product decision

The Observatory owns the **scanner**, collection policy, source validation, symbol watchlist, research features, UI projection, evidence ledger and explanation interface. External sources still own their respective facts, licensing and collection timing. No unrestricted website scraping or API licensing bypass is necessary.

The scanner runs once per *permitted source class*. It does **not** merge a macro time series, 8-K filing or single-venue trade into an imaginary full-market quote. No invented options bid/ask, portfolio positions, Manual Live candidates, current as-of timestamps or ready-to-trade status.

| Lane | Intended input | Beta UI / freshness label | Authority |
| --- | --- | --- | --- |
| Equity/ETF observations | Limited real-time Alpaca Basic **IEX** or another explicitly authorized source | Actual vendor as-of, single-venue coverage, per-observation freshness | Source-derived research ONLY |
| Historical bars | Source-identified and **completed** same-product daily bars (20–60) | Last completed session, source/venue, previous completed close | Technical research ONLY |
| Corporate disclosures | SEC JSON submissions/financial facts, approved User-Agent and rate controls | Filing date and source link; separate from quote as-of | Filing research ONLY |
| Economic reference | FRED V1 per-series approved, no API usage until key and rights checked | Source economic period, units, revision/vintage | Human-readable, ephemeral reference; NOT AI input or persistent cache pending explicit permission |
| Global context | OWID Grapher .csv + .metadata.json; verify chart and underlying third-party license | Annual/day period preserved; citation/unit | Context ONLY, subject to rights |
| Options research | Separate authorized indicative/OPRA rights and quote chain timestamps | Quote category, liquidity, bid/ask provenance | Existing options intelligence; never synthesize a chain |
| Broker truth | Future authenticated IBKR read-only capital/fills, independently scoped | Broker as-of/account boundary | NOT part of scanner or free public feed |

### Confirmed provider facts to plan around (verify again before activation)

Alpaca Basic Trading API is advertised at $0, US stock/ETF real-time **IEX** rather than all-market SIP, with a **30 WebSocket stock-symbol subscription** and limited historical request budget; free options feed is **indicative**, not paid OPRA. The scanner may reflect what that source says, never call it consolidated NBBO. Actual vendor account/data usage permissions for invited private beta must be approved, and API secrets must stay in Render environment, not GitHub, HTML, client JS or messages.

SEC data.sec.gov official `submissions` and `companyfacts` use JSON with no API key. Require a truthful User-Agent, configured host allowlist, queue/caching only when permitted, per-host backoff and a conservative rate budget, well under SEC's stated no-more-than-10 requests/sec fair-access guideline. Never scrape SEC HTML when official JSON suffices.

FRED's currently published terms prohibit AI/ML use of the API and restrict storing/caching/archiving FRED content; its API can also include third-party copyright. Our adapter therefore **defaults to no AI-assistant input and no persistent cache**, with per-series permission gating. Soulaana may describe the scanner's source state, not ingest FRED output into a model by default. Evaluate underlying BLS/BEA/Treasury primary-source APIs separately for future licensed/approved macro analysis.

OWID provides documented chart CSV and metadata and does not imply permission to reuse every underlying third-party series; approve per-chart source/attribution before ingestion. No external browser fetch.

### Exact source code now present

- `engine/market_scanner/source_contract.py`: economic observation and disjoint macro-only envelope.
- `macro_sources.py`: injected-transport, per-series/per-chart licensed FRED/OWID parsers (NO live network in tests).
- `sec_filings.py`: official filing JSON parser and issuer/date validation (no quote fields).
- `alpaca_iex_ingress.py`: pure Alpaca Basic IEX trade/daily bar normalization, authenticated feed and finalized-bar flags required; NO keys, network or order routes.
- `equity_research.py`: caller-supplied approved server entitlement, 30-symbol capped observational scanner, provider trade as-of, quote expiry, completed consistent history, historical 5/20 close averages, comparison with last completed close, fail-closed output. No trading signal, broker position, options quote, user capital or new model.

All output carries its original source and original period. Never compute *market-wide breadth* from a single venue's subset. Scan results are observation cards only, not actionable trade recommendations.

### Operational collection cadence (proposed, no job scheduled)

- Owner sets a watchlist; max 30 simultaneous equity streams on free IEX plan, with requests queued and throttled.
- For intraday IEX observations, ingest authorized trade events, validate every source timestamp and provider agreement, evaluate bounded freshness (default 180 seconds when applicable), perform deterministic research comparisons using a separate completed daily history.
- Fetch SEC filing JSON on a measured schedule or on owner inspection (rate control globally); do not hammer filing servers.
- Fetch slow economic/global reference only on a permitted frequency and only within series/chart reuse rights; **no FRED persistent caching or AI use** absent express permission.
- On connection/permission failure: status = HOLD; quote, candidate, options, Manual Live and position output empty. Do not roll yesterday's quote forward with a fresh generated timestamp.
- Present the Living Market Sky only from source-authorized, scoped observations. Meaningful sky glow must map to explainable metrics, not decorative stochastic movement.

### Remaining activation gates

1. Owner opens a free data-provider account and reviews the plan's **personal-owner vs invited-tester commercial/display** usage. Do not commit keys; add approved read-only market-data credentials through existing protected Render settings only when ready.
2. Add bounded server-only transport, source agreement/entitlement configuration and request logging that omits secrets. Validate vendor IEX messages and completed daily bars; no order APIs. Keep vendor outage/budget held safely.
3. Add exact Tower-protected, read-only research endpoint and map normalized scanner observations to existing OBDATA003 market projection only where provenance and UI redistribution are actually authorized. PR #199's status override cannot be replaced by an unreviewed feed; intentionally fail closed if runtime handler identity has changed.
4. Run static/source tests, time and licensing negative tests, full Tower security tests, owner authenticated source/time/browser walkthrough. Keep manual and automated execution HOLD.
5. Separately evaluate options contract entitlement and equity/broker market-data contracts before using any research for actual trading.

**No live-data success is claimed by these source/test commits.**

Official documentation / terms:
- Alpaca Market Data plans: https://docs.alpaca.markets/us/docs/about-market-data-api
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC developer/fair access: https://www.sec.gov/about/developer-resources
- FRED API terms: https://fred.stlouisfed.org/legal/terms/
- FRED observations: https://fred.stlouisfed.org/docs/api/fred/series_observations.html
- OWID chart API: https://docs.owid.io/projects/etl/api/chart-api/
