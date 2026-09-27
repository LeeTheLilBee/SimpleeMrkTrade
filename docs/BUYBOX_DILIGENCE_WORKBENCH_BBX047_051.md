# BBX047–051 — Diligence Workbench / real source and owner queue

This is a source-only feature for the full universal BuyBox V1, not an ATM
demonstration. It uses the current seven versioned acquisition manifests.
No external listing feed, AI document extraction, seller outreach, financing,
archive transfer, Tower approval or production deployment is introduced.

## Actual owner workflow

- Open an actual saved opportunity, then **Diligence Workbench**.
- Review every vertical-specific evidence category, its criticality, actual
  recorded evidence state, owner-entered source reference, optional original
  attachment and outstanding owner tasks. Unknown is shown as missing.
- Choose a date yourself for a requirement that is missing or not yet
  documented. This creates one persistent Deal Room task, attached to the exact
  vertical evidence kind and manifest version. It never sends anything to
  a seller. Further tasks are not duplicated while one is OPEN or WAITING.
- The task is updateable through the real Deal Room. Completing or canceling
  a task does not verify evidence. Conversely, uploading/reviewing a source does
  not auto-complete the owner's task or invent a deadline.
- Existing encrypted upload and historical evidence-document review remain the
  exclusive record of what was received/reviewed. The new room only links to
  those functions, including the original attachment when present.
- Soulaana's new Diligence tab summarizes the actual category counts, critical
  outstanding categories and real owner-entered task dates. She cannot mark a
  document reviewed, contact a seller, authorize a deal, or claim a Vault
  archival receipt.

## Data/authority contract

`diligence_snapshot(op)` derives all requirements from
`registry.get_vertical(op["vertical"])["evidence"]` at read time. It never
stores a parallel, manually edited requirement list.

`create_diligence_task(...)` explicitly records:
`workstream=EVIDENCE_DILIGENCE`, `evidence_kind`, the manifest version,
opportunity revision at creation, source evidence ID (if any), the authenticated
owner actor, actual owner-picked deadline and non-execution flags.

BuyBox task state and documentary evidence state remain **separate axes**.
An owner's document review remains documentary support only, not independent
professional verification or a purchase/funding permission. BuyBox continues
to depend on Teller for financial/management readiness and Tower for protected
decisions and access to Vault. No direct OB/Vault call.

## Tests and boundaries

Unit tests cover every registered vertical, no fabricated initial records,
recorded source statuses, no duplicate pending requirement tasks, owner task
revision/supersession, no auto-complete or auto-verification, strict input
validation and Soulaana's actual deadline references. Authenticated app tests
cover persistent task/event/UI, stale optimistic revisions, missing CSRF,
unauthorized access and owner contextual explanation.

All fixtures live in temporary test databases and never populate the owner
product. This pack touches only `buybox/` source, tests, template and CSS.
It is designed to merge into BuyBox's dedicated branch after its checks pass;
it does not modify Tower or the active Render service.
