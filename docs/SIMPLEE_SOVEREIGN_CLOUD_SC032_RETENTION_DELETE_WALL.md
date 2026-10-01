# SIMPLEE SOVEREIGN CLOUD — SC032 RETENTION / DELETION AUTHORITY WALL

Date: October 1, 2026. Based on verified `vault-dev` source commit `ce5fd5a847904150a36615669e8c78009e14d6a7` after SC031. Production remains **NO_GO**.

## Boundary

Vault already owns append-only retention policy, legal hold, hold release and disposition-review metadata. Cloud owns opaque encrypted storage, integrity and recovery substrate. A valid Vault disposition review is therefore **not** a Cloud/provider delete command.

SC032 adds a strict source-only `TrustedVaultRetentionScope` and `source_retention_disposition_status()`. The scope binds the canonical encrypted object reference and ciphertext SHA to both the archival receipt's retention policy and the current governance policy. Policy mismatch, malformed canonical object/hash, an active legal hold without disposition block, or an impossible held+reviewed / blocked+reviewed state fails closed.

Even after a correctly governed disposition review, the returned state is `SOURCE_ONLY_DISPOSITION_REVIEWED_NO_DELETE`. The source contract keeps all of these false:

- Cloud delete capability exposed
- Provider delete authorized
- Vault canonical receipt deleted
- Backup delete authorized
- Production authorized

A separate future Tower/Vault deletion protocol, provider semantics, retention evidence, backup consequences, audit proof and explicit owner release remain mandatory before any destructive operation could even be designed.

## Actual merged source acceptance

The tests exercise the **real merged Vault** `RetentionGovernance` and `CanonicalEvidenceRegistry` alongside the Cloud local ciphertext backend. They show:

1. policy + legal hold blocks Vault disposition review;
2. releasing the hold allows Vault's metadata-only `DISPOSITION_REVIEWED` event;
3. the encrypted Cloud object still exists byte-for-byte afterward;
4. the append-only Vault archival receipt still exists;
5. Cloud's backend/service/bound-port interfaces expose no delete/remove/purge method;
6. the S3-compatible source adapter does not call `delete_object`;
7. owner-local evidence output explicitly says no retention/deletion protocol is connected;
8. retention output is redacted and never exposes object refs, hashes, version IDs or policy IDs.

This is deliberately stronger than merely saying “we do not call delete today”: the current Cloud source **does not have a deletion capability in its runtime contract**.

## Important limits

The absence of a Cloud delete API does not itself prove legal compliance, immutable retention or provider Object Lock. A privileged infrastructure operator could still delete bytes outside this source contract if the real provider policy allows it. Real provider retention/Object Lock, legal-hold enforcement, operator permissions, external audit custody and destructive-action review remain independent release gates.

Likewise, this work does not authorize indefinite retention by default as a legal/business policy. Vault/owner policy still determines what should be retained and when a disposition may be reviewed. SC032 only prevents a review state from silently becoming destructive storage authority.

No paid provider, production secret, hosted endpoint, real user document, live Tower signer, provider deletion API or destructive action is introduced.
