# SIMPLEE SOVEREIGN CLOUD — SC044 SIGNED-PREFIX NAMESPACE COVERAGE

Date: October 1, 2026. Based on merged SC043 `vault-dev` commit `e88c786eff781e860adcf15d37bcbb8ab51137bb`. Source-only; production **NO_GO**.

## Problem

SC041 compares all resolver-used namespaces in the current Cloud journal with all currently enrolled durable namespace bindings. SC043 signs storage/replay/namespace ledger prefixes plus the namespace binding-key commitment. Those were still separate facts: a registry entry added AFTER a signed checkpoint could make today's coverage clean without proving it existed at that older signed vector.

## SC044

The operational journal and namespace binding ledger can now produce fully verified **historical prefix inventories**:
- resolver-backed namespaces observed at or before an exact storage event count;
- enrolled namespaces present at or before an exact namespace-binding event count.

Both methods verify the FULL current append-only ledger first and reject unavailable/out-of-range prefixes. They do not trust a detached truncated database.

`source_control_checkpoint_namespace_coverage()` first verifies the signed control checkpoint against:
- the Cloud storage journal prefix;
- the consumed Tower-shaped replay prefix;
- the namespace-binding event prefix;
- and, for SC043/v2, the exact namespace binding-key commitment.

It then compares resolver use and enrollment at the exact storage/namespace counts contained in that signed checkpoint. It returns only redacted counts.

This means a later repair cannot rewrite an old checkpoint. If a signed vector recorded resolver-backed namespace use while that vector's namespace registry lacked the enrollment, that checkpoint remains `SOURCE_ONLY_NAMESPACE_BINDING_HOLD` even if the current registry is later fixed. Conversely, namespace enrollments and resolver use that occur after a checkpoint do not expand its historical counts.

The owner evidence desk now shows BOTH:
1. current namespace-binding readiness; and
2. `checkpoint_namespace_coverage` for the exact supplied signed control vector.

That makes “fixed now” visibly different from “was correct at checkpoint time.”

## Important non-claim

A signed vector is still not a single atomic transaction across three separate SQLite ledgers. SC044 therefore keeps `cross_ledger_point_in_time_certified=False`. It proves consistency of the exact signed prefix vector, not simultaneous database commit time, real offsite latest-tip custody or production infrastructure.

Legacy v1 control checkpoints can still anchor historical event-prefix coverage but cannot claim the namespace binding-key commitment was signed. V2/SC043 checkpoints explicitly report that stronger fact.

No real provider, Tower/Vault live authority, external registry replication, KMS/HSM, paid infrastructure, real documents or production release is created.
