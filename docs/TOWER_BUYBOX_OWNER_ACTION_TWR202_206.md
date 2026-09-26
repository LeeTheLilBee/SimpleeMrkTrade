# TWR202–TWR206 — Tower BuyBox action draft and owner preflight

**Source-only contract. No live BuyBox owner launch or production receiver.**
Base: dedicated Tower branch at 1120b9ca2b6d75a5aa9b0fd50bfc727edc6727b6, after TWR201.

## Actual source reviewed

BuyBox draft branch buybox-universal-acquisition-foundation-bbx001 at
f227a051429799c5b174b04129b58e4b0ab1e247: buybox/INTEGRATION_HANDOFFS.md,
buybox/core.py, buybox/registry.py, buybox/contracts.py and buybox/workflow.py.
PR #26 is not merged here; its local owner password is temporary development
access and is not the permanent Tower identity. BuyBox's readiness remains UNKNOWN
until real authenticated Teller/Tower source integration.

## New versioned source-only interfaces

1. tower.buybox.action.v1 — exact-field untrusted draft; versioned request,
idempotency/correlation IDs, opportunity ID and revision, input SHA-256 digest,
one of seven actual BuyBox vertical IDs, client-claimed actor and entity
references, explicit action/purpose, issued-at and valid-until, and asserted
classification. Draft lifetime <=300 seconds. Unknown fields, invalid purpose,
expired/future/naive timestamps, changed revision/digest or unknown actions
fail validation. Claimed references, digest and classification are not verified
source evidence or security authority.
2. prepare_buybox_action_review — returns request fingerprint and action
class with state UNTRUSTED_DRAFT; no approval, receipt, signature, readiness,
transaction or external call.
3. draft_matches_current_opportunity — equality test only. Production caller
must load true current opportunity/revision/digest using an authenticated
adapter, never accept caller-supplied comparison data.
4. tower.buybox.owner.preflight.v1 — reads existing canonical Tower session,
step-up, hosted owner identity and app truth. Reports blockers without exposing
secrets. Even synthetic all-green inputs cannot issue a handoff: the real
receiver and secure storage have not been certified. This module adds no route,
token, identity system or entitlement.

## Required remaining cross-system execution gates

- Owner doorway: only after an independently deployed and verified private
BuyBox receiver, exact Origin, persistent encrypted storage, backup/restore,
source publication/health, explicit entitlement, session/step-up, one-time
issuer-bound handoff, replay denial and safe return. Then implement and test
/tower/launch/buybox, rather than labeling a stub as launchable.
- Protected action: actual Tower policy decision derived server-side from
principal/entity/action/resource/purpose/classification/current revision/digest,
TTL/owner approval and audit/decision receipts; must invalidate on material
change. Local draft formatting is not an authorization.
- Teller: authenticated deal-terms fingerprint and money+management readiness
only from Teller, never direct BuyBox→OB or cross-sleeve pooling. Preserve ATM
Set 1 / Set 2 and protected floors. Missing, stale, conflicted or changed
terms => UNKNOWN / blocked.
- Vault: current metadata-only PR #35 caller-supplied Tower-context booleans
are not a live security gate. Require actual Tower-derived permission, secure
original transfer, malware scan/quarantine, Vault independent storage/receipt,
retention, correction lineage and protected download. PR #38 storage provider
is not connected. Preserve CSV MIME allowlist mismatch.
- Grounds, SimpleeOnTheGo and Clouds: scoped/permissioned read-only projections
and two-phase idempotent close-to-operations receipt+acceptance. Soulaana
explains source-bound facts only; cannot approve or execute.
- Hosted Teller v2 owner crossing remains issue #25 until real user and
shared-secret/receiver proof; do not mislabel the CI synthetic verifier as
live acceptance.

No Observatory, Teller, Vault, Grounds, ATM, Clouds, BuyBox or Render mutation
in this pack. No live financial action, contract signing, property/title
transfer, broker execution or unlocked trading mode.
