# TWR-OBML031–035 — Owner OB handoff replay-storage proof separation

**No live Manual Live authorization.** Source audit against dedicated Tower
\`cde18c80d886b34ee4b3885ffc21b00b81f2f35f\`.

The existing operational owner handoff in
\`tower/owner_observatory_handoff.py\` uses an HMAC-authenticated, single-use
SQLite code ledger and verifies the current Tower session, owner identity,
step-up and Observatory app access. Its \`handoff_configuration_status()\`
intentionally checks only whether the secret is present/long enough and the
ledger path is absolute. This is valid *configuration status*, not proof that
the SQLite file is backed by a persistent volume, has a coherent backup, or
will reject an old code after service restart/redeploy.

## New independent source-only gate

\`tower.ob.owner_replay_storage.audit.v1\` accepts an explicit ledger path and
putative approved private mount (not a browser-supplied security authority)
and checks absolute unambiguous paths, rejects common ephemeral temp roots,
forbids symlinked ancestry or public-readable DB/directories and checks that
the ledger is inside the proposed mount. It reports whether a mount was
observed, not that the provider guarantees durability. Tests use an injected
synthetic mount predicate and confirm that even a structurally good candidate
stays \`SOURCE_PATH_REVIEW_ONLY\` and \`may_issue_manual_live_grant=False\`.

These independent proofs CANNOT be performed by inspecting code or a path:
1. Provider-side verified volume/backup ownership and quota/retention.
2. Coherent database and encrypted related artifacts restore test.
3. Real deployed worker/restart/redeploy replay denial and revocation behavior.
4. Authenticated actual owner/OB crossing on the selected owner URL.
5. A distinct current account and OBML-purpose-bound step-up and review
   receiver; real broker, financial floors, market and owner Review Center
   gates remain separate.

No existing handoff runtime, Flask route, secret, provider environment or
storage path is mutated by this pack. Do not disable a working general
Tower→OB Survey/Paper corridor merely because the new audit is unverified;
also do not convert a source audit or a signed OB *namespace* into real
Manual Live L1 authority.

Issue #115 remains the actual release decision record. Owner authenticates
privately; GitHub receives blocker codes and redacted evidence only. The
owner has disapproved new paid BuyBox/Grounds provisioning and no paid Render
resource is introduced here. No date-driven mode activation.
