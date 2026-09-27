# BBX032–036 — local encrypted original and frozen-snapshot preflight

**Status: source-only integrity check, NOT Tower/Vault archival or live release.**
This pack follows merged BBX027–031 on the BuyBox development branch.

## Actual source reviewed
- BuyBox original bytes are encrypted and kept under a private opaque reference
  by \`buybox/documents.py\`. \`PrivateDocumentStore.read\` decrypts and
  compares SHA-256 and length. It is **not** canonical Vault storage.
- \`buybox/tower_evidence.py\` freezes evidence ID, artifact ID/hash, opportunity
  revision and a local decision snapshot; metadata drafts are intentionally
  untrusted, not network requests.
- Draft PR #35's \`buybox.vault.evidence.v1\` is metadata-only. Its proposed
  Tower helper currently receives caller-provided gate booleans; production
  Tower must derive them from authenticated authoritative state. An
  \`ARCHIVED\`-shaped response is not an archive receipt or verified issuer.
- Local CSV intake is accepted by BuyBox but is **not** in PR #35's canonical
  Vault v1 MIME allowlist. Do not silently promote CSV to a Vault candidate.

## New source-only check
\`buybox.vault.local_original_preflight.v1\` reads the exact persisted current
opportunity with \`stored_source_snapshot\`, requiring matching saved revision
and digest. It verifies that exactly one current artifact, evidence record and
frozen snapshot match the chosen IDs, that the snapshot's own hash and
version/evidence lineage are intact and it was saved as the **latest** snapshot
(revision N frozen, saved as revision N+1). Later edits invalidate this
preflight and require a new freeze/save. It then reads and decrypts the actual
private original, rechecks the declared length, SHA-256 and MIME magic/UTF-8.

A success reports only \`LOCAL_ORIGINAL_VERIFIED_UNSENT\`, source refs/hash
and local metadata. It **never** returns original bytes, storage paths, an
external Vault path or a download token. It leaves Tower identity/owner
approval, malware scan, actual binary transfer, Vault receipt, archival and
acquisition permission false.

## Tested adverse cases
Synthetic encrypted PDF accepted only after actual freeze+save; unsaved or
stale snapshot denied; tampered snapshot digest, falsified evidence lineage,
corrupted ciphertext and persisted source digest denied; CSV deliberately
excluded. No real user document or external transport is used.

## Further Group 4 requirements
1. Independently authenticated Tower user/entity/action/step-up/approval
   and purpose/retention/redaction checks; do not trust request-shaped
   \`tower_context\` flags.
2. A bounded protected source-to-Vault binary transfer behind Tower, quarantine,
   malware scanner, content type/digest/size checks and safe failure/retry.
3. Vault independent encrypted canonical storage, append-only version/correction
   chain, retention/legal holds and protected receipt issuance.
4. Tower receipt verification and status reconciliation back to BuyBox; only
   a canonical signed/verified receipt can establish ARCHIVED. A local
   preflight, metadata draft or user-supplied ARCHIVED string cannot.
5. Real private storage/backups/restore and authorized hosted owner crossing
   before enabling any records, download or archival operation.

BuyBox remains **source-only**. No paid Render service, disk, provider, secret,
real Vault activation or protected Tower endpoint. See issues #42 and #54.
