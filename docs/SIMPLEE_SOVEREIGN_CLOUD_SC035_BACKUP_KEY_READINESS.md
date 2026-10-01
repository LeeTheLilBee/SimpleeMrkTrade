# SIMPLEE SOVEREIGN CLOUD — SC035 REDACTED BACKUP KEY-REFERENCE READINESS

Date: October 1, 2026. Based on merged SC034 `vault-dev` commit `c6386a199729a7770913d97efc42255ebd7e9239`. Source-only; production **NO_GO**.

SC034 introduced historical key resolution by opaque immutable key reference so rotating new backups to v2 does not automatically strand v1 backups. SC035 adds a **redacted preflight** over the verified local backup journal to answer a narrower operational question before an actual restore: “Can the injected key resolver currently return a correctly sized key value for every historical key reference used by acknowledged backup intents?”

The journal first verifies the full append-only intent/event/incident chain. Only backups whose current durable state is `BACKUP_ACKNOWLEDGED` or `BACKUP_RECONCILE_PRESENT` enter the key-dependency inventory. Pending/uncertain backups are reported separately and do not count as recoverable key dependencies; missing/corrupt/replay-integrity-held backups are reported as integrity holds rather than key-ready copies.

The source preflight calls the injected resolver once per distinct historical key reference and emits only aggregate counts:

- acknowledged backups;
- distinct historical key references;
- resolvable and unavailable reference counts;
- acknowledged backups depending on unavailable references;
- pending backup count;
- integrity-hold backup count.

No key reference strings, key bytes, provider refs, entity IDs, object hashes, exception messages or KMS details appear in the result. The check reads **no primary or backup provider bytes**.

A successful resolver call proves only that a 32-byte value was returned for a reference. It does **not** prove that value is the correct historical key for the SCB1 ciphertext. Actual correctness still requires a separately authorized encrypted restore verification and AES-GCM authentication. Accordingly, the report always keeps provider-byte verification, ciphertext authentication, KMS/HSM custody, rotation ceremony, old-key recovery drill and production authorization false.

Synthetic tests cover fixed-key mode, v1→v2 rotation, retired v1 affecting only its dependent acknowledged backup, no provider reads, resolver exception redaction, wrong-but-well-sized key remaining merely “resolvable,” pending ACK-lost backups excluded, integrity-held backups excluded and tampered key-reference journal metadata failing before the resolver.

This is not a KMS/HSM inventory or a real custody check. Production still requires external key custody, least-privilege identities, rotation/revocation policy, backup/escrow, witnessed old-key recovery, independent audit and owner acceptance.
