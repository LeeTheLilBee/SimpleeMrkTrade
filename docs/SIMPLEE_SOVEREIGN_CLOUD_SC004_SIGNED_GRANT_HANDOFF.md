# SIMPLEE SOVEREIGN CLOUD — SC004 SIGNED TOWER GRANT SOURCE CONTRACT

Date: 2026-09-27. Stacked on SC001 development branch (with SC002 and SC003 source code). NO_GO for hosted/production use.

## Correct handoff

BuyBox/Teller -> Tower -> Archive Vault -> Simplee Cloud. Existing executive clouds/ has no document-body access. Tower remains the only issuer of identity, entity, classification, purpose, approval/step-up and revocation decisions. Vault keeps canonical evidence/version/scan/retention/receipt records. Cloud stores encrypted VLT1 objects and independently checks ciphertext hashes; a Cloud storage ACK does not finalize Vault archival.

SC004 proposes a cryptographically verifiable service-to-service capability shape using standard Ed25519 (cryptography package), not a new encryption algorithm. It is a SOURCE-ONLY verifier and fake-key test harness. It does not change Tower, install a network route, create an actual issuer, provide a hosted Vault mTLS client, or turn SC001's test authority into a live verifier.

## Future verified grant

Tower must sign a canonical JSON payload with:
- schema, issuer Tower, audience simplee_sovereign_cloud, exact service archive_vault;
- request ID, Tower decision reference, entity, purpose, operation and classification;
- approval and step-up receipt references;
- opaque object/backup ref and canonical ciphertext SHA-256, bound to trusted Vault state;
- one-time random nonce, issued-at and expiry (maximum 120-second lifetime).

Cloud source verification checks a pinned Tower public key, standard Ed25519 signature, exact canonical fields/no duplicate JSON keys, audience/issuer/caller, bounded expiry, operation-specific object ref, every trusted Vault scope field and signature-protected classification. It then calls independent injected verifiers of the actual authenticated Vault transport peer and current active/revoked Tower decision. Failure or unavailability denies. Only AFTER all these checks does a private SQLite nonce ledger consume the unique nonce atomically and durably.

A signed object alone does not establish physical mTLS peer identity, trusted ownership of the expected Vault record, active approval or reliable revocation; actual issuer and receiver must independently prove those through authenticated runtime integration. Neither client JSON, forged verified_by_tower booleans, fake callbacks nor presence of a signed claim grants a runtime release. The SC004 output is a typed proposed AuthorizedCloudInvocation. It is intentionally NOT wired to the SC002 source storage operations; production connection requires a separately reviewed bridge that binds the exact signed object/digest and current Tower decision on EVERY call, including read/reconciliation/backup.

## Nonce and key caveats

The source nonce ledger writes an opaque hash of signer ID plus nonce in a private SQLite file, with FULL synchronous and unique insertion. Reopening preserves rejection of a used nonce. It is not externally anchored, not a protected long-term anti-replay system and cannot resist a privileged administrator removing/rolling back the database. Production needs independent tamper-resistant replay storage/replication, key lifecycle/rotation/revocation and actual peer attestation.

No Tower private keys, provider credentials, users' document content, actual deployment configuration, personal data or infrastructure provisioning are committed. Tests generate only short-lived synthetic in-memory key pairs.

## Additional security and release gates

- Tower supplies real signed issuer, explicit key IDs, rotation policy, revocation authority and receipt provenance; Cloud pins approved public keys. Tower and Vault owners must agree on canonical claims and deployment-time trust-root distribution.
- Vault supplies an independently authenticated canonical scope, actual Tower-approved scan/original-digest and Vault-generated VLT1; Cloud must compare the invocation digest to the exact bytes before storage/retrieval.
- Private mutually authenticated Vault-to-Cloud transport provides actual peer identity, not an HTTP client-supplied identity string. Direct BuyBox, Teller, executive Clouds or Soulaana access stays denied.
- Replay, expiry, invalid audience/entity/purpose/object/digest, inactive decision, unavailable revocation, wrong peer and test authority are adversarial runtime acceptance gates.
- Revocation and nonce store must be durable, independently protected, auditable, recoverable and subjected to failover/replay drills before a live receiver exists.
- SC002 journal must be reconciled against actual physical storage and Vault canonical receipts; signed grant verification cannot change Vault retention, legal hold or recovery authority.
- Explicit owner sign-off for any infrastructure/operator, hardware ownership/jurisdiction, billing and later protected release. No automatic deployment by a source CI result.
