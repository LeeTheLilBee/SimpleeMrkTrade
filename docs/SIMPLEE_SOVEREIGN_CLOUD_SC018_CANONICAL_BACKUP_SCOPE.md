# SIMPLEE SOVEREIGN CLOUD — SC018 CANONICAL BACKUP VERIFY SCOPE

Date: September 28, 2026. Source baseline: merged `vault-dev` commit `c55c25caca151bdb72a28a197e49f546fc040901` after SC016. **Source-only / production NO_GO.**

## Boundary closed

SC016 proved that an encrypted primary read must resolve from the actual merged Vault ARCHIVED workflow plus canonical archival registry row. Backup verification has an additional requirement: the primary archival receipt alone is **not** enough to authorize access to a separately encrypted backup object.

SC018 therefore exercises a test-only authoritative join between:

1. the actual merged Vault `ArchivalJournal` verified ARCHIVED state,
2. the actual merged append-only `CanonicalEvidenceRegistry` primary object reference and ciphertext digest, and
3. a **separate Cloud BackupReceipt** whose source object reference and source ciphertext SHA must match that canonical primary archive.

Only after all three match does the test adapter build the expected `TrustedVaultScope` for `VERIFY_BACKUP`. Cloud's existing signed one-use source verifier must then sign the actual `backups/<opaque>` reference and backup ciphertext SHA. The existing independent canonical backup receipt resolver must return the same backup receipt before physical backup GET.

## Negative cases

The source test denies before backup bytes are read when:

- the primary Vault record is ARCHIVED but no separate canonical backup receipt exists,
- physical backup bytes exist but no trusted backup assignment exists,
- the backup receipt points at a different primary object or source ciphertext SHA,
- the Vault workflow has not reached ARCHIVED,
- entity, archival request or canonical receipt identity is wrong,
- a primary `objects/...` reference is incorrectly reused for `VERIFY_BACKUP`,
- signed backup ref or backup SHA differs from the trusted backup receipt, or
- the actual Vault workflow journal is tampered.

This makes the finality model explicit: **Vault primary archival finality and backup custody/recovery authority are separate facts.**

## What is still missing

The joined resolver exists only inside the SC018 test. The merged Vault canonical registry currently records primary archival metadata; it is not a live backup-receipt authorization service. A real Vault-owned protected backup receipt/retention/custody record must eventually be implemented behind actual authenticated Tower/Vault service transport. Cloud must never query Vault SQLite directly in production.

The real implementation still needs Tower's signed issuer/current-policy/private peer, Vault's authenticated backup receipt and retention/legal-hold truth, independently operated backup failure domain/key custody, provider immutability evidence, external audit custody, restore drill and owner-approved release. No provider, paid resource, key, live route or production data is added here.
