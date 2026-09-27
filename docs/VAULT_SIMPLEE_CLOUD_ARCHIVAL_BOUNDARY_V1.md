# Vault ↔ Simplee Cloud archival boundary v1 (source-only)

Cloud provides encrypted object storage and recovery; Vault owns evidence identity,
version lineage, classification, retention and receipt presentation; Tower is the
sole authority for identity, permissions, purpose, approvals, step-up and revocation.

## Proposed trusted archival sequence
1. Tower authenticates the service caller and issues a short-lived, audience-bound,
   entity/purpose/action-scoped authorization with unique request ID.
2. Vault validates the authorization with Tower through a trusted service channel;
   reject expired, revoked, reused, wrong-entity or wrong-action grants.
3. Intake quarantines original bytes and verifies a scanner receipt cryptographically
   bound to the exact original SHA-256. No clean scan => no archival.
4. Vault encrypts the original with an approved key and authenticates the entity,
   evidence ID and version ID as associated data.
5. Simplee Cloud accepts ciphertext only, writes create-only and returns a signed
   or authenticated storage commit receipt binding object reference, digest,
   namespace and request ID. An application must never receive raw object location.
6. Vault verifies Cloud receipt through the trusted service channel and commits
   canonical archival metadata with scan and Tower receipt references.
7. A failure between Cloud commit and Vault metadata commit enters reconciliation;
   never show ARCHIVED until both sides verify. Retention and legal holds govern
   disposition of any orphaned encrypted object.
8. Tower-gated read requests resolve Vault's opaque reference, recheck permissions,
   retrieve ciphertext from Cloud and verify digest/authenticated encryption.
   Release only an approved redacted view or controlled download.
9. Corrections append a new version and point to the previous version. Decision
   snapshots preserve exact evidence-version IDs used at decision time.

## Contract fields to settle with the Cloud chat
- Request: request ID, entity namespace, opaque object reference, ciphertext SHA-256,
  ciphertext byte count, encryption envelope version, idempotency token.
- Commit receipt: Cloud operation ID, object reference, entity namespace,
  ciphertext digest and length, committed timestamp, receipt authenticity.
- Recovery: restoration receipt and integrity check, never silently replace an
  existing immutable version.
- No Cloud authorization shortcut, no plaintext upload to Cloud, no app-facing
  object key or presigned URL, no automatic paid deployment.

## Current code limitations
`vault/canonical_evidence_registry.py` is an internal metadata persistence
primitive, NOT an authenticated HTTP endpoint or a complete archival orchestrator.
Its caller-supplied receipt references are not independently verified. Do not
expose its methods directly to BuyBox, Teller or any user-controlled request.
The exact Cloud contract and production authorization mechanism remain pending.
