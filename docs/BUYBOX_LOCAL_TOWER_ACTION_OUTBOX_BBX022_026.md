# BBX022–BBX026 — saved-source Tower action draft outbox

**Source-only. No Tower submission, approval, Teller readiness or paid hosting.**

This pack follows the actual BuyBox BBX017–021 protected Tower receiver source,
while leaving Tower's live launch disabled. It uses the already-merged BuyBox
BBX016 `prepare_untrusted_tower_action_draft` and the exact Tower
`tower.buybox.action.v1` validator at Tower commit
`e7a309001ba0ababe25abfdf52c458924fe78fe9`.

## New module and exact state machine

`buybox/tower_action_outbox.py` adds a private SQLite table
`buybox_tower_action_drafts` with a unique local idempotency key and request
ID. The local retry key is distinct from the randomly generated idempotency key in the immutable future Tower wire packet; neither is authentication.
Each row contains the exact server-read stored opportunity revision,
verified local snapshot digest, canonical draft payload, immutable SHA-256
payload fingerprint, and preparation/expiry times. This is NOT a Tower signature
or source-of-funds verification; the caller-claimed actor and entity remain
untrusted until Tower independently derives authority.

The **only** possible states are `PREPARED_UNSENT`,
`STALE_LOCAL` and `EXPIRED_LOCAL`, enforced by a database CHECK
constraint. No API can set SENT, APPROVED, ARCHIVED, FINANCED or READY.
Each returned summary explicitly has `authorizes_action=False`,
`submitted_to_tower=False`, `tower_receipt_present=False` and
`teller_readiness=UNKNOWN`.

- Local preparation requires a fresh SQLite transaction and obtains a
  BEGIN IMMEDIATE writer lock before validating actual persisted source,
  idempotency and request insertion. It cannot silently commit a caller's
  unrelated transaction.
- Retrying an identical local idempotency key preserves the same request ID,
  source revision, digest and expiry. A different intent on the same key is
  an explicit conflict.
- A saved opportunity revision/digest change, missing/corrupt source, or
  expiry makes the old draft terminal. It cannot be silently revived by
  a retry or treated as a fresh approval. A new source-bound draft requires
  a new idempotency key and actual current source read.
- Historical packet JSON and payload SHA remain unchanged on reconciliation.
  The row records the local terminal reason and time.
- This module makes **no HTTP call** or live Tower/Teller/Vault/OB request.
  It is a pre-integration local source record; its row cannot be treated
  as an external workflow or archival receipt.

## Source-only testing

The independent CI wall checks creation, idempotent retries, changed deal
terms, corruption, expiry, persistent replay across separate SQLite
connections, invalid keys, fresh transaction requirements, forbidden
approval-state mutation and pinned exact Tower contract compatibility,
alongside the existing BuyBox/Vault and protected owner-exchange tests.
All scenarios use synthetic records, never actual family/business details.

## Next source pack

Design Tower's **authenticated** current-resource and policy adapter after
the owner/step-up/entitlement/BuyBox receiver corridor is independently
verified. It must re-fetch the actual BuyBox snapshot, derive actor/entity
inside Tower, verify exact action/purpose/classification and record the
issuer-bound decision/denial. A local PREPARED_UNSENT row cannot be
promoted by an external JSON-shaped string; create a distinct verified
receipt registry after real authorization/transport exists. Then design
Teller terms-fingerprinted money+management readiness (no direct OB),
Tower-mediated Vault original transfer, and two-phase Grounds/ATM close
handoffs. Do not invent readiness or execute any acquisition.
 
**Owner hosting instruction:** continue in GitHub only. No new paid Render
service, disk, database, object storage, credentials or production BuyBox
activation unless the owner grants fresh explicit approval. See issue #42.
