# Soulaana source health, event timeline and opportunity-triage foundation

This is the next read-only stage of the existing Official Catalyst Radar, not another scanner, data license, API connector, trade recommendation engine or automatic order router.

## The narrow capability

The same authenticated Tower owner GET /ob/research/catalysts.json now includes soulaana_provenance_triage:

- Source health: the six exact source identities, state (SOURCE_BOUND, NO_PUBLICATION, SOURCE_HOLD, KEY_REQUIRED, REVIEW_HOLD, or delegated SEC), count of records in this validated response, whether cached, and latest source period.
- Period meaning: Federal Register publication date, CFTC report-as-of date, EIA weekly series observation, World Bank annual year, NWS alert effective time. None is blindly relabeled as a live market observation or HTTP retrieval date.
- Bounded event timeline: only source facts that currently have independent reviewed Soulaana-content permission. Up to 12 actual dated record descriptions with publisher link, source identity and last successful fetch change marker.
- Same-series comparisons: only the exact fixed EIA crude-inventory and World Bank US annual nominal GDP series can compute a previous-to-later numeric difference, in source-reported units. CFTC is a distinct futures-only positioning context; NWS effective timestamps and Federal Register stages are not numeric price signals.
- Source change markers: FIRST_OBSERVED_IN_PROCESS, UNCHANGED_SINCE_LAST_VERIFIED_FETCH, CHANGED_SINCE_LAST_VERIFIED_FETCH. A tiny in-process SHA-256 fingerprint ledger tracks validated source records by exact publisher document/alert ID or exact series+period/market+period. Changed does not prove an official revised release; it means the same identity's normalized returned record differed from a prior successful fetch in that one Python process. Cached owner reads do not create a new fetch. No durable ledger, personal records, background scheduler or new vendor API.
- Fail-closed source conditions: revoked source rights discard cached facts and that source's ledger fingerprints; no/failed publication does not reuse previous content or claim withdrawal. Separate AI permission gate prevents owner-display rights from becoming AI-content rights.
- Qualification handoff: SOURCE_CONTEXT_ONLY cannot claim issuer-specific matching, an entitled current equity quote, current licensed options chain, contract liquidity, capital/risk approval, owner acceptance or a ranked trade candidate. Soulaana explains the necessary independently verified next evidence.

## This is not live candidate selection

The eventual best-of-best flow is source context to issuer/identity truth to licensed underlying/options quote truth to options liquidity/risk and capital gate to review of qualifying candidates. This work implements the first stage and typed missing-evidence handoff, without putting fake zeroes or hypothetical candidates in production. Existing scanner/Capital Defense/Review Center contracts remain authoritative; no SourceRights permission is inferred from an official source.

## Boundaries and rights

Five existing source/indicator-specific reviewed flags remain necessary before fetching. EIA still needs a free registered key; World Bank indicator-specific exception review still required. No additions to permitted data providers, no FRED, FMP, Twelve Data or restricted commercial data, no web scraping, no external LLM calls. Both original provider URLs and timestamps stay visible to the owner only in this protected corridor; original content is rendered with textContent. BLS remains separately held; no replacement falsely labeled CPI.

## Acceptance checklist

Synthetic tests verify owner-only route retains exact Tower guard; 5 validated source receipts; cache behavior and source-specific change markers; changed values for same CFTC market+period; source ID tampering and duplicate denial; per-source revocation removing timeline/fingerprints; no AI approval giving no timeline or comparisons; candidate/readiness booleans always closed. GitHub Actions does not prove that an owner/browser session has opened the newly rendered cards. For hosted smoke tests, existing source use and AI gates remain the only enabled network sources; no extra background calls are made.
