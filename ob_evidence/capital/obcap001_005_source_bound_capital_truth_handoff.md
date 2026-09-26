# OBCAP001–005 — Source-bound capital truth / Observatory–Teller–BuyBox boundary

**Parent:** `206cef29a046d01eee76446886dffa32c44fe09d` (accepted OBSIM006–010 and CAPSIM011–015).

## What is actually authoritative today

| Existing source | Canonical responsibility | What it cannot establish |
|---|---|---|
| `OB_ACCOUNT_IDENTITY_TRUTH_V1` (`web/ob_account_identity_truth.py`) | Explicit mission-account namespace, source-role and CURRENT/UNKNOWN/CONFLICT/STALE taxonomy | Account balance, settlement, broker verification, deployable acquisition cash |
| `OB_ENGINE_ACCOUNT_AUTHORITY_V1` (`web/ob_engine_account_authority.py`) | Existing repository operational vs projection vs historical source-role reconciliation, conflicts preserved | Bank/broker authenticity and spendable acquisition funds |
| `OB_CAPITAL_SIMULATION_V1` and `OB_CAPITAL_POLICY_V1` (CAPSIM) | Experimental simulation assessment and restriction-only pre-policy projection | Real account capital, actual bank funds, Seller/ATM cash availability or Teller readiness |
| Mission-capital rehearsal overlay (legacy `web/static/ob/ob_mission_account_capital_rule_rehearsal_overlay.js`) | Historical rehearsal and placeholders | An authoritative protected floor amount or live deployability decision |

No existing OB contract was found that authoritatively exposes **spendable acquisition capital** to Teller or BuyBox.

## New canonical OBCAP001–005 contract

`OB_CAPITAL_TRUTH_V1` in `web/ob_capital_truth.py` is a new, read-only, evidence-bound **monetary observation** authority. It consumes the existing account identity and source-role taxonomy; it does not create or select accounts and does not interpret acquisition affordability.

- Explicit account key **and capital_scope_ref** (e.g. an already-authorized sleeve reference); no silent mixing of ATM Set 1 and Set 2 or account-wide with sleeve-level balances.
- Thirteen separately observed money metrics: account value, settled cash, realized and unrealized P&L, protected base/reserve, committed, available growth/trading, maximum at-risk, harvestable, pending distribution, surplus. Missing **is not zero**. Realized and unrealized are never silently substituted.
- Exact integer cents; monetary values are source assertions, not proofs of external authenticity. Every observation binds source role, revision, evidence hash, observed/received/expiry UTC, account identity fingerprint and scope.
- Deterministic, immutable account/scope snapshot with CURRENT/UNKNOWN/STALE/CONFLICT per field, evidence lineage and tamper-evident hash. CURRENT means currently dated **indicative source assertion**, not verified bank balance.
- No authenticated broker adapter is wired in this pack. `BROKER_VERIFIED` is not an accepted self-asserted source role; no claim is promoted to deployable funds. Source hashes prove payload integrity *only*, not external authenticity.
- `capital_truth_reference()` emits statuses and proof identifiers without monetary values. No direct app connector, public route, account transfer, broker order or policy change.

## Teller consumption and acquisition readiness — boundary handoff, not a built integration

Correct authorized future flow:

`OB source evidence` → `Tower identity / permission / redaction / evidence mediation` → `Teller financial administration and deployment-readiness evaluation` → `Tower-authorized Teller result` → `BuyBox deal comparison`.

Teller can consume `OB_ACCOUNT_IDENTITY_TRUTH_V1`, source-role reconciliation and a **Tower-authorized, read-only** `OB_CAPITAL_TRUTH_V1` reference as provenance/context; it must obtain genuine external bank/broker settlement and account evidence through approved financial rails before asserting spendability. OBCAP's indicative numbers are **not** acquisition-ready money.

A future *Teller-owned*, deal-specific readiness contract should bind:
- `readiness_id`, `request_id`, entity/mission account, authoritative sleeve reference, buyer/role context and Tower authorization;
- immutable acquisition `terms_fingerprint`: price, down payment, vault cash, closing costs, debt/financing, repairs/capex, reserves, fees, contingencies and timing;
- money-source status/verified-at/expiry and provenance references, existing commitments and protected floors, actual deployable amount net of those obligations;
- `READY | REVIEW | BLOCK | UNKNOWN`, explicit missing/contested evidence and reason codes, owner-approval state, assessment as-of and hash.

BuyBox may ask Teller for new readiness **whenever material terms change**, invalidating the earlier terms fingerprint. BuyBox cannot read OB balance, infer acquisition funding from OB returns, trade, bypass Tower, or lower protected reserves. Teller readiness itself is not a trade/capital transfer authorization.

### Existing ATM capital doctrine stays unchanged
Set 1 = Acquisition/Growth 1 + Operations/Vault Reserve 1; Set 2 = Acquisition/Growth 2 + Operations/Vault Reserve 2. Preserve the alternate cycling design, Set 2's higher target, commitments, existing protected-floor/risk policies and independent readiness evaluation. No four new top-level OB account identities or hardcoded floor amounts are created here. An OBCAP scope reference is metadata only and cannot authorize a sleeve, alter a floor, or transfer money.

### Non-authorities
This pack does **not** modify CAPSIM policy, OB modes, Tower/Teller/BuyBox application code, OB trading execution, cash withdrawals, mission capital plans, or deployed endpoints. It does not claim the real-money program is fully broker-verified; actual provider integration and external verification remain an explicit later prerequisite. The contract is deliberately deny-by-default until then.

## Verification gates
Focused OBCAP and authority/event regressions, followed by all repository tests in a fresh CI runner. Preserve the source- and capital-authority dependency graph as acyclic. Merge only after exact-head checks and green CI.
