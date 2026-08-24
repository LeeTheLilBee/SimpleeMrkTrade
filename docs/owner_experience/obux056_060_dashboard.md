# OBUX056–060 — Canonical User Dashboard + Arrival / Session System

## Product boundary

The normal **Dashboard** is the signed-in user's OB account home.

It answers:

- What is happening in my OB account?
- What changed since I was here?
- What is my access state?
- What mode am I in?
- Can OB/Soulaana reach me?
- What activity or review is waiting?
- What market intelligence deserves a look?
- Where should I move next?
- Where are my account/session/beta tools?

The normal Dashboard does not own owner mission accounts.

The separate **Owner Dashboard** remains the owner operation / mission-account surface.

The separate **Owner Console** remains the system-health / source / safety surface.

## Arrival flow

1. Tower launches OB.
2. The real Dashboard exists behind a dark, blurred, inactive scrim.
3. Versioned Private Beta SOP appears when required.
4. Versioned What Changed appears after a meaningful beta revision.
5. Soulaana offers an optional session check-in.
6. OB offers a safe resume when appropriate.
7. Soulaana offers optional first-session guidance.
8. Dashboard reveals.

The SOP supports:

- left/right arrows,
- page dots,
- keyboard arrows,
- touch swipe,
- visible progress,
- focus trapping,
- reduced-motion support.

## Soulaana check-in

The check-in is optional.

It may collect:

- feeling,
- energy,
- focus,
- pace,
- session intent.

By default the response lives only in session-ephemeral storage.

A response enters private recent-session history only when the user explicitly chooses to use it in private session review.

The check-in may alter presentation density or pacing.

It may not alter:

- market truth,
- prices,
- rankings,
- contract selection,
- risk facts,
- source labels,
- execution,
- trade decisions.

OB does not diagnose the user.

## Canonical OB session

`OBSessionState` centralizes:

- SOP acknowledgement,
- What Changed acknowledgement,
- selected mode,
- active room,
- selected symbol,
- safe resume route,
- optional check-in,
- notification readiness,
- feedback context,
- reflection,
- return/signout reason,
- recent session closeouts,
- active tracked-position count,
- multi-tab lease.

This browser implementation is a versioned replaceable persistence boundary.

It is not a claim that browser storage is the final production datastore.

## Guided first session

Guidance occurs on the actual product surfaces:

Dashboard → Market Map → Symbol Room → Trade Center → Review Center.

It never sends a beta tester into proof/walkthrough pages.

## Feedback

The global beta feedback control captures:

- room,
- mode,
- symbol when relevant,
- build,
- SOP version,
- category,
- message,
- component context.

Until a canonical server submission sink exists, feedback is truthfully labeled as saved in the local OB beta queue and emitted as a structured browser event.

The UI never falsely says it reached a server.

## Tower controls

Every canonical OB room receives:

- Feedback,
- Back to Tower,
- Sign out of OB,
- mode state,
- Live Auto locked state,
- idle privacy cover.

Back to Tower preserves Tower authority and allows safe resume context.

Sign out of OB closes/clears OB-local ephemeral state and returns to Tower.

Full identity signout remains Tower-owned.

If OB is tracking a position, signout explicitly says that signing out of OB does not close an external brokerage position.

## Mode doctrine

Survey:
Observation and intelligence. No trade pressure.

Paper:
Simulated practice lifecycle.

Manual Live:
Owner-supervised.
OB prepares, alerts, tracks, and reviews.
The owner chooses and places externally.

Hybrid:
OB may narrow objective choices.
The user chooses the contract.
Execution remains separately gated.

Automated:
Locked.

## Legacy retirement

OBUX060 retires the historical OBUX006–010 `after_request` response-body substitution that replaced `/ob/dashboard` after the template rendered.

The canonical Dashboard is now the real template plus the source-backed projection and arrival/session system.

## Owner boundary

Mission-account scripts are explicitly absent from normal `dashboard.html`.

Owner Dashboard and Owner Console remain separate surfaces.
