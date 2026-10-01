# SIMPLEE SOVEREIGN CLOUD — SC038 DURABLE REDACTED NAMESPACE BINDING

Date: October 1, 2026. Stacked from the corrected SC037 source head and intended for current `vault-dev` after SC037 merge `fe0c4a523b622d230e9e4d124b81b1111a4052ec`. Source-only; production **NO_GO**.

## Gap closed

SC037 introduced an externally injected stable namespace resolver so a reconstructed Cloud process can keep addressing the same opaque 64-hex entity namespace after future namespace-secret policy changes. It already denied resolver drift/collision in one process, and an incorrect mapping for an **existing read** eventually failed exact primary-journal provenance.

There was still a different restart risk: after process reconstruction, a wrong resolver mapping could be used for a **brand-new object reference**. Because no previous object existed at that new ref, ordinary primary provenance could not tell that the entity had historically lived under another namespace. That could split one canonical entity across two physical namespaces.

SC038 adds `SQLiteNamespaceBindingLedger`, a private append-only source ledger containing only:
- HMAC-tagged canonical entity identity using a distinct 32-byte binding secret;
- the pre-approved opaque 64-hex stable namespace;
- timestamp and hash-bound append-only event lineage.

Raw entity IDs are never stored. One entity tag can bind one namespace, and one namespace can bind one entity tag. Trigger-bypassed row/event mutation, missing audit event, drift and collision fail closed.

## Crucial authority separation

Cloud I/O **cannot enroll mappings as a side effect**. Resolver mode now requires a separately pre-enrolled `SQLiteNamespaceBindingLedger`. Every write/read operation first asks the external resolver for the opaque namespace and then requires that exact entity→namespace pair already exist in the durable binding ledger. Enrollment is an explicit `enroll_source_binding()` source-test preparation action representing future independently authenticated Tower/Vault namespace-registry work.

This matters for migrations: old SC037-only temporary source fixtures do not receive automatic trusted enrollment. A future real migration must establish and independently verify the existing canonical mapping before enabling a resolver-backed service. There is no live persisted Cloud namespace registry today.

## Acceptance

Synthetic tests cover:
- mapping survival across process and ledger reopen;
- idempotent enrollment plus entity drift and cross-entity collision denial;
- wrong binding secret after restart;
- row/event tampering and missing event;
- concurrent conflicting enrollment;
- resolver restart returning the wrong namespace for a **new write**, denied before provider PUT or journal reservation;
- unenrolled mappings denied before provider access;
- no raw entity name in the resolver cache, operational journal, binding rows or binding events;
- fixed-secret mode remains separate;
- no live binding-registry mode or false external/KMS certification.

The binding secret is itself not production KMS/HSM custody. This local ledger is not a multi-host authoritative mapping service, external immutable registry, independently replicated namespace catalog or disaster-recovery proof. Real deployment still requires authenticated Tower/Vault mapping authority, durable replicated registry, binding-key rotation/custody, backup/restore and owner release.

No paid infrastructure, provider signup, production credential, hosted route or real user document is introduced.
