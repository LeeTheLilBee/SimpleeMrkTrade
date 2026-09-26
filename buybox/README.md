# BuyBox — Simplee universal acquisition intelligence

BuyBox is a separate Python package on its own feature branch in the currently
accessible SimpleeMrkTrade repository. Its target is a complete Zillow-like
cross-asset acquisition system, **not** an ATM-only product.

## Universal product boundary

BuyBox owns discovery, opportunity records, evidence and claim analysis, scenario
evaluation, policy judgments, negotiation/diligence/decision records and acquisition
memory. Its seven registered verticals are ATM, multifamily, commercial, laundromat,
land/farm, operating businesses and equipment. The same core serves all verticals.

- Teller supplies authoritative money-side deployment and management capacity; BuyBox never reads OB accounts directly.
- Grounds owns existing property operations and is the handoff/link destination for real estate.
- Tower owns protected authorization, external access and the Vault request boundary.
- Soulaana explains grounded evidence, calculations, conflicts, rules and next action; she does not approve, overwrite evidence or change policy.
- Vault is reached through Tower, never via a direct BuyBox implementation.

## BBX001 foundation (implemented)

- Versioned seven-vertical registry.
- Canonical opportunity records with separate lifecycle and attention states.
- Evidence manifest, distinct missing/claimed/verified/conflicted states and weighted coverage.
- Decimal-safe, fail-closed calculation and isolated illustrative ATM policy checks.
- Scenario calculation with no mutation of base values.
- Teller readiness and Tower receipt **shape contracts**, with explicit warning that authenticated issuer verification is still missing.
- SQLite current state, preserved historical revisions, per-revision digests, activity events, optimistic-concurrency checks.
- Source-grounded deterministic Soulaana brief placeholder, synthetic tests.

Open `buybox/preview.html` locally to inspect the presentation concept (all data is labeled synthetic).\n\nRun tests from repository root:

```sh
python -m unittest discover -s buybox/tests -v
```

## Important status restrictions

The code is NOT a complete V1, NOT a production-deployed app, and is NOT
connected to live listing feeds, bank/broker accounts, or live Teller/Tower/Grounds
services. A local authority-reference-shaped dictionary is not a verified
authorization. All protected actions remain blocked until real authenticated
integration is implemented. Registry settings and preliminary ATM thresholds
are proposals requiring owner sign-off. No protected floors have been invented.

## Full-product implementation plan

The foundation precedes the universal discovery and search surfaces, event/outbox
delivery, file/document storage and extraction provenance, complete rule/formula
registry, financing and portfolio analyses, detailed ATM and other vertical
calculators, full acquisition lifecycle, responsive mixed-layout UI, full Soulaana
context adapter, external integration certification and post-acquisition feedback.

Do not merge this feature branch into OB/Tower main without review and tests.
