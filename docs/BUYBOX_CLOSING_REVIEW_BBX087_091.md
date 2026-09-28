# BBX087–091 — universal Closing Review

This pack adds an owner-visible **Closing Review** room to BuyBox. It is a
source assembly and historical review workspace only. It does not create legal
title, lender approval, bound insurance, Teller readiness, Tower authorization,
settlement completion, funds movement, acquisition ownership or post-close
operational records.

## Why this exists

BuyBox already has real-record diligence, Deal Integrity, Financing, Insurance,
Decision Desk and protected-action source contracts. The missing owner
experience was one place to answer two different questions without blending
them:

1. **What is the current BuyBox source state?**
2. **What still requires another system or professional to establish?**

The Closing Review deliberately keeps those separate.

## Implemented owner flow

- Read the current persisted opportunity, critical diligence count, unresolved
  source discrepancies, document-linked operating baseline, current financing
  alternatives, current insurance records and open owner tasks.
- Treat source problems as local review blockers: missing critical diligence,
  unresolved contradictory originals, no documented financing option, every
  recorded financing alternative requiring source/price recheck, no recorded
  insurance source, no clean binder/policy source, open tasks and missing
  document-linked operating baseline.
- Always show separately that BuyBox itself does **not** establish:
  - Teller money readiness.
  - Teller management/capacity readiness.
  - Tower closing authorization.
  - Lender commitment.
  - Insurance actually in force.
  - Title, ownership, lien release or transfer.
  - Settlement/closing-agent completion.
- Allow the owner to freeze an immutable local Closing Review against the exact
  current saved revision and SHA-256. The review may cite one current financing
  alternative and one current insurance record and optionally capture an
  owner-planned closing date.
- Preserve selected source IDs/digests and their current review flags. Later
  opportunity revisions leave the old review visible as historical rather than
  rewriting it.
- The saved record explicitly states that it does not authorize closing, move
  money, transmit externally or advance lifecycle.
- Soulaana has a dedicated \`closing\` context that explains exact local and
  external blockers and cites the latest local review without turning it into
  permission.
- Focus Desk surfaces the real \`ClosingReviewRecorded\` event.
- Opportunity dossier links directly into Closing Review.

## What “source review assembled” means

A local source state without BuyBox-level source blockers is only a cleaner
research package. It is **not** a green light. Even then the external authority
list remains blocked/unknown until the owning systems and actual professionals
establish their truth.

This pack intentionally does not add a button that says Approved to Close.

## Cross-system boundaries

- **Tower:** owns authenticated step-up and protected closing authorization.
  A local review is not a Tower receipt. Future use of
  \`AUTHORIZE_CLOSING\` must bind the exact current source and independently
  verify the issuer/session/action/expiry.
- **Teller:** owns money and management/capacity readiness. BuyBox must not infer
  spendable acquisition capital from financing documents or OB balances.
- **OB:** remains behind Teller for acquisition-capital truth; no direct
  BuyBox→OB query or execution is added.
- **Vault:** local encrypted originals and digests are not canonical archive
  proof. Permanent proof remains Tower-mediated.
- **Grounds / SimpleeOnTheGo:** operational ownership/handoff occurs only after
  independently verified closing and receiver acceptance.
- **Soulaana:** explains records and gaps; she cannot approve, sign, waive,
  fund, bind coverage or select a source as legal truth.

## Testing

New tests cover:

- Empty all-seven-vertical source state never appearing green.
- Exact persisted source revision/digest binding.
- Immutable local review snapshots and later historical labeling.
- Current financing/insurance selection without promotion to approval.
- Foreign/stale IDs and stale forms failing closed.
- Local owner access/CSRF.
- Soulaana closing context and record citations.
- No lifecycle update, external transmission, funding or authorization.

Run:

\`python -m unittest discover -s buybox/tests -v\`

No paid Render resource, live Tower/Teller request, insurer/lender API, legal
closing service or external transaction is created by this pack.
