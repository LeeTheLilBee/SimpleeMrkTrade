# Vault synthetic integration drill evidence and remaining live gates

This branch combines copies of the existing canonical metadata ledger and
AES-GCM envelope with the transaction journal in a **local synthetic harness**.
The test-only object store and SyntheticTrustedVerifier must never be used as
production Tower, scanner or Cloud implementations.

Test scenarios: successful archival and authenticated backup restore; ciphertext
and plaintext SHA-256 comparison; corrupted backup detection; crash immediately
after Cloud-like commit (must remain RECONCILE_REQUIRED); scanner digest mismatch
(no storage write); wrong-entity restore denial; event-chain tampering checks.

The GitHub Actions workflow .github/workflows/vault-integration-drills.yml runs
the selected pytest suite on PR changes or manual dispatch. A committed workflow
is not proof of a passing run: inspect actual CI status/logs before claiming pass.

Remaining live gates: Tower authenticated authorization and revocation, signed
scanner receipt, real Simplee Cloud commit/lookup, durable reconciliation
worker, one canonical ledger migration, protected retrieval, backup isolation
and real restore drill on deployed infrastructure. No production credentials,
external infrastructure, or paid resources configured. In-memory backup
restoration proves algorithmic correctness only, not real-world disaster recovery.
