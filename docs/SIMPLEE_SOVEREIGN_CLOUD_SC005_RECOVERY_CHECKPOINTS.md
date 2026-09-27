# SIMPLEE SOVEREIGN CLOUD — SC005 RECOVERY DRILL AND EXTERNAL CHECKPOINT CONTRACT

Date: 2026-09-27. Source-only, stacked on SC001 development branch. Production NO_GO.

## Purpose

SC001 built bounded VLT1 ciphertext handling and separately keyed SCB1 backup envelopes. SC002 added the local hash-chained intent, operations and incident SQLite journal. SC003 provides source-only provider compatibility. SC004 proposes signed Tower service access without a live issuer/receiver.

SC005 adds two independently scoped *source-test-only* contracts: a journal prefix hash signed by an injected **external** Ed25519 signer and a drill that verifies recovery of the inner encrypted VLT1 bytes from the SCB1 backup without ever writing primary storage or decrypting a Vault document.

## Journal anchor

- The journal verifies its entire local event hash chain before returning a historical prefix hash through checkpoint_head(sequence).
- checkpoints.py builds a canonical JSON snapshot with unique opaque checkpoint ref, exact event count/head hash, previous signed-checkpoint digest, key ID and timestamp.
- An independently injected signer callback signs these exact bytes with audited Ed25519, then the verifier checks the pinned public key and (if supplied) the full current journal and historical prefix.
- An independently injected CheckpointSink must accept create-only delivery. This PR implements **no external signer, no commercial/offsite sink, no KMS, no network route, no durable cross-domain replication, no key in the repo**.
- A hash-chained SQLite database on the same host can be wholly replaced by an attacker with privileged storage access. Only a previously delivered and independently retained signed anchor enables rollback detection against that trust root; a forged/replaced signer or independently replaced anchor defeats the assumption.
- A source test fake anchor and in-memory test private key are NOT actual hardware/organizational independence. Signed checkpoints are not Vault canonical receipts, provider lock evidence or proof of document recovery.
- The next real deployment must prove anchor write-once retention, independent custody, key rotation and loss recovery, immutable offsite retention, monotonic sequence checks, scheduled checkpoint/verification, administrative tamper drills and owner alert delivery.

## Recovery drill

- recovery_drill.py verifies synthetic recovery from independent injected backend and SCB1 AES-256-GCM backup key using the existing IndependentBackupService.
- Checks Tower/Vault gate through source_test, trusted expected inner SHA and stored backup scope/digest. After verifying, returns a safe synthetic report with elapsed measurement and non-certification flags.
- The drill does NOT overwrite a primary object or expose/decrypt an original document. Any integrity failure or missing backup causes an append-only BACKUP_INTEGRITY_FAILURE journal incident before the error is surfaced.
- An intentionally deleted primary synthetic local object can remain absent while the separate encrypted backup still verifies. That is NOT evidence that two folders are on independent machines/data centers or that Vault can complete its real recovery commit.
- Actual RPO/RTO targets, fault injection across provider/site loss, separate credentials and key custody, restore from independent media, Vault original AES-GCM/authenticated SHA check, canonical metadata/receipts, legal hold, owner decision and real alerting remain unimplemented/unverified.

## Operational promotion gates

1. Owner approves actual provider/hardware and independent failure-domain location, cost and vendor/subprocessor jurisdiction disclosure.
2. Independent signer and append-only/offsite checkpoint sink under separate credentials and rotation/recovery policies; real immutable retention of anchors and audit logs.
3. Tower/Vault/Cloud real authenticated issuer/receiver + callback checks in issue #99, current permissions/revocation and nonce durability; never connect source test fakes to real storage.
4. Restore test under actual primary outage with independently retrieved keys/metadata/backup, verified encrypted bytes and Vault original authentication and canonical recovery receipt.
5. Measure and owner-approve service-specific RPO/RTO and run repeated recovery drills with documented owner notification and incident handling.
6. No production authorization by source-only success; SC001 parent PR stays DRAFT/NO_GO until distinct security/operational release approval.

This package creates no paid storage, external accounts, provider selection or production data.
