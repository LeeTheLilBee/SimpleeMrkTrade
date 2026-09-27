# VCR002–006 — Vault canonical evidence metadata / Simplee Cloud ref compatibility

This is a **source-only compatibility correction** to draft PR #64. The original
registry accepted only generic opaque identifiers and therefore rejected the
actual VLT1 managed-store/Cloud object key (objects/ followed by 48 lowercase
hexadecimal characters) supplied by Vault draft PR #38 and Cloud SC001 PR #65.
No real service can safely bridge the contracts without matching object refs.

This pack adopts that exact internal ciphertext-object reference in the Vault
metadata registry, preserving the opaque receipt/evidence/entity identifier
policy and refusing raw paths, URLs, wrong prefixes and malformed refs. The
test wall independently checks out Cloud SC001 at exact commit
52e64b7cfa967a5ed2e98cbcb48f94caf027c121, validates accepted/rejected
references against valid_object_ref, tests request replay and correction
lineage, and runs original Vault registry tests. The SQLite connection helper
now explicitly closes connections after transaction completion.

**Boundary:** source-shaped receipt references are preparation inputs. This
is NOT proof of Tower authorization, malware scanning, encryption success,
physical ciphertext existence, retention, externally certified immutability,
legal hold, archival completion or recoverability. A future trusted Vault
orchestrator must independently verify signed Tower authorization, scan,
Cloud physical write and reconciliation before issuing an archival receipt.
PR #64 remains draft. No paid provider, hosting or secret was created.

Review with PRs #35 (BuyBox metadata), #38 (Vault encrypted storage), #65
(separate Simplee Sovereign Cloud), and #70 (SC002 uncertain-write journal).
Never merge unrelated product branch trees wholesale.
