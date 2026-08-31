# OBUX086–090 — Owner Capital Lanes

Parent: `25497056d408197fe36a298c3e0d96953a5c0982`

## Product decision

The legacy Mission Account system is no longer a shared Observatory product feature.

Normal users do not receive it.

Owner capital context now lives only on the Owner Dashboard as **Capital Lanes**.

## OBUX086 — Legacy runtime retirement

Canonical product templates no longer load:

- `ob_mission_accounts.js`
- `ob_mission_account_capital_rule_rehearsal_overlay.js`
- `ob_account_experience.js`

Shared Settings no longer contain a Mission bar option or mission-layout state.

The product-surface policy denies legacy Mission Account UI on every canonical `/ob/*` route.

## OBUX087 — Owner-only Capital Lanes

Owner Dashboard owns six independent Capital Lanes:

- Trust
- Personal
- Simplee World
- SimpleeOnTheGo / ATM
- The Grounds / Apartment
- Proof / Demo

The Owner Dashboard contract no longer fetches `/ob/account-experience.json`.

Capital Lane policy lives inside the owner-only contract and may later consume only a verified owner-specific snapshot.

## OBUX088 — ADHD-friendly manifestation

The Owner Dashboard follows these interaction rules:

1. One dominant current-lane focus.
2. Other lanes appear as compact nodes.
3. Clicking a lane opens details only.
4. Context changes only after `Enter this lane`.
5. Only the top three owner-attention items are shown directly.
6. Deeper owner intelligence is collapsed.
7. Raw evidence remains behind `Show me why`.
8. No continuously orbiting animation.
9. Keyboard focus and Escape behavior are supported.
10. Reduced-motion preferences are respected.

Entering a Capital Lane changes owner context only.

It does not:

- move capital;
- place an order;
- choose an option contract;
- unlock Manual Live;
- unlock Live Auto.

## OBUX089 — Normal Dashboard cleanup

The normal Dashboard no longer displays:

- `Your OB account`
- `YOUR OB / Account snapshot`
- `ob-account-snapshot`
- `obAccountSnapshot`
- `obAccountSource`

Normal Dashboard begins with intelligence and next action instead of owner capital/account chrome.

## OBUX090 — Safety

Tower source remains untouched.

No broker execution capability is added.

Live Auto remains locked.
