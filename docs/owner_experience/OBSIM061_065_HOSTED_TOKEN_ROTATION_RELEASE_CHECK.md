# OBSIM061–065 — hosted owner rehearsal reset, session isolation, and release check

**Scope:** Tower protected, opt-in, synthetic Proof/Demo owner rehearsal already introduced as OBSIM056–060. This pack does not enable the hosted feature, add a paid service or change trading authorization.

## Problem and fix

The first hosted implementation reused the old workspace's process-local CSRF token when the owner explicitly selected **New synthetic rehearsal**. This allowed a stale old browser token to address a newly reset report namespace and contradicted the UI's claim that each rehearsal has its own token. There was also a narrow concurrency gap between the before-request token check and replacement/mutation.

The accepted reset now requires the previous workspace to have stopped, rotates to a fresh unguessable token, replaces the process-local workspace and returns `new_rehearsal_token` **only** inside the authenticated, origin-bound, token-checked successful reset response. All subsequent status/sample/mutation calls with the previous token return a denial. The browser immediately replaces its in-memory token; if reset acknowledgment is incomplete, it prompts re-entry via Tower rather than guessing success. Mutation and reset revalidate that the checked workspace object is still current and its token still matches **while holding the same lock**. A concurrent stale request cannot act upon a detached previous session.

Tests assert before-stop denial, actual accepted tick/final, old token denial, new token acceptance, Tower-session rotation isolation, private header/scope behavior and exact source boundaries. There is still no durable report archive, cross-worker guarantee or real market feed: the hosted beta is single-worker volatile memory, with restart/deploy loss disclosed in its UI. A full hosted owner/device walkthrough remains an independent acceptance gate.

## Current deployment decision

- Canonical owner URL must be identified from the existing services; there are two separate Render workspaces with `simplee-tower-ob` services. Do not update the service, origin or secrets based solely on its display name.
- Feature configuration remains default OFF: `OB_OWNER_REHEARSAL_HOSTED_ENABLED=1` requires a separately reviewed and exact `OB_OWNER_REHEARSAL_ORIGIN=https://<verified-canonical-host>`. **Do not set these before checking the actual owner entrance and runtime revision**. No mode, signed account, manual live or paid service is implied.
- Source CI and passive deployed version checks do not authenticate an owner's actual user journey or persist reports through restart. Real Manual Live/Hybrid/Auto remain HOLD and broker/financial readiness stays separately external.
