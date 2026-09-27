# OBATTN001–005 — source-bound, owner-only attention queue

Exact parent: `54bbac772093fd734ba7241364bab50c8c11253e` (accepted OBSOUL001–005).

`OB_OWNER_ATTENTION_V1` consumes the complete verified Soulaana/OBREC→OBSAFE lineage, with an optional same-recommendation OBGUARD receipt and independently reverified guard evidence. It creates deterministic, immutable owner-inspection cards with source receipt IDs and integrity fingerprints. There is no alternate safety engine or position/trading recommendation engine.

## Priority rules
- P0 canonical BLOCKED state: retain canonical safety reason codes and inspect the block.
- P1 verified OBGUARD repeated-distinct-source assertion: owner inspection of **source assertions only**, never claim actual broker incidents or automatic kill switch.
- P2 canonical EVIDENCE_PENDING state: surface missing/held source reasons.
- P3 OWNER_REVIEW_READY: offer owner inspection, never imply order authorization.
- P0 always precedes P1. Missing guard records never imply safety. Replayed identical source payloads are already deduplicated by OBGUARD and cannot manufacture P1. The queue never changes canonical recommendation state or relaxes an existing restriction.

No live notification dispatch, automatic action, acknowledgement/dismissal affecting safety, broker submission, capital movement, policy/mode change or direct OB–BuyBox connection. A non-money-bearing reference requires Tower authorization. Teller alone owns deal-specific money/readiness and BuyBox must re-request it when acquisition terms materially change.

This pack adds the source/queue contract and regressions, **not** an installed hosted notification service or complete attention UI. Next: OBRES fail-closed source freshness, outage and recovery proof without reclassifying simulation as real capital.
