# BBX057–061 — Financing Desk: real written terms, no fabricated funding

Source-only, owner-entered Financing Desk for all seven BuyBox categories. Dedicated PR into the universal BuyBox working branch. Does not alter Tower, Teller, OB, Grounds, Vault, or hosted Render services.

## Workflow and scope

1. The owner uploads a **real original** lender letter or term sheet as the additional `financing_terms` evidence kind using existing private encrypted intake and authenticated original download. This evidence is *not* a new universal required-diligence category and does not artificially increase vertical evidence-completeness scores. Original SHA-256 and evidence ID are preserved.
2. The owner transcribes actual written terms and source page/paragraph: lender/source label, loan program, document/expiry dates, price basis, principal, fixed APR, full amortization months, origination fee and other lender fees. Closing costs, proposed cash reserve and (ATM only) physical vault cash are owner-entered acquisition assumptions, displayed separately from the written terms.
3. BuyBox preserves option records append-only; a documented correction points to the current prior option and never changes historical source records.
4. Deterministic Decimal amortization models the monthly payment, annual payment, scheduled interest, aggregate cash requirement and an **unverified buyer funding gap**. Model only `FIXED_FULLY_AMORTIZING` in USD, 12–360 months. No invented balloon, variable-rate, SBA eligibility, draw schedule, escrow, tax treatment or prepayment assumption.
5. An illustrative operating/debt ratio appears only when there are already matching-period documented annual revenue and expense figures. This is not lender DSCR qualification or independent normalized NOI. Record/document date and changed asking-price basis are checked; expired, hash-mismatched or mismatched-price options show a visible recheck warning.
6. Soulaana explains actual saved options and source IDs; Teller's money and management readiness remains **UNKNOWN**, and there is no direct BuyBox→OB call or loan submission. Reserved cash and ATM vault float are liquidity requirements, **not booked as operating expenses**.

## Authority, missing capabilities and later integration

- Financing options are owner transcriptions of originals, not independently verified lender offers or final commitments. Documentary review is not bank credit approval.
- Existing BBX027–031 `buybox.teller.readiness.question.v1` is an **unsent**, source-bound question to be routed via Tower/Teller. This pack does not auto-create/submit a question or infer spendable capital from modeled cash gaps; a future owner-confirmed selection must rebind terms to a fresh opportunity snapshot and obtain actual independently verified Teller money **and** management readiness.
- Full variable/balloon/SBA/interest-only lender-specific products, committed quote status, real provider verification, closing escrow, rate locks, signed contracts, cash verification and owner authorization require separate explicit contracts. No new Render costs or external calls.

## Tests

`python -m unittest discover -s buybox/tests -v` runs the exact existing suites and adds financing arithmetic, original provenance, source/price/expiry invalidation, corrections, unsupported structures, reserve/vault liquidity treatment, encrypted-document protected user workflow, stale revisions, Soulaana citations and auth/CSRF. All test lender names/values/files are isolated temporary fixtures, never real product sample records.

## Coordination

This PR only modifies `buybox/financing.py`, `buybox/app.py`, `buybox/soulaana.py`, `buybox/focus.py`, the dossier and new financing UI, styles, tests and this document. It does not mint or ingest a real Tower or Teller receipt. Keep `main`, existing OB and Tower runtime untouched. The owner-selected workspace remains `tea-dag3rfu1egvs73a6s72g` but no hosted deployment is authorized by this pack.
