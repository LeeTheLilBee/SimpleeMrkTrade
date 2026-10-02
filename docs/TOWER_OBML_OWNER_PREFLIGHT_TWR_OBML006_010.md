# TWR-OBML006–010 — Observatory Manual Live L1 owner-review Tower reconciliation

**Source only. No owner Manual Live clearance, mode unlock, broker order, trade
intent, capital movement, protected-floor release or hosted release authorization.**

Reviewed the independently authored owner request [PR #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68)
at exact commit \`badef7fab30f93be6878d89b28f4863cfa6fc202\`,
including its machine-readable request contract and source-only tests. It
targets \`main\` because it is an OB handoff request; do not merge \`main\` or
old \`tower-dev\` wholesale into the dedicated Tower branch. This change
targets \`tower-hosted-runtime-identity-twr081-085\`, keeping the existing
\`/tower/launch/observatory\` → \`/ob/dashboard\` operational corridor.

## Existing authoritative source evaluated

- \`tower/tower_human_login_ob_launch.py\`: authenticated owner session,
  existing generic step-up, session identifier and one-time operational OB
  handoff/receipt. That receipt proves only its defined operational OB entry,
  **not** a new account-specific Manual Live review grant.
- \`tower/owner_observatory_handoff.py\`: existing owner handoff and
  operational access receipt/ledger; do not fork a second master-key engine.
- \`tower/identity_authority.py\` and \`app_truth_projection.py\`:
  verified current hosted owner/OB entitlement distinct from publication.
- \`tower/step_up_auth.py\`, \`ob_mode_clearance.py\`,
  \`ob_tower_bridge_adapter.py\` and \`ob_tower_route_guard.py\`:
  older general purpose/route/mode review; do not interpret a legacy display
  flag or generic step-up as \`OBML_OWNER_REVIEW\` or verified broker status.

## This pack

\`tower.obml.owner.review.preflight.v1\` reads current Tower owner session,
generic step-up, existing operational OB receipt, hosted identity and
authoritative OB publication. It returns a redacted **BLOCKED** assessment
even if all those inputs are verified. It explicitly identifies the
additional independent gates: fresh OBML-purpose-bound step-up; exact
canonical OB mission-account identity; current revocation/nonce ledger;
OB operating mode/Effective Policy + OBSAFE/OBREC/OBATTN/OBRES lineage and
market-source freshness; separate broker-account/options-permission evidence;
owner Review Center receipt; and real Tower issuer plus independently
validated OB receiver.

No route, token, claim-driven launch, new identity engine or browser secret
is created. A requested level of Manual Live is not a current mode clearance.
The output is amount-free and all broker/API/hybrid/automatic execution,
capital/mandate release and override capabilities remain False.

## Next independent work

1. Bind exact OB account ID/fingerprint to Tower-derived authenticated owner
   and mission account. Recheck source and protect against changed account
   selection and stale capital policy; no BuyBox cross-access to OB balances.
2. Implement a distinct OBML-review-only fresh step-up event and independent
   current revocation/session/entitlement checks using Tower authority.
3. Define an actual signed one-use, short TTL issuer and consuming OB review
   adapter without duplicating the existing operational owner launch. Recheck
   purpose, audience, route, account identity and nonce, and log redacted
   outcomes. Do not use a caller-supplied \`verified_tower_attestation\`
   boolean as proof.
4. OB independently checks canonical mode and effective policy/kill switch,
   evidence and broker permissions and human Review Center receipt. Even a
   positive Tower review does not issue a broker order or unlock Live.
5. Full negative tests plus authenticated hosted owner acceptance before
   advertising a usable Manual Live review. Owner must independently place
   any authorized order on the broker's own website/app.

No paid Render/service procurement; PR #68 remains a request, not a live
deployment/authorization. Track master execution issue #54.
