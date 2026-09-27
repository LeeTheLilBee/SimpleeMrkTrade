# VRO003 — Vault Real Operations source-only regression gate

Parent: draft Vault Real Operations PR #38 at
\`4dd2cdca37326abeaf09a01cbfc6deadd0200a74\`.
This is an independent GitHub CI check, not a merge of the draft into
\`vault-dev\`, not provider approval, and not a real archival deployment.

The workflow installs Python test-only dependencies, compiles the two scoped
modules and their tests, and runs the exact synthetic test suite:
\`vault/test_real_operations_encrypted_storage.py\` and
\`vault/test_real_operations_managed_object_store.py\`. Tests use local
fake/in-memory clients, fabricated authorization decisions and synthetic bytes.

The code checks AES-256-GCM envelope corruption/scope failures, local
create-only encrypted backup, S3-compatible conditional create-only ciphertext
PUT/GET shape and content hash mismatch. Passing tests demonstrate **source
behavior only**, not provider support, private bucket policy, KMS, malware
scanner, receipt provenance, Tower authentication, immutable canonical Vault
transaction, retention/legal hold, restore drill or protected download.

No AWS/Render credentials, cloud keys, provider selection, paid provisioning,
real documents or network-storage tests are included. Real Tower middleware
must create \`TowerStorageDecision\` from authenticated server authority; its
\`verified_by_tower=True\` dataclass field is not cryptographic proof and
must NEVER be exposed as a client-controlled JSON property.

The parent PR #38 remains DRAFT/NO_GO pending provider/security/owner
decisions and actual end-to-end tests in its handoff document. BuyBox↔Vault
metadata contract PR #35 is a separate, still-unactivated corridor.
See cross-system worklist #54 and BuyBox hosting hold #42.
