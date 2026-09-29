# OBINTEL001–030 — Source-bound Symbol Intelligence Record & Historical Research

**State:** proposed source-only work, stacked on Market Data Desk PR #207 → provider gateway PR #206 → scanner PR #205. Not an activated real market feed or Tower deployment. No paid resources, provider subscriptions, credentials, web market-price fetches, broker transports, account capital or trading-mode grants.

## Why this exists

Legacy `engine/symbol_intelligence.py` merges earlier signal/trade/execution-universe results; it is not a verified issuer + history + current-source record. Legacy `engine/backtest_engine.py` downloads historical data itself and reports a one-sample “win”; its statistics MUST NOT become live or historical performance claims. The new source-bound research contracts sit **beside** those modules and never import them, yfinance, or a simulated market-pricing fallback. No preexisting score is recalculated merely because historical research exists.

## One record; distinct evidence lanes

`SymbolResearchInputs` explicitly binds one reviewed directory identity (exchange, ticker and SEC CIK where cross-referenced) to independently entitled, as-of-bounded inputs:

1. **Completed-session OHLCV:** `historical_research.py` enforces exact symbol, source/product, unique ordered dates, positive and coherent OHLC, completed sessions, adjustment basis and its proof, separately reviewed automated analysis/owner display/AI/retention rights. A date-only historical snapshot never asserts intraday freshness or verifies a full exchange trading calendar. It computes 20/50/200-session close moving averages *only when enough bars exist*, plus the raw sample high/low, last completed close, volume and sample start/end comparison. Historical-only outputs explicitly deny live/current/options quote, capital and execution authority. Price history is not silently stitched across sources or adjustment bases.
2. **Issuer facts:** `fundamental_research.py` accepts reviewed, offline SEC companyfacts JSON for exactly the directory-bound ten-digit CIK. Each selected unmodified US-GAAP concept must match its expected units and be joined by accession to a separately evidenced official SEC acceptance timestamp. Future/mismatched/unverified accession facts are excluded; GAAP concepts are not silently merged, corrected or converted into comparative investment scores. The reference retains its SEC accession source, fiscal period and form. Source-permission and AI-use flags stay separate. This is a deliberately bounded subset of company financials, not a complete financial statement or an invented historical company profile.
3. **Issuer events:** existing accepted EDGAR filing events remain exact CIK/source/time bound; these are research leads, never proof of a share price move.
4. **Current scanner:** read-only `UniversalMarketGateway.owner_research_packet()` may add the provider IDs and observed-at evidence for an actually approved, current, session-verified observation at the *same* research time. The combined record never embeds a raw broker quote, independently executes an order, assumes optionability, or promotes an event/history into current price truth. A missing provider stays NOT_CONNECTED/EVIDENCE_PENDING.

Every record has `schema=OB_SYMBOL_RESEARCH_RECORD_V1`, as-of, identity, individual source states, no-candidate/admission/no-execution flags, independent provenance and explicit history-not-live and option-entitlement markers. Querying an earlier date than captured identity leads to FUTURE_IDENTITY_HOLD; it cannot conjure backdated ticker metadata.

## Historical scenario laboratory

`replay_historical_horizon()` separates its 20-session *formation* from subsequent *outcome* bars at a selected historical cutoff. Future bars never enter the formation computation. Its return is an **unpriced retrospective close-to-close diagnostic**, with `trade_count=None`, `win_rate=None`, `strategy_pnl=None`, no implied fill, costs, slippage, dividend treatment beyond declared adjustment basis, option backtest, survivorship proof, calendar certification or trading prediction. Insufficient lookback/outcome is an explicit hold. A recorded result from this tool must not be called a strategy P&L or an actual trade.

A fully valid years-long history requires the provider to supply actual licensed, completed, source-consistent data. The code does not assert that a free provider supplies five years or full consolidated history. Adjusted historical data requires separately documented corporate-action/adjustment methodology.

## Existing-engine read-only adoption

`research_bridge.py` defines the nonpromotable `OB_RESEARCH_HANDOFF_V1` envelope for Equity Engine V2, Options Intelligence, Candidate Fusion, Intelligence Fusion V2 and Soulaana, plus Market Map, Symbol Page, Trade Center and Review Center. It does not modify decisions, rankings, signal/option pricing, risk overrides or engine admissions; an independent canonical source/evidence and Tower review is mandatory.

`engine_v2/research_context_adapter.py` adds a distinct `research_context` to already-built engine outputs or selected/spotlight/rejected universe rows by exact matching symbol. Existing keys, score, candidate ordering, position and permissions remain untouched. `engine_v2/symbol_page_integration.py` accepts an optional record for the existing Symbol Page builder; absent a real server record, old behavior is unchanged.

`research_memory.py` supports a transient in-memory source-*reference*-only ledger. It refuses unreviewed history/fundamental retention and excludes issuer-event caching pending specific retention rights. It does not persist quotes, financial values, API tokens, account identifiers or trading instructions. Production Archive Vault/Tower persistence requires separate approval, transactional receipts, expiry/revocation propagation and retention policy. Soulaana receives permission-filtered context; no financial values if financial AI-use is denied, and no historical numeric values if historical AI-use is denied. Soulaana's source brief is deterministic and cites original evidence; she cannot create price facts or override Tower.

## UI placement and condition

The four protected room templates have a **conditionally rendered**, dark celestial, source-bound research panel through `ob_research_context_partial.html` and `ob_research_context.css`. Their matching room name and trusted server-injected `OB_RESEARCH_HANDOFF_V1` are required. No data present → no populated panel; no client-side API, dynamic scraping, synthetic live price, browser approval or new trade control. The Market Map receives bounded summary only; Symbol Page receives investigation detail; Trade Center receives non-promotable context; Review Center can show source/replay provenance when supplied. Actual hosted Tower route handlers must selectively pass those server projections after enforcing account/session/owner/invitee rights, canonical data freshness and source provenance. The source-only template inclusion does **not** mean the live site is now displaying this record.

## Acceptance before real owner beta

- Reviewed exact provider business/internal non-display, owner display, AI, historical data retention and invitee redistribution rights; do not infer these from a free personal API key.
- Verify official source, true quote/filing event time, daily bar completion, directory/CIK identity and option-series entitlement independently.
- Separate actual account/trading mode permissions, market data freshness, candidate sufficiency, risk and broker-side execution checks. No historical bar or filing permits an order.
- In hosted Tower branch, integrate only the approved source and optional panels from this PR, reconcile concurrent UI work (#166, #169, #177), avoid wholesale source merge and keep exact protected routes/default deny. Never deploy stale/demo/fixture market values as current.
- Run real independent backend/provider entitlement tests when approved, then an owner login, Dashboard → Market Map → Symbol → Trade → Review and Data Desk walkthrough. Without live entitlements, mark UI unavailable rather than pretending this source-only work activated prices.

## Tests

`python -m pytest -q tests/test_obscan001_025_sovereign_intake.py tests/test_obscan026_040_universal_gateway.py tests/test_obscan041_055_market_data_desk.py tests/test_obintel001_030_symbol_research.py tests/test_obscan_public_edgar_fetch.py`

All newly authored prices/issuers in tests are **synthetic fixtures** only. The dedicated CI also compiles modules and confirms no yfinance/network/broker execution path in new market research code.
