# SIMPLEE SOVEREIGN CLOUD — SC006B CONCURRENT REQUEST HARDENING

Date: 2026-09-27. Based on merged `vault-dev` SC006. Source-only tests, **production NO_GO**.

These adversarial synthetic tests run overlapping requests against actual SC002/SC004/SC005B Cloud source components. The one-use Tower-shaped grants and local encrypted object backends are fake; no external Tower, provider or Vault canonical service is contacted.

- Reuse of the **same signed nonce** across concurrent requests must result in exactly one accepted invocation. A consumed nonce cannot become valid merely through a race.
- Multiple individually fresh signed grants for the **same original logical write** can return the same idempotent internal storage receipt or a fail-closed hold, but must never create more than one physical object.
- Competing fresh BACKUP_CIPHERTEXT grants for the same source/backup request must likewise reserve one opaque backup reference and execute at most one create-only PUT, not generate duplicate backup objects.
- When the provider accepts a backup but loses the ACK, competing calls never retry it automatically. Its canonical SC005B reservation remains pending and must be reconciled with a fresh independently authorized grant.
- Competing reconciliations of that same backup intent must yield one durable PRESENT transition at most, while every other concurrent attempt denies/holds. No operation writes a duplicate physical backup or declares a Vault backup/archival commit.
- All tests check hash-chain and metric invariants after races; source runtime remains disabled.

Operational dependencies remain independent: Tower needs real signing/peer/current-policy authority and tamper-resistant replay storage; Vault needs actual authenticated canonical scope and final registry/receipts; Cloud needs an owner-approved locked provider, independent backup and key domain, externally anchored audit ledger, real restore/incident delivery and separately approved release. Passing tests cannot prove multi-host/process/database failover, remote object-lock semantics or real hardware isolation.

No paid infrastructure, credentials, live route or real document is created.
