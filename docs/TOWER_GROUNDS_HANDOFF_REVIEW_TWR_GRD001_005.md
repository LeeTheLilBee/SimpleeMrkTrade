# Tower ↔ Grounds handoff — review request / TWR-GRD001–005

Status: **source-only draft for Tower chat review**, not an implementation, integration acceptance or runtime entitlement. Grounds implementation lives on [Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51) (`grounds-resident-operations-grd001-005`, GRD001–023 at creation of this request). This PR is deliberately based on `tower-dev` to avoid changing the concurrent Grounds PR and active Tower/Teller work. If Tower's authoritative branch moved since this checkpoint, reconcile/cherry-pick deliberately rather than overwriting it.

## Critical correction to historical Tower metadata

An older Tower registry describes Grounds as owner-only with a future `/grounds` room. **That cannot be the final operating model.** Grounds is an owned-property application with three separate identity contexts: resident, authorized employee/vendor, and owner. Registering Grounds or showing a card is not granting access, and merely setting `owner_only=False` without implementing scoped verification would be unsafe. Keep current route locked until real crossings are certified.

## Handoff Tower must design/certify

1. Separate resident and staff onboarding/sessions, plus owner. No user-supplied role, property ID, unit ID, or assignment grants. Preserve session binding, multi-factor/step-up as appropriate, revocation, expiry, return flow, audit, tenant privacy and incident rollback.
2. Attested issuer/audience specifically for Grounds. Develop an actual signed and replay-resistant handoff consistent with Tower's authoritative protocols; the normalized claims in Grounds `grounds/access.py` are **internal shape, not a live wire or issuer contract**. Reconcile exact role list, property membership, unit/active-lease membership, and technician/vendor work assignment. Distinguish persistent employment/lease access from temporary delegated/vendor assignment. Inspection self-service requires its own inspection-specific assignment and revocation checks; Grounds currently blocks inspector writes pending that certification (GRD024–033 in Grounds PR #51). Deny missing/mismatched/expired/stale roles.
3. Scope every Grounds read/write server side, including list/search and attachments, to user+property+unit/job; revalidate when lease ends, resident moves, worker assignment revokes, ownership changes, or privileges narrow. Avoid cross-property existence leaks and resident lookup by ID.
4. Tower-mediated Teller rent checkout. Grounds renders lease context and verified Teller invoice status and requests a scoped checkout intent; **Teller alone** processes ACH/card, receipts, returns and financial reconciliation. Tower must not assume a string/URL is a verified payment handoff.
5. Tower-mediated Vault sealed lease, notice and maintenance proof reference. Never grant a resident direct Vault access. Grounds currently rejects unverified lease proof and unsupported photo intake; add a real proof receiver before activating uploads/documents.
6. Verified BuyBox closing handoff. A listing or proposed deal must not become owned property until closing evidence is checked. Grounds may request Teller readiness; BuyBox consumes Teller readiness, never direct OB balances.
7. Clouds takes safe, redacted operational snapshots only after a real Grounds publisher and operating source are validated. Soulaana is explanatory/read-only and must respect the same scope.

## Acceptance prerequisites / handoff for the other Tower chat

- Decide canonical branch and reconcile with current Tower app registry, hosted identity and Teller boundary work.
- Specify exact issuer/audience, handoff signing/replay/nonce/session and property/lease/job authorization claims; locate authoritative Tower owner and external-user authentication mechanisms rather than inventing a parallel login.
- Create a real Grounds receiver and protected routes only after dedicated private storage, secrets, backups/restore proof, PII handling, denial regressions and owner acceptance are confirmed.
- Verify resident-to-resident, unit-to-unit, property-to-property, technician-to-job, temporary vendor expiry, stale/replayed token, step-up, rent spoofing and Vault proof spoofing negative tests.
- Tower must own the status transition. This checklist module's outputs **never** enable a route or mint a token.

### Explicit non-effects

No changes to OBSERVATORY trading, existing Tower/OB/Teller/Vault access routes, current hosted deployment, rent payments, tenant accounts, paid Render, or protected capital. This PR contributes an inspectable requirements contract and negative tests, not a production crossing.
