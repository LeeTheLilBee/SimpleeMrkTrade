# SIMPLEE SOVEREIGN CLOUD — SC023 PHYSICAL REFERENCE ANTI-ALIAS

Date: September 28, 2026. Based on merged SC022 `vault-dev` commit `4b818b680e26673864035e588ad2efb52aaf48c1`. Source-only, no hosted receiver and production **NO_GO**.

## Gap closed

The existing durable journal idempotency policy reserved the logical pair `(namespace, request_id)`. It did not prevent a different logical request ID in the **same entity namespace** from reserving the same opaque physical object ref. An immutable backend rejects a second physical PUT, but the new request could then enter uncertain state and incorrectly use its own reconciliation to claim bytes produced by the FIRST request. Vault's canonical registry also has independent object-ref uniqueness, but Cloud should deny that alias before reaching provider storage.

SC023 enforces one physical primary ref per logical write request and one physical backup ref per logical backup request **within a namespace**. It keeps the original request's idempotent replay, and permits coincidentally identical random object refs under two completely separate HMAC entity namespaces. Both source SQLite unique indexes and explicit checks inside the same BEGIN IMMEDIATE reservation transaction prevent concurrency races. Verified journal reads also reject physical ref aliasing if a privileged local tester drops an index before altering state. An existing temporary source-test database with aliased physical refs fails at construction rather than silently migrating or claiming success.

Separate backups of one source object with independently generated NEW backup refs remain permissible; this policy protects physical destination ref identity, not a global prohibition on backup versions or key rotation.

## Acceptance and limitations

Adversarial synthetic tests cover different logical signed requests reusing the same primary ref, exact-request replay, cross-entity same-ref isolation, distinct refs in one entity, duplicate backup destination refs, cross-entity backup destinations, six concurrent request races and privileged dropped-index insertion. Source journal event and owner coverage checks remain consistent.

This is still a source-only local SQLite and fake Tower/Vault authority test. It does not establish real service identity, external producer origin, remotely enforced provider conditional PUT, Vault canonical receipt, independent backup failure domain, live monitoring, offsite audit custody or production release. No paid infrastructure, credentials, real user documents or network route are introduced.
