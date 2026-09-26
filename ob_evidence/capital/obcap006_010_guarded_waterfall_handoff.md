# OBCAP006–010 — guarded mission-capital waterfall rehearsal

Parent: `6c6b5ce2143775dc5a97f8672b66548e1ac938e0` (OBCAP001–005 accepted).
New derived/read-only authority: `OB_CAPITAL_WATERFALL_PROJECTION_V1`.
Canonical inputs: four independently verified OBCAP truth snapshots, one explicit `simplee_on_the_go_atm` account, matching UTC as-of and unique scope references, and owner-confirmed *reference* to the existing ATM policy revision.

## ATM doctrine preserved
- Set 1: Acquisition/Growth 1, Operations/Vault Reserve 1.
- Set 2: Acquisition/Growth 2, Operations/Vault Reserve 2.
- Set 2 acquisition target must exceed Set 1 acquisition target, and Set 2 operations target must exceed Set 1 operations target. No pooled balances or fallback from one sleeve to another.
- Protected floors and the owner plan are **inputs**, never rewritten. Plan fingerprint is integrity metadata, not independent proof that a source is externally authenticated.
- Rehearsal ordering per sleeve: gross indicative settled cash minus the more protective of the existing floor, observed base-plus-reserve or explicitly proposed tighter floor, minus commitments and pending distributions. Clamp the resulting *planning scenario* at zero. Missing, stale or conflicting essential inputs prevent numerical projections rather than inventing zeros.
- The high-water projection is `max(previous owner-provided high water, indicative current account value)`. Report drawdown separately. This is a **candidate**, never an automatically adopted ratchet.
- Harvest number is hypothetical only and requires current indicative surplus and *realized* profit; capped by both and the planning scenario amount. A positive number never authorizes a transfer or claims externally authenticated funds.
- `funded != finished`: planning target arithmetic is not real acquisition readiness or completion.

## Teller/BuyBox handoff
The existing source authority `OB_ACCOUNT_IDENTITY_TRUTH_V1` and OBCAP001–005 source-bound truth are the relevant upstream contracts. `waterfall_reference()` deliberately emits a **non-money-bearing**, Tower-authorization-required proof reference, not a spendable balance. Teller remains the independent financial administrator and owner of acquisition/readiness outputs. BuyBox may only consume a Tower-authorized **Teller** readiness record and must ask Teller again whenever material deal terms change. There is **no** OB–BuyBox connector, no Teller implementation, and no Tower or policy changes here.

## Explicit non-authorities
No real external source verification yet; `CURRENT` in OBCAP still means indicative source evidence. No automatic floor/owner policy change, harvest execution, broker order, vault-cash movement, financing approval, readiness verdict, Manual Live/Hybrid/Automated unlock, mode change or deployment.

## Next family
OBCAP011–015: non-executable capital-mode *recommendations* based on these verified planning receipts, with explicit owner-provided hysteresis thresholds, a prior accepted mode state, separate sleeve signals, and no mode switch or policy authorization.
