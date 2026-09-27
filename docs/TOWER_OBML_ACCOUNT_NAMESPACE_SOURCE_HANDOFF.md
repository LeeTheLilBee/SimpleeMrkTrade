# TWR–OBML account namespace signature check — source-only Monday handoff

Parent: `c183606775ee82d8ee5e4290529bdc798b0fd1bc` (accepted OBML011–015 redacted owner-beta gate report). Related Tower clearance request **draft PR #68** and separate OB mission-account export **draft PR #80**. This isolated implementation does not modify either branch or assert their draft code is merged.

## Boundary

`tower/obml_account_namespace_source.py` verifies the exact `obai1` wire shape proposed in PR #80 using a trusted **caller-injected** HMAC key, canonical OBAUTH mission-account identity/fingerprint, exact issuer/audience, zero grant flags, short issue/expiry window (max 60 seconds), and a **caller-supplied durable atomic** one-time nonce consumer. Signature is verified before reading JSON. Duplicate JSON keys, noncanonical base64, unknown fields, wrong/missing issuer, demo/unknown/default account, wrong key, replay, expired/future claim, storage failure and forbidden owner/broker/money assertions fail closed. No raw token, HMAC key, nonce or broker ID appears in the returned source-only receipt or errors.

This source check is deliberately **not** the Tower owner authentication and clearance verifier. A valid signature only establishes that the canonical OB namespace source used the provisioned key. Tower still needs a true server-owned owner session, account entitlement, purpose-bound fresh step-up, current revocation, atomic challenge/nonce replay security for *the Tower handoff*, exact route/audience/permission, denial/audit, and actual hosted crossing. The OB owner source preflight, safety/recovery, actual broker provider/options/settlement proof, protected reserves, Review Center human decision and independent manual fill reconciliation remain separate. Do not fold those authorities into this source verifier.

There is **no production key**, key transport, configured endpoint, nonce store, route, deployment, paid resource or Manual Live unlock in this PR. Tower implementation owner must supply key via managed server configuration and an appropriate durable shared nonce store, review key ownership/rotation and verify that this source-only receipt never gets promoted to a Tower owner/session grant. No app code may pass user-controlled key material or an in-memory nonshared nonce consumer as production evidence.

## Monday integration acceptance

1. Review and land PR #80 producer only after its tests pass; verify its emitted token end-to-end against this consumer with a **test key**, not production credentials. Freeze schema and key ownership jointly.
2. Merge or apply draft PR #68 handoff request into the canonical Tower workstream after resolving its older base; verify Tower's actual session/permission/step-up/revocation/replay issuer and OB receiver, with negative tests.
3. Test cross-account and Proof/Demo refusal, nonce replay across worker/process restart, revoked/missing session, stale step-up, wrong purpose/audience/route, stale market and canonical safety BLOCK. Verify no live mode opens from a good namespace signature.
4. Perform owner beta through Tower → OB on a genuinely available hosted runtime. Until trusted external Tower/broker evidence exists, label the result Survey/Paper or owner rehearsal only, not broker-backed Manual Live.
5. Do not provision paid Render or external resources; do not wire an OB broker API or bypass Teller for acquisition readiness.

A CI-green source verifier provides one bounded cryptographic compatibility check; it is not deployment acceptance, provider authentication, owner clearance, or a trading authorization.
