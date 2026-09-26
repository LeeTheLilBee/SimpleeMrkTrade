# BuyBox BBX011–BBX015 — private hosted boundary and Tower receipt primitives

**Source-only foundation, not a BuyBox deployment or live Tower integration.**
Canonical draft product starting point: BuyBox branch
buybox-universal-acquisition-foundation-bbx001 at
f227a051429799c5b174b04129b58e4b0ab1e247 (PR #26).

## Verified existing product shape

- buybox/app.py uses a development-only local owner password and Flask cookie.
- buybox/store.py stores revisioned opportunities and history in SQLite.
- buybox/documents.py stores original records encrypted with a separately held
  Fernet key in a private directory. It is **not Archive Vault**.
- Current local run binds 127.0.0.1. Exposing the development server, local
  login, SQLite file or encrypted originals on an ephemeral host is prohibited.
- Acquisition stage transitions requiring Tower/Teller remain blocked. No
  fabricated listings or production external readiness.

## Chosen preparation topology

A separate, protected BuyBox application/backend operated within the confirmed
Simplee World Render workspace, behind the canonical Tower owner doorway. The
BuyBox backend may need an HTTPS callback/receiver, but that does not authorize a
standalone password login or an unrestricted public browse route. A private
Tower proxy versus a narrowly exposed authenticated receiver remains a
deployment/security review decision; neither is created by this pack.

Private owner beta may use **one** BuyBox instance with transactional SQLite
on a genuinely mounted persistent disk and encrypted originals on the same
approved private volume. The volume, backup mechanism, recovery test, retention
and provider choice are NOT authorized or created here. A future multi-instance
deployment requires an explicitly designed shared transactional data store and
atomic replay ledger; do not put a single-writer SQLite file behind independent
uncoordinated instances. A database/object-storage migration may supersede this
option before approval. No paid resource should be provisioned without the
owner's explicit cost/plan approval.

## New source-only exact protocol

- Schema: tower.buybox.owner.handoff.v1.
- Transport format: tbh1.base64url(canonical JSON).base64url(HMAC-SHA256).
- Signing secret: a dedicated Tower↔BuyBox secret, separate from Flask's
  session secret, Teller's signing secret and BuyBox's Fernet document key.
  Values are issued through secured hosting secret management, never GitHub,
  URLs, logs or chat.
- Claims: schema_version, issuer=tower, audience=buybox-owner,
  purpose=owner_entry, handoff_id, tower_session_ref, actor_ref, entity_ref,
  owner_entitlement_ref, issued_at_epoch, expires_at_epoch, target_path=/,
  return_path=/tower/access-home.
- Strict max lifetime 60 seconds, exact set of fields and types, no public
  redirect destination, canonical Base64url, signature comparison before
  parsing, duplicate JSON key denial, wrong issuer/audience/time denial.
- Receiver produces a VerifiedOwnerHandoff (a verified protocol result, not
  an owner session). Consuming a verified ID uses an atomic unique SHA-256
  constraint in the same durable transactional database. A second consume
  fails even from another connection; no process-local memory-only replay
  authority.
- The current module does not issue a Tower token or expose HTTP routes.
  A future Tower issuer must derive actor/entity/entitlement/session/step-up
  from actual Tower authority; client-provided identity flags cannot mint
  this token. The future receiver must remove the URL fragment before
  requests/rendering and use exact same-origin exchange, HTTPS-only secure
  cookies, bounded session duration, CSRF control, no browser persistent
  storage, and a checked Return to Tower link.

## Private hosted-source inspection

buybox.hosted_readiness.inspect_private_hosted_config checks Tower auth mode,
absence of the legacy local password, separate strong keys, HTTPS exact origins,
secure session cookie, absolute private DB/document paths under a distinct
mounted volume, and disallows symlinked or group/world-readable storage.

Even when these syntactic checks pass, the returned state remains
SOURCE_CONFIGURATION_VALID with provider_storage_proven=False,
backup_restore_proven=False, tower_receiver_active=False and
may_serve_private_records=False. An env flag, a fixture mount predicate, or
source-only test success is **not** actual Render provision/backup/restore
proof. No server startup or product release is added by BBX011–015.

## Required next pack

1. Real Tower issuer on the dedicated Tower branch; match this wire schema,
   60-second lifetime and distinct secret. Verify exact owner session,
   step-up, approved BuyBox entitlement, actual app publication/health and
   receiver Origin before issuance. Keep the app registry locked until
   receiver runtime and protected storage evidence are real.
2. BuyBox protected pre-render receiver in a production auth mode; disable
   local login and all unauthenticated records/downloads. A verified one-use
   token cannot be replayed; secure short-lived cookie and revocation policy
   must be implemented/tested. Full end-to-end owner acceptance still needed.
3. Approve the actual storage/provider plan and price before provisioning.
   Prove durable mount, private backups, document key recovery and restored
   database+original bytes together before real intake.
4. Follow with Tower-scoped action policies and independently verified Teller
   readiness, Tower-mediated Vault proof, Grounds and ATM two-phase handoff.
   No BuyBox↔OB, BuyBox↔Vault direct path or financial execution.
