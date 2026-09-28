# SIMPLEE SOVEREIGN CLOUD — SC009 SOURCE-ONLY PRIMARY-LOSS RESTORE REHEARSAL

Date: September 27, 2026. Based on merged SC008 `vault-dev` commit `789f6223aa1adde2acd0e9ff532eca93b5f65fec`. Production is still **NO_GO**.

## New source acceptance

SC005 verified the isolated SCB1 → VLT1 cryptographic copy, and SC008 verified separation of Cloud ACK versus actual Vault canonical archival receipt. SC009 rehearses the **specific source behavior when primary ciphertext is unavailable**, rather than running only while the primary remains intact.

An isolated synthetic test creates an actual Vault AES-GCM VLT1 envelope and double-encrypted SCB1 backup, then renames the entire primary local storage root to simulate loss. With the primary unavailable, a fresh fake Tower-shaped VERIFY_BACKUP grant and independently injected synthetic canonical backup receipt authorize isolated Cloud backup verification. No primary object is recreated or overwritten. A separate Vault-side test caller authenticates the recovered inner VLT1 using Vault's key/AAD (entity/evidence/version) and original SHA.

The tests also deny a restore without trusted canonical backup receipt, reject wrong-entity references, catch tampered/missing backup and lost backup key with journaled integrity incidents, prove that verification does not repair a deliberately corrupted primary, and propagate backup-provider outage rather than reporting a healthy or missing object.

## Explicit limitations

These are two private directories on the SAME disposable test filesystem. Their isolation cannot establish separate hardware, independently owned physical servers, two data centers, independent backup administration, offsite immutability or recoverability after actual site loss. The cryptographic key is a synthetic in-memory 32-byte value, not real KMS custody. All tested Tower policy/transport and Vault receipt resolvers are fakes; source recovery evidence truthfully keeps `external_failure_domain_verified`, `vault_original_authenticated` (from Cloud's perspective), `RPO/RTO certified` and `production_recovery_authorized` false.

No actual Vault recovery commit, object rewrite, provider enrollment, paid resource, real data, real clock-based RPO/RTO SLA, external signed audit anchor or production route occurs. Those require separate Tower/Vault owner-workstream and owner approvals per issue #99 and master issue #66.

This pack adds ONLY source tests, this handoff and scoped GitHub CI; no live code path changes.
