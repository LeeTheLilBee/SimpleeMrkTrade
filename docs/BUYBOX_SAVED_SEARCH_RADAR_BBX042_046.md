# BBX042–046 — Owner Saved Searches / Opportunity Radar

Status: isolated BuyBox source PR. No marketplace feed, background polling,
scheduler, external alert delivery, financial action, or new hosting resources.

## Owner experience

BuyBox's existing Browse filters can be saved as a durable owner-named view.
The supported fields are vertical (any of seven registered categories or all),
search phrase/city, and optional maximum documented asking price. An unknown
asking price cannot be silently treated as zero to satisfy a price filter.

A saved view alone creates **no notifications or observations**. The owner must
press **Check current BuyBox records**. The first check stores an exact source
revision/digest baseline and does not call existing matches "newly discovered".
Subsequent explicit checks compare persisted opportunity IDs + revision SHA-256
against the prior check and display:

- newly matching **saved BuyBox records**;
- matching records whose actual saved revisions changed;
- records no longer satisfying the saved filter;
- unchanged state as ordinary no-change information.

Each check is append-only; older checks and search archive history remain
available. A named search can be archived, stopping subsequent checks without
removing any opportunity. All check results explicitly report the lack of live
marketplace provider access or automated notification delivery.

The current site is owner-only. In Tower-hosted mode the actor identifier is
derived from the already server-side verified owner session, not a browser form.
Tower is still the permanent entry point; saved search routes inherit all
existing authentication/CSRF protection.

## Trust boundaries and storage

`buybox/saved_search.py` stores only validated filters, opportunity IDs,
revisions and their exact persisted snapshot digests. It does NOT copy sellers'
PDFs, encrypted local file paths, Vault references, full Opportunity objects,
OB account balances, Teller readiness, or third-party source payloads into
the search-result history.

`stored_source_snapshot` checks the current saved opportunity against the
immutable revision record/hash before an owner check can be recorded. An
inconsistent source fails closed. The compare-and-insert transaction uses a
SQLite IMMEDIATE write lock; schema initialization is statement-by-statement
so it cannot implicitly commit the in-flight comparison.

## Explicitly outside this pack

No scheduled web scraping or assumption that a source URL gives listing
permission. Provider feeds require authorized terms, a real adapter, source
revision/observation provenance, rate limits, dedup/versioning and Tower scoping.
Native map layers/geocoding and notification channels remain future work. No
external facts are presented as new market opportunities merely because the
local owner record changed.

## Testing

`python -m unittest discover -s buybox/tests -v` includes tests for empty/
baseline state, actual newly matching and revised local records, out-of-filter
changes, price and category filters, invalid input, protected/archived views,
read-only origin truth, immutable check history and corrupted source hash
rejection. Test fixtures never populate the actual owner's workspace.
