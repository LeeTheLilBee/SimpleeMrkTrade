# SIMPLEE SOVEREIGN CLOUD — SC037 STABLE OPAQUE NAMESPACE RESOLVER

Date: October 1, 2026. Based on merged SC036 `vault-dev` commit `8b52ee053a3cb068e517889ab27a3b06e0e98e0c`. Source-only; production **NO_GO**.

## Gap

Cloud physically isolates each entity under a 64-hex HMAC namespace instead of exposing raw entity IDs in storage paths. The original service derives that namespace from one 32-byte namespace secret. This is private and deterministic, but a naïve future rotation to a different HMAC secret would derive a different namespace for the same entity and make already-written ciphertext appear absent.

SC037 preserves the existing fixed-secret mode for all current source fixtures and adds an **optional externally injected stable namespace resolver**. Resolver mode passes no namespace HMAC secret into Cloud. The trusted external seam returns the already-established opaque 64-hex namespace for the entity, allowing a reconstructed Cloud service to continue addressing existing journal and provider objects after secret-management policy changes.

The resolver is still source-only and does not become authority: Tower/Vault authorization happens first. Resolver outage, malformed namespace, same-process entity mapping drift or two different entities colliding into the same namespace all deny before provider access. The in-process drift/collision cache stores only per-process HMAC tags made with a random ephemeral cache key, not raw entity IDs. It is not persistent identity state.

The journal remains the deeper historical provenance check. If a newly reconstructed process is given the wrong stable namespace mapping, exact acknowledged-primary lookup fails before provider GET rather than silently claiming another location.

## Source acceptance

Synthetic tests prove:

- a stable resolver allows a second reconstructed service to read an existing object without receiving the original namespace HMAC secret;
- changing a fixed HMAC secret directly produces a different namespace and fails acknowledged-primary provenance before provider read;
- same-process resolver drift denies;
- cross-entity namespace collision denies;
- resolver outage and malformed output deny before provider read;
- fixed-secret and resolver modes are mutually exclusive;
- the resolver cache and journal do not persist the raw test entity name;
- a wrong stable mapping after process restart fails journal provenance before provider GET;
- source health can state that a resolver was injected while still keeping namespace-rotation custody certification and production authorization false.

## External requirements

This does **not** provide a real stable namespace registry, HSM/KMS secret rotation, durable mapping database, external uniqueness proof, multi-process consistency or disaster recovery for namespace mapping. A real resolver must be independently authenticated, backed up, replicated, auditable and fail closed; it must preserve one stable namespace per canonical entity across service restarts and secret rotations.

The owner/Tower/Vault/provider release path still requires actual namespace mapping custody, migration/rollback proof, authorization, external provider security and independent recovery testing. No paid resource, production secret, hosted route or real user data is introduced.
