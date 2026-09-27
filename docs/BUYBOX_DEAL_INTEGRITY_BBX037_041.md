# BBX037–041 — Deal Integrity / original-document discrepancy room

Status: Draft PR #62 into BuyBox's dedicated working branch. No live external
source feed, Tower authorization, Teller capital grant, Vault archival or
production deployment is authorized by this work.

## Real owner workflow

1. Owner brings an actual opportunity and uploads a supported private original
   to encrypted BuyBox intake. The original is retained under its exact SHA-256.
2. In **Deal Integrity**, owner transcribes a statement with its exact source
   evidence ID, original artifact ID, subject (deal, serial number, parcel, etc.),
   registered field and unit, value, reporting period/as-of date, and page/row
   locator. Input is labeled SOURCE_RECORDED. This never rewrites underwriting.
3. Owner may review the original in the separate document-review step. Once the
   actual original's evidence revision is DOCUMENT_SUPPORTED, a claim may receive
   an append-only OWNER_DOCUMENT_REVIEWED successor, including rationale.
   The old claim/review and old original evidence ID remain traceable.
4. The core compares only current claims with matching subject, field, topic,
   unit and exact period/as-of date. Different normalized values become a
   source discrepancy; equivalent formatting does not. Historical price changes
   at different dates are NOT falsely treated as contradictions.
5. A documented correction can supersede a current claim in the exact same
   scope with an explicit correction reason. The earlier value is preserved.
6. Unresolved discrepancies block analytical qualification, without silently
   choosing a winning document or changing seller price, ATM ownership,
   financial metrics, protected money or approval. Soulaana points to the exact
   conflicting claim IDs. Focus shows actual saved claim and review events.

## Current registered fields

- ASKING_PRICE (USD, point-in-time)
- ANNUAL_REVENUE / ANNUAL_EXPENSES (USD, exact 365/366-day reporting span)
- INCLUDED_ASSET_COUNT (integer, point-in-time)
- OWNERSHIP / CONTRACT_ASSIGNABILITY (text, point-in-time)
- OTHER (explicit topic, text, point-in-time)

Unknown remains unknown. Received and owner-reviewed document labels are
different from independent verification. A seller's assertion can never be
automatically promoted to a verified claim, an accepted financial input, or
a Tower-granted exception.

## Source binding and invalidation

Every claim originates from an uploaded artifact paired to an exact evidence
revision and original digest. A later evidence review may supersede the
RECEIVED evidence ID; the claim-review path validates its exact same-original
successor rather than losing provenance or trusting an arbitrary other file.

Recording or reviewing source claims calls existing material-change invalidation.
It clears any stored readiness/authorization caches, retains append-only
opportunity revisions and audit events, and makes source changes visible to
the actual owner and Soulaana.

## Deliberately not implemented / separate authorization

Owner adjudication between genuinely contradictory sources needs an approved
future policy and, when relevant, independent title/professional verification
plus a Tower-scoped decision or exception. This pack does not mark discrepancies
resolved because a user clicked one source. It does not read OB directly,
recalculate protected floors, send data to Teller, contact sellers, transmit
original bytes to Vault or create real escrow/closing permissions.

## Verification

Run `python -m unittest discover -s buybox/tests -v`. Added tests for two real
originals contradicting, like-for-like period comparisons, human review
successor lineage, append-only correction, cross-system invalidation, source
references in Soulaana, actual authenticated browser intake, stale revision and
unauthorized access. All fixture files/values exist in ephemeral test folders
only; the actual owner database remains empty until entered by the owner.

Integration guidance for other build chats: This pack changes BuyBox-only files
(`claim_register.py`, `core.py`, `app.py`, `soulaana.py`, `focus.py`,
templates/styles/tests). It introduces no new Tower, Vault or Teller API.
Refer to PR #62 instead of copying code directly into parallel branch heads.
