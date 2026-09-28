# SIMPLEE SOVEREIGN CLOUD — SC022 PER-OBJECT BACKUP COVERAGE (SOURCE JOURNAL ONLY)

Date: September 28, 2026. Based on verified `vault-dev` source `667e400c17ddc6f8ad9257175b5b31b00d72b676` following SC021. **Production NO_GO**.

## Problem and correction

The existing owner source snapshot independently counted primary writes and backup reservations. Totals could look equal even when two separate primary objects existed and a backup covered only one of them. Worse, an unresolved, missing, corrupt, cross-entity or mismatched backup could be mistaken for complete protection.

SC022 adds `SQLiteOperationalJournal.source_backup_coverage()`. It first verifies the complete append-only storage/backup/incident event and payload commitments, then compares distinct acknowledged primary objects with acknowledged backup intents using the exact triple **opaque entity namespace digest + source object reference + source ciphertext SHA-256**. Only `WRITE_ACKNOWLEDGED/RECONCILE_PRESENT` primaries and `BACKUP_ACKNOWLEDGED/BACKUP_RECONCILE_PRESENT` backups count as journal-ACK matches. Unresolved backups remain uncovered, reported separately as a pending subset; missing, corrupt or replay-integrity-failed backup states cannot claim coverage. Failed primary integrity states are excluded from acknowledged-primary count and remain separately reported as a primary hold.

The owner-local source snapshot and SC021 evidence desk expose only aggregate counts and a safe coverage action card. No raw request ID, entity name, ref, physical path, ciphertext digest, document content or credential is returned.

**Crucial limit:** A durable local ACK is not proof that physical backup bytes still exist, decrypt successfully, are independent of primary hardware or have an authoritative Vault canonical backup receipt. All respective output flags remain false. Physical verification requires an actual independently authorized restore drill, Vault original authentication and external failure-domain evidence; the source count never says 'fully protected'.

## Source acceptance

Regression tests cover empty local source, one unbacked write, two primary objects with only one backup, ACK-lost pending backup moving to matched journal status only after original-ID reconciliation without another PUT, same object ref/digest across different entity namespaces, nonmatching ref, backup replay corruption removing coverage, damaged primary remaining a separate integrity hold, tampered committed backup intent denying all owner reports, and absence of sensitive identifiers in source JSON/Markdown.

No new CI workflow is added: the existing consolidated Vault/Cloud source gate executes the full tests, preserving SC015's one-full-suite gate topology. No provider, paid resource, public route, production key, authentic Tower/Vault sender, external backup hardware or user documents are introduced.

See [source master #66](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/66) and [Tower/Vault owning handoff #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99).
