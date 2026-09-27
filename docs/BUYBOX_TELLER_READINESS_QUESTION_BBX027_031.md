# BBX027–031 — source-only Teller financing/readiness question

**Purpose:** prepare a financing question for the future authenticated BuyBox → Tower → Teller corridor, without interpreting Observatory account balances, overstating protected reserves, making a payment or promoting a locally shaped dictionary to Teller authority.

## Verified source boundaries

- BuyBox's saved opportunity revision and SHA-256 digest come from \`stored_source_snapshot\`, not a browser form.
- Existing BBX022–026 \`buybox.tower.action.outbox.v1\` remains the local UNSENT action record; this pack does not replace it, send it or create a second action/outbox authority.
- TWR202–206's exact \`REQUEST_TELLER_READINESS\` action/purpose remains the eventual Tower request; the new question is a separate terms proposal, not a signed Teller response.
- \`buybox/contracts.py\` is explicitly a **shape checker**, not issuer verification. \`buybox/core.py\` deliberately returns \`UNKNOWN\` for unconnected external readiness regardless of a seller/user-supplied response. Do not change this to READY.
- Teller's actual authenticated business-account money and manager-capacity readiness producer, protected reserve floors, and any OB-derived truth are to be mediated by Teller/Tower, never directly queried by BuyBox.

## New source interface

\`buybox.teller.readiness.question.v1\` derives the exact saved opportunity ID/vertical/revision/digest and its locally stored asking price. It combines them with explicit *owner-proposed, unverified* decimal terms (proposed purchase price, proposed debt/equity, closing costs, reserve, a proposed funding lane and opaque terms reference). Both the current revision and the complete normalized terms are committed to a SHA-256 fingerprint. No seller financial fact is silently declared verified merely because it was saved.

ATM questions must keep the proposed \`ATM_SET_1_ACQUISITION\` and \`ATM_SET_2_ACQUISITION\` sleeves distinct. Multifamily can only nominate an unverified Grounds acquisition lane; other verticals remain \`MISSION_ACCOUNT_UNASSIGNED\`. These are labels for a later Teller request, **not** balances, actual mission-account grants, deployable capital or reserve-policy evaluations. Missing, forged, cross-vertical, float-rounded, negative, nonfinite or excessively precise money terms fail local validation.

The question is \`LOCAL_TERMS_QUESTION_UNSUBMITTED\`, has a maximum five-minute validity, and exposes only \`UNKNOWN\` for money/capacity/Teller readiness. It has no Tower principal, verified Teller issuer, receipt, external dispatch or acquisition/capital permission.

\`recheck_unsubmitted_teller_readiness_question\` compares the packet/fingerprint to its contents and the actual current persisted BuyBox source, and returns \`STALE_OR_EXPIRED_LOCAL\` on revision/terms/source change or expiry. An apparently signed or approved extra field fails exact validation; this local routine cannot validate Teller authenticity or transition a protected acquisition stage.

## Group 4 remaining real work

1. Separately specify and implement a server-derived Tower authenticated deal-readiness request, bound to entity, opportunity, exact terms fingerprint, request ID and TTL.
2. Teller must return independently authenticated money **AND** management/capacity readiness, exact requested terms, protected floor/sleeve checks and current issuer receipt. UNKNOWN, stale or changed terms cannot pass as READY; do not pool ATM sets.
3. Keep Grounds rent invoice, checkout, receipt and reconciliation inside Teller, not inside a BuyBox request or untrusted Grounds status string.
4. Vault original transfer and retained immutable proof require real independent Tower/Vault issuer and storage/scanning; PRs #35 and #38 are preparatory, not certified live archival.
5. Two-phase idempotent Grounds and ATM operations take-over only after verified closing/title/contracts and independent acceptance, not a listing or local BuyBox lifecycle label.

**Owner instruction:** no paid Render provisioning, secrets or hosted BuyBox activation. GitHub tests and documentation only. See issue #42 and cross-system worklist #54.
