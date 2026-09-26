# OBCAP011–015 — advisory Capital Modes, source-bound review and hysteresis

Parent: `24a961e4b529fbf36655fbfdd381eb7791edc7d6` (OBCAP006–010 accepted).
Canonical read-only projection: `OB_CAPITAL_MODE_REVIEW_V1`.

## Scope
Six **advisory** labels: ACCUMULATE, BALANCED_GROWTH, PROTECT, SURPLUS_GROWTH, HARVEST, RECOVERY. They are not Observatory's actual Survey/Paper/Manual/Hybrid/Automated trading modes and cannot modify those permissions.

Inputs:
- Existing owner-confirmed ATM Set 1/Set 2 plan and four-sleeve OBCAP006–010 waterfall, validated with all four OBCAP001–005 snapshots.
- Explicit owner-provided *review* thresholds: watch/protect/recovery-exit drawdown in basis points, hypothetical harvest minimum, indicative surplus threshold and consecutive distinct chronological review count. No percentages, capital release floors or profit promises are invented by the code.
- Explicit owner-declared current capital mode per sleeve. A source reference/hash is recorded but is not asserted to be independently authenticated.
- Optional prior immutable review receipt, strictly earlier than the next waterfall. Duplicate frames, tampered receipts and different policy hashes fail closed; policy change requires a fresh review chain. Receipt integrity **is not** external authentication.

## Advisory precedence and hysteresis
- Missing/stale/conflicted essential waterfall evidence → INSUFFICIENT_EVIDENCE, no numerical or mode claim.
- Protect-range and watch-range drawdown → immediate PROTECT_PRIORITY_OWNER_REVIEW; do not delay risk review to satisfy hysteresis.
- The owner's declared PROTECT/RECOVERY mode is treated conservatively: proposal moves through RECOVERY, never quietly auto-exits owner policy.
- Before surplus growth or hypothetical harvest, preserve the independently defined sleeve acquisition/operations target; shortfall recommends ACCUMULATE for **review**.
- Hypothetical harvest remains hypothetical. Positive profit observations do not establish settled funds.
- Non-PROTECT candidates must recur in distinct later review receipts **with a changed, per-sleeve underlying source-observation fingerprint** for the owner-set hysteresis count. Merely rebuilding a snapshot against unchanged source evidence at a later as-of does not advance the streak; it is marked `AWAITING_FRESH_SOURCE_EVIDENCE`. This is owner-review evidence only, not an authorization or system-state switch.

## Preserved architecture
The four ATM sleeves remain distinct; Set 2's targets remain higher and no protected floor, high-water history or commitment is rewritten. There is no cross-sleeve aggregation, real-money release, transfer, broker submission, acquisition affordability claim, trade-mode unlock, or alteration of the existing CAPSIM source.

The relevant downstream path remains `OB verified evidence → Tower authorization/redaction → Teller financial readiness → Tower-authorized Teller result → BuyBox`. This family creates no direct connectors. Material BuyBox deal-term changes require a fresh Teller-owned terms-bound assessment.

## Next dependency gate
An authenticated bank/broker/source adapter and provider-origin proof are not present. Before any REAL capital assessment or deployable acquisition calculation, separately establish external source verification, settlement, account-specific actual obligations and protected floor source authority. OBCAP's current values and proposed modes stay explicitly indicative until then.
