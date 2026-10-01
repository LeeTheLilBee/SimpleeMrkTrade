# SIMPLEE SOVEREIGN CLOUD — SC041 NAMESPACE REGISTRY COVERAGE RECONCILIATION

Date: October 1, 2026. Based on merged SC040 `vault-dev` commit `b5d51b780ad5e01cc6c3a2cf16fa6207d3eb1601`. Source-only; production **NO_GO**.

## Gap closed

SC038 made resolver-backed operations require a durable pre-enrolled entity→opaque namespace binding. That prevents mapping drift when the correct binding database is present.

A different failure remained: the binding database itself could be lost and replaced by a brand-new empty database. An empty append-only database is internally valid, so an owner-local check that looked only at its own integrity could appear healthy even though it no longer covered namespaces already used by resolver-backed Cloud operations.

SC041 makes resolver-backed namespace use independently visible in the verified Cloud operational journal. After Tower/Vault authority and exact durable binding succeed, but **before provider access**, the service records a redacted `namespace_binding_verified` event containing only the existing opaque namespace and request tag. Failed/unenrolled bindings never emit the success marker.

The operational journal can now return an internal, fully verified set of distinct namespaces that actually passed this resolver-backed gate. The namespace-binding ledger can return its own verified enrolled opaque namespace set. `source_namespace_binding_coverage()` compares those sets and returns **counts only**:

- resolver-backed namespace count;
- enrolled namespace count;
- matched count;
- missing resolver namespace count;
- enrolled-but-not-yet-used count.

No entity ID, namespace value, request ID, object ref, digest or key is returned.

If any resolver-used namespace is absent from the supplied durable binding ledger, status becomes `SOURCE_ONLY_NAMESPACE_BINDING_HOLD`. A recreated empty or partial ledger therefore cannot look like complete namespace continuity. Extra pre-enrolled namespaces are allowed and reported separately because a canonical entity may be enrolled before its first Cloud object.

## Fixed-secret separation and migration

Original fixed 32-byte namespace-secret mode does **not** emit `namespace_binding_verified`, so fixed-key operations do not falsely create a requirement for the resolver binding registry.

Likewise, operations from source revisions before SC041 have no resolver-success marker and are not silently reclassified. A future real migration must establish authoritative historical namespace coverage from Tower/Vault registry evidence; this source feature does not invent it retroactively.

## Owner desk

When a namespace-binding ledger is supplied, the owner evidence desk now uses coverage status instead of merely saying the local binding DB is internally valid. A missing/partial registry becomes an explicit local HOLD. Counts remain redacted and external registry/KMS custody, cross-ledger external certification and production authorization remain false.

## Acceptance

Synthetic tests cover:
- fixed-secret operations creating no false resolver requirement;
- resolver-backed write emitting the marker only after binding acceptance;
- exact complete coverage;
- lost/recreated empty binding DB;
- partial registry with one of two historical namespaces missing;
- extra unused enrollment;
- denied unenrolled mapping producing neither provider PUT nor success marker;
- operational-journal and binding-ledger tamper;
- owner output containing only counts, never raw entity/request/namespace values.

No external registry, KMS/HSM, provider, paid infrastructure, hosted route, real user data or production release is created.
