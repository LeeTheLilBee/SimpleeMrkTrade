# SIMPLEE SOVEREIGN CLOUD — SC036 OWNER EVIDENCE DESK + BACKUP KEY READINESS

Date: October 1, 2026. Based on merged SC035 `vault-dev` commit `25a79ae88e503e24ce0a191ad59474e6fc5252ad`. Source-only; production **NO_GO**.

SC035 can verify the local acknowledged-backup journal and ask an injected key resolver whether every historical key reference is currently resolvable, while reading no provider bytes and exposing no key references. SC036 makes that result optionally visible in the existing SC021 owner-local evidence desk.

The desk now accepts an optional `JournaledBackupOperations` object. It must point at the **same verified operational journal** already used by the owner desk; a different journal or arbitrary object is rejected. When supplied, the desk adds a bounded `backup_key_readiness` section containing only aggregate counts and source status. When omitted, the section explicitly says `NOT_EVALUATED` rather than silently assuming keys are available.

A matched backup ACK and key resolvability are intentionally separate facts. The owner view can therefore show that a primary has an acknowledged backup while also showing that its historical key reference is unavailable. That state becomes a source HOLD, not a recovery success.

The desk never emits the actual key reference, backup ref, source object ref, digest, namespace, key bytes or resolver exception text. Provider bytes are not read. KMS/HSM custody, correct key material for the ciphertext, old-key recovery drill, physical failure-domain recovery and production authorization remain false.

Existing source/replay tamper gates remain first-class: a corrupted storage journal or consumed-grant replay ledger blocks the desk even when backup key readiness is supplied.

No hosted dashboard, production KMS, provider credentials, paid resource, real user data or GO is introduced.
