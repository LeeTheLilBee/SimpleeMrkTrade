# BBX067–071 — Source-bound Owner Decision Desk

This is a **private analytical research disposition**, not Tower authorization, a binding LOI, a lender approval, verified closing, or a change to OB/Teller account authority.

## Actual owner flow

The owner enters a real saved opportunity and reviews current evidence, diligence, source discrepancies, documented financing alternatives, source-backed comparables, and open tasks. The Decision Desk summarizes those existing records and provides four owner research choices: WATCH, DEFER, REQUEST_EVIDENCE, or DECLINE. Its form accepts a rationale and references to existing evidence IDs from the same opportunity, which are **citations only**. It does not send a seller request or automatically complete tasks.

On submission, BuyBox reads the exact current persisted opportunity revision and SHA-256 digest from its versioned store, verifies the owner-bound action is against that current source, and records the choice, rationale, allowed evidence IDs, current analytic findings/summary, source revision/digest and new local note digest. The note is stored via normal optimistic-revision history and remains visible as historical research if the opportunity later changes.

Stale web forms, forged source data, invalid reference IDs, missing actor/rationale and attempts to submit `APPROVE_ACQUISITION` are rejected. The actor is derived server-side from the existing private local owner session or verified Tower owner session; it is never supplied as an arbitrary form field. The source cannot be silently altered to match the note.

Soulaana can describe these exact notes, their source revisions and citations, current missing evidence and unresolved contradictions. No local note overrides those gaps or grants money and management readiness.

## Explicit non-authority

- `authorizes_purchase`, `authorizes_offer_or_loi`, `authorizes_closing`, `transmitted_externally` and `updates_lifecycle` are all false.
- Teller money readiness and management/capacity remain UNKNOWN until authenticated, source-bound external verification exists.
- Tower governs session, step-up, exceptions, contracts, and protected action execution. No BuyBox-local decision note is accepted as a Tower receipt.
- No OB trading/mission balance access, source upload to Vault, seller contact, lender communication, property handoff, acquisition close, or external actions are initiated by this pack.
- This room intentionally avoids an Approve Acquisition button. Actual approval/decline with contractual effect requires a separately implemented verified Tower workflow.

## Files and tests

`buybox/decision_desk.py` owns immutable local note generation and current-source checks. `app.py` adds protected GET/POST rooms using the existing owner login and CSRF. `decision_desk.html`, dossier and Deal Room links, Focus and contextual Soulaana explain the real saved records.

Run `python -m unittest discover -s buybox/tests -v`. New unit and authenticated web tests cover all seven verticals, saved-source digest and revision binding, historical state, exact evidence citations, forged approval/actor/digest attempts, stale submissions, CSRF/access control and grounded Soulaana output. Fixtures exist solely in temporary test databases.

Integration note: This PR changes only BuyBox source code, templates, tests and this document. No external contracts or hosting permissions are implied. Owner-selected Render workspace remains `tea-dag3rfu1egvs73a6s72g` and BuyBox must launch through Tower. This is source work for a PR into BuyBox umbrella branch #26, not permission to merge into main or deploy publicly.
