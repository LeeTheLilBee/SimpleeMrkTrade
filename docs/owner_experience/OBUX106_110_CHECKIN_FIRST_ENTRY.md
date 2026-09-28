# OBUX106–110 — Check-in-first Observatory entry; separate OB landing removed

Owner direction: Tower launches OB → **one in-place popup carousel** (welcome, versioned beta boundary as needed, Soulaana voluntary check-in, enter) → **actual Dashboard**. No second OB login, marketing splash, proof page, extra landing click, forced multi-modal parade or redirect to a different account/room. The Dashboard renders under an inactive privacy blur until the check-in completes.

## Implemented in the OB main-based candidate
- `dashboard.html` mounts `#obArrivalRoot` and first-paint `ob-entry-pending`, loads the new `ob_checkin_entry.js/css` and drops the old arrival script from active template. Historical `ob_session_arrival.js` is retained in source for audit/rollback; never load both on the same page.
- One responsive, accessible original celestial modal. Steps: Welcome; mandatory **explicit beta boundary** acknowledgment for an unacknowledged SOP version (or concise What's Changed for new version); optional feelings/energy; focus/pace; session intent/opt-in private-review retention; Enter the Observatory. Progress indicators and Back; Skip check-in only bypasses optional questions and does not bypass the unacknowledged beta boundary.
- `OBSessionState` is reused for `acknowledgeSop`, `acknowledgeWhatsNew`, `saveCheckIn`, `skipCheckIn`. No second persistence authority. Voluntary answers are presentation context only. No market truth/risk/contract/ranking/mode changes, medical inference, owner permissions, trading/broker API/capital transfer.
- Returning to Dashboard from an existing same-origin `/ob/` product room skips repeat questions when the session already checked in; a fresh Tower arrival (or `/ob/dashboard?ob_arrival=fresh`) presents the entrance again. A fresh URL marker is cleared on successful completion. On a failed popup render, keep the Dashboard covered and offer return to Tower.
- Original CSS nebula/orbit composition only; no user-provided photos, stock/watermarks or arbitrary generated financial values; reduced-motion/mobile/high-contrast support.

## Tower receiver/integration handoff — NOT included in OB main changes
**Tower stays the front door.** The production-candidate Tower branch is separate and selectively imports Observatory sources. Its real guarded `/tower/launch/observatory` → `/ob/dashboard` path must serve the exact merged Dashboard template and these new two static files while preserving session, step-up, operational launch receipt, owner/normal role separation, default deny for unknown `/ob/*`, back-to-Tower/sign-out and no direct public entry. Do not replace Tower `/`/login page with an unguarded OB popup. Remove a second *OB* landing/marketing splash if one currently intervenes. No new service, deploy setting, paid plan, secret or auth bypass is permitted by this source PR.

On the canonical dedicated Tower branch, add an exact revision manifest plus anonymous-denied and owner-session positive/negative HTTP tests (anonymous, wrong session, expired step-up, old owner claim, replay/revocation, logout, wrong-origin). Then owner personally verifies full carousel and actual Dashboard. Do not claim hosted acceptance from the main-branch template or source CI.

## Acceptance matrix
1. Tower launch is the only authorized initial owner entry; no double login or separate OB splash, and `/ob/dashboard` shows just the popup over the real Dashboard.
2. First launch presents versioned beta/SOP boundary with explicit checkbox; Skip check-in cannot circumvent that acknowledgment. Existing acknowledgment avoids re-reading the SOP on every product-room return.
3. Every optional question may remain blank; Skip marks skipped; Continue marks completed; review-memory is explicit opt-in; same-origin product-room Dashboard return does not reopen unwanted carousel; Tower re-entry/replay does.
4. Keyboard Tab stays inside modal, focus is visible, all choices labelled, Enter/Back work, reduced-motion and small viewport work. No underlying Dashboard interaction until finished.
5. On failure, no accidental product disclosure/unmasking; Back to Tower remains available. No live trade/Manual Live permission from an arrival form.
6. No invented broker/market/capital state; source and hosting releases remain separately verified. Owner browser acceptance recorded with exact hostname and SHA.

### Source boundaries
`main` is the Observatory source authority for the interface. Canonical hosted Tower is currently on the dedicated `tower-hosted-runtime-identity-twr081-085` branch and has its own guards/integration route. Do not merge two branches wholesale or configure the separately failing main-based Render build as a shortcut.
