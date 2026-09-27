# BBX062–066 — Comparable Research / Valuation Evidence Lab

A source-only, owner-entered market research room across all seven universal BuyBox verticals. This is **not an appraisal, independent sale verification, recommended purchase price, lender valuation, or funding readiness**.

## Actual original-first workflow

An owner uploads a protected listing, sale record or comparable document using the dedicated `comparable_original` category. This evidence is excluded from the seller-diligence required-evidence score, so adding market sources cannot falsely mark a target acquisition more verified.

The owner transcribes the exact comparable subject ID, market text, written price, chosen vertical-specific denominator, listing-versus-reported-sale event kind, date and page/row locator. The original SHA-256, evidence ID and uploaded artifact ID are preserved. The app verifies the actual encrypted original again before recording. Received records are owner transcriptions, not external authenticated sold-property facts.

## Vertical-specific normalization

- ATM route/business: USD per included machine
- Multifamily: USD per unit or square foot
- Commercial property: USD per square foot
- Laundromats: USD per machine
- Land/farm: USD per usable acre
- Operating businesses: recorded price / documented annual earnings (unverified descriptive ratio)
- Equipment: USD per asset unit

Like-for-like descriptive cohorts require identical vertical (opportunity scoped), selected basis, exact case-insensitive owner market text and **the same source kind**. Listings and reported closed sales are never mixed. At least two distinct comparable subjects are required before showing the observed minimum, median and maximum. A single record returns INSUFFICIENT_DISTINCT_SUBJECTS, not an invented average. No geocoding, freshness policy or market-size equivalence is guessed from text. The actual earliest/latest source-event dates are shown so users can identify old evidence.

Potential duplicate subject/event records are blocked pending correction review. An owner can append a documented correction only for the same comparable subject, market, source kind, basis and event date, and must give a reason. Previous source records and digests remain available in history.

## Authority and Soulaana

Soulaana can explain real cohorts, exactly which source IDs contributed, why categories were kept separate and where source depth is insufficient. She cannot declare a target value, select a seller/source as truth, bypass Deal Integrity, approve a bid, mark a reported sale independently verified, consult OB balances or authorize acquisition. Teller money and management readiness remains UNKNOWN.

This pack performs **no web scraping, licensed third-party feed access, outside seller communication, real property appraisal, closing confirmation, bank/Teller request, Vault archival or Render deployment**. Real external APIs, location normalizations, subject verification and approved valuation-policy overlays are separate future integrations.

## Tests

Run `python -m unittest discover -s buybox/tests -v`. Coverage includes every registry vertical, unsupported metric gates, original-source hashes, split listing/sale cohorts, duplicate subject handling, immutable corrections, dates and amounts, Soulaana provenance, authentic encrypted upload, protected web routes, tampering and no fictional production records. Fixture documents exist in temporary test directories only.

Coordination: this PR modifies only BuyBox code/UI/tests and this document. Keep the main Observatory/Tower runtime and Render workspace unchanged. PR #26 remains the dedicated umbrella source branch.
