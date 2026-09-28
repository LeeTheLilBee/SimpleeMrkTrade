# SIMPLEE SOVEREIGN CLOUD — SC016 VAULT CANONICAL READ-SCOPE CONTRACT

Date: September 28, 2026. Source baseline `vault-dev` `05d01551018888abc57b91b438e66a630d33cd26` after CI consolidation. **NO live service or production authorization.**

## The next actual source-integration edge

SC008 verified that the real merged Vault `ArchivalJournal` and `CanonicalEvidenceRegistry` only reach the final ARCHIVED state after separately checked internal Cloud and canonical registry receipts. SC016 checks the next consequence: an encrypted Cloud READ must resolve scope **from independently owned, actual canonical Vault metadata**, and an internally acknowledged Cloud PUT cannot by itself authorize a read.

The read-only test adapter exists ONLY inside `simplee_cloud/tests/test_sc016_vault_canonical_read_scope.py`; it is not a runtime implementation or route. Given an internally assigned synthetic Vault read request, it verifies the actual original Vault workflow hash chain and ARCHIVED state, then reads the actual merged append-only canonical registry row matching the exact receipt ID, original request ID and entity. Only then does it construct the expected `TrustedVaultScope` for Cloud's existing source-only one-time signed-grant verifier. The test reads the exact original Vault VLT1 bytes, not a hardcoded pretend hash.

It denies the following before a Cloud physical GET: stored-but-not-archived Cloud ACK, canonical row inserted before Vault workflow reaches ARCHIVED, absent/wrong entity/receipt/original request, signed wrong object/digest, current Tower policy revoked, consumed nonce and corrupted Vault journal history. No raw backend body or physical object reference is returned to an application or owner-facing output.

## Explicitly not a live registry resolver

The adapter's request assignment is a trusted **synthetic test fixture**. In production, Vault's owning service must independently authenticate the private Tower/Cloud transport, current user/entity policy, canonical original evidence/version/retention/scan, approval and step-up BEFORE producing an authoritative scope. A browser flag or request-supplied receipt ID cannot replace that authority. The currently merged `CanonicalEvidenceRegistry` is a metadata ledger, not an authorization service; its internal SQLite access must never become a public API or direct Cloud-to-database connection.

Tower remains the real grant signer/key custodian/peer and current policy authority. Cloud only consumes exact signed, trusted, scoped requests and returns internal encrypted storage, not original documents or Vault canonical finality. This source-only test adds no new production method or cross-service credential.

## Acceptance and next owners

Only a test and this handoff were added; SC015's consolidated full Vault/Cloud source workflow automatically covers it without spawning the eighteen historical duplicate jobs. [Tower/Vault handoff #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99) remains open for real service implementation. No provider, paid resource, live data, credential, mTLS deployment, signed real grant or production route is created.
