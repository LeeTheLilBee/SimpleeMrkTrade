# SIMPLEE SOVEREIGN CLOUD — SC008 ACTUAL MERGED VAULT FINALIZATION ACCEPTANCE

Date: September 27, 2026. Stacked on merged `vault-dev` SC007B commit `a21bacdd42c9d02e019c5c2cec14aaf0167058d3`. **Source-only. No production authority.**

## What is proved with the actual repository modules

SC006 established that genuine Vault-created AES-GCM VLT1 envelopes are byte-compatible with Cloud's encrypted write/read/backup source paths. SC008 adds the **actual merged Vault archival transaction journal and canonical evidence registry**, rather than pretending that a Cloud write ACK is a Vault archive.

The isolated synthetic test coordinator uses `vault.archival_transaction_journal.ArchivalJournal`, `vault.canonical_evidence_registry.CanonicalEvidenceRegistry`, `vault.real_operations_encrypted_storage.encrypt_original/decrypt_original` and Cloud's already merged `SourceOnlyBoundCloudPort`. It checks this explicit handoff:

1. Vault source workflow is `RECEIVED → QUARANTINED → VERIFIED → ENCRYPTED`; scanner/Tower checks are *synthetic test stubs only*. A real original's SHA and ciphertext envelope SHA are separately computed.
2. The source Tower-shaped grant, trusted Vault test scope and journaled Cloud PUT bind exact entity, original request ID, opaque ref and encrypted SHA. A successful internal Cloud storage receipt does **not** set Vault `ARCHIVED` and does not automatically create a canonical registry row.
3. The test performs a separate fake-authorized encrypted read and uses Vault's own decryptor to verify its AAD (entity/evidence/version) and original SHA. The trusted real orchestration layer must replace this fake source receipt verification with genuine Tower and Vault evidence.
4. Vault source moves to `CLOUD_COMMITTED` only after its own verified Cloud receipt and then independently inserts a canonical registry row. The test only moves to `ARCHIVED` after a distinct registry receipt digest; it checks that the real journal chain and registry tuple agree on entity/evidence/version/original hash/Cloud ref/ciphertext SHA.
5. An accepted-but-ACK-lost physical write leaves Cloud `WRITE_UNCERTAIN` and Vault `RECONCILE_REQUIRED`. A fresh source Tower grant on the ORIGINAL request reconciles the physical ciphertext without duplicate PUT; even `PRESENT_INTERNAL_STORAGE_ONLY` cannot commit Vault by itself. Absent/corrupted ciphertext remains HOLD, without canonical registry row or an `ARCHIVED` transition.
6. Invalid signed bytes cannot create Cloud write intent; conflicting canonical object ref replay is refused by Vault registry.

## What it deliberately does not claim

The source-only Vault `CanonicalEvidenceRegistry.record_archival` trusts its caller's previously authenticated original/scan/Cloud evidence. It does **not** authenticate a bearer, Tower private issuer, Cloud provider or scanner by itself. Likewise `ArchivalJournal.advance` validates state sequencing and caller-supplied receipt hashes; it is not a verifier of real external signatures. The synthetic acceptance code exists only in test files, not a service implementation, HTTP route, live Vault canonical resolver or reusable `verified_by_tower` boolean.

**Tower and Vault owning workstreams** must independently provide live issuer, actual private transport, current policy and approval/step-up, real scan provenance, protected Vault record lookup, proof of a separate canonical registry transaction, legal retention and final receipt. Cloud cannot choose or declare these. The source Cloud ACK is not a Vault archival receipt.

This test does not certify offsite WORM, provider Object Lock/versioning, real independent backup failure domain, KMS, actual site loss/recovery, owner alarm delivery, RPO/RTO or an approved paid pilot. No real documents, live service traffic, credentials or paid resources are created.
