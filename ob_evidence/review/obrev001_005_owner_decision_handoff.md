# OBREV001–005 — source-bound owner disposition and adverse review

Parent: `df7deac24085eba200a65d388ff829e8ad16d664` (OBREC001–005 accepted).
New canonical review-only authority: `OB_OWNER_REVIEW_EVIDENCE_V1`.

Consumes only a fully reverified OBREC→OBSAFE→OBSTRAT→OBPORT/OBPOS receipt with canonical market time/mode/owner-fit context as originally supplied. Explicit owner-provided DEFER, DECLINE, REQUEST_MORE_EVIDENCE or INTERESTED_FOR_REVIEW is stored as **owner assertion**, not a Tower-authenticated session. Interest for review is rejected unless upstream recommendation is OWNER_REVIEW_READY. Owner review cannot precede the bound market observation. The source hash is integrity metadata, not identity or broker proof.

Negative Dive, Overtime, Overreach and Source Gap are explicit source-labelled review issues and produce `ADVERSE_REVIEW_PENDING`; duplicates and unknown issues fail closed. Safety BLOCK/HOLD remains visible and cannot be overridden by owner interest. No automatic classification of adverse notes as realized trade results.

This pack does not ingest broker trade confirmations, assert actual fills, calculate actual profits, make transfers, set mode or risk policy, provide Teller acquisition readiness, connect BuyBox to OB, or deploy to Tower. A signed authenticated owner-session protocol is separately needed for privileged operations.

Next family OBREV006+ should attach independently verified outcome/proof records to actual owner/manual decisions only after the appropriate source and authorization gate exists. OBLEARN must consume only properly classified review evidence and may never relax hard stops or change policy silently.
