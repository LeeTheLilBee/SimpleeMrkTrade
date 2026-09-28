# SIMPLEE SOVEREIGN CLOUD — SC007 AUDIT RESERVATION BINDING

Date: September 27, 2026. Source-only hardening on verified merged `vault-dev` head `aea5e2f5a8ade0e4210ad3b2b31a9cc053bfffb5`.

## Gap and fix

The existing SC002/SC005B operational journal chained event fields and ensured a matching write/backup reservation existed, but the event only included the opaque request tag/namespace, **not the complete immutable reservation payload**. If a privileged local tester bypassed the table's update trigger and changed the reserved object reference, ciphertext SHA, size, key reference or timestamp, the event chain could still report valid.

SC007 commits a SHA-256 fingerprint of the entire canonical reservation row to its `WRITE_RESERVED` or `BACKUP_RESERVED` event (marked `reservation:v2:<sha256>`). The event's own hash then binds that fingerprint into every later event and the SC005 prefix checkpoint. At verification, both table-to-event and event-to-table cardinality must match, there must be exactly one correctly scoped reservation event per row, and the full row fingerprint must agree. An altered, deleted or inserted reservation now fails closed on `verify_chain()`, read intents, checkpoint heads, health checks and subsequent transactions.

No content, raw entity name, Vault original, signing secret or bearer token is added to the journal. The Cloud backup and write operation interfaces remain unchanged.

## Compatibility and limits

This is an **intentional source-test journal schema-version boundary**. Existing SC002/SC005B temporary `source_test` journal databases with unbound reservation events fail closed and are not silently migrated or accepted. There is no production Cloud DB or real document data authorized here. Before any future persisted runtime release, an independently reviewed migration/backup procedure must preserve verified history and external signed checkpoints.

A malicious administrator who can rewrite the entire SQLite event chain plus payloads and all external evidence is not stopped by a local hash chain. The SC005 independent signer, immutable offsite sink, key custody and rollback verification remain mandatory release gates. Similarly, this work does not certify S3 Object Lock, real Tower issuer/mTLS, Vault's canonical archival receipt, site-loss recovery or owner-approved infrastructure.

## Acceptance

Synthetic adversarial tests change each primary/backup reservation field by bypassing local triggers, delete intents without deleting events, inject forged rows, reopen the journal and simulate legacy unbound event entries. The complete Cloud regression suite and existing combined Vault/Cloud source checks must remain green. Only this Cloud-owned journal and its new test/doc/workflow are changed.

No provider, payment, production route or private credential is created.
