# Tower ↔ Grounds source scope review — TWR-GRD007–011

Status: **source-only reviewer, no effective grants, no endpoint, no production Grounds session**.

## Reviewed authorities and branch isolation

Tower PR #52 was reviewed at \`396f50b1e17ec220d1d28e0212678b567315c165\`, passed both exact-head CI runs, and merged into the dedicated Tower line at \`dffa3d9c45df3484f523de4178658924a33831a0\`. Do not merge older \`tower-dev\` wholesale: it was 39 commits behind the actively hosted Tower branch when reconciled. This pack uses the actual thirteen Grounds roles from \`grounds/contract.py\` at independent Grounds PR #51 source \`ec4919ad1a35503c54d2fb907c8bf08ed573583d\`, pinned for CI. Grounds's normalized \`grounds/access.py\` is an internal shape, not a signed real Tower wire or a trusted tenant login.

## New exact source-only interface

\`tower.grounds.scope.review.v1\` consumes an *untrusted proposed* claims mapping with exactly the fields in TWR-GRD001–006 \`ALLOWED_CLAIM_FIELDS\`:
\`issuer\`, \`audience\`, \`subject_ref\`, \`session_ref\`, \`role\`, \`property_refs\`, \`unit_refs\`, \`assigned_work_refs\`, \`issued_at\`, and \`expires_at\`. A separate exact target has \`property_ref\`, nullable \`unit_ref\`, nullable \`assigned_work_ref\`, and a documented \`operation\`. Role identifiers must match the independent Grounds source. Review bounds expiry to 300 seconds and rejects malformed references, duplicates, unknown roles, unsupported operations, stale/future claims and extra authority booleans. It compares proposed property/unit/job intersections and distinguishes resident, staff/vendor and owner shapes.

A matching proposal returns only \`UNTRUSTED_SOURCE_REVIEW\` and a \`candidate_scope_match\` formatting indicator. It **never** validates a signature, session, active lease, occupant or co-tenant relationship, technician/vendor assignment, notice delivery, physical-entry consent, Teller status, Vault receipt or hosting evidence; \`launch_authorized\`, \`session_created\` and every other side effect remain false. A user's asserted \`step_up_active\`, \`lease_membership_current\`, \`approved\`, \`entry_permission\` or \`signed_by_tower\` is rejected as an excess field, not promoted to evidence.

The checks explicitly distinguish an in-app notice-read record from delivery/legal service, appointment request from legally authorized entry, an urgent resident report from on-call human triage and actual recipient delivery, and Grounds rent display from Teller's verified invoice and checkout. \`owner\` alone does not authorize physical access. Neither claimed unit scope nor unchanged Tower scope overrides Grounds's current active lease/household membership. A vendor/technician/inspector must have actual current assignment checked by the future authorized receiver, even if a proposed work reference matches.

## Remaining implementation gates

1. Independently authenticated Tower resident and staff identity, step-up policy, owner scope, actual issuer/audience/single-use receiver and session revocation; never use the source reviewer as an access gate.
2. Grants derived from current authoritative person, property and lease/household and staff/job records; Grounds independently rechecks each list/read/write after lease end, member removal, assignment expiry or transfer. No cross-property or cross-unit existence leaks.
3. Actual private storage and backup/restore review, role-based PII boundaries and source logging; no real resident data or paid resources before owner approval.
4. Separate Tower-mediated Teller rent invoice/checkout/reconciliation; Vault lease/notice/work evidence, verified receipts and retention; actual human urgent escalation and delivery receipts. Source strings, local notifications and appointments are not those events.
5. Complete negative tests, actual hosted revision and owner acceptance before adding a real \`/tower/launch/grounds\` route. Preserve the existing owner-facing Tower and OB/Teller boundaries.

**No change to Tower app registry, live Grounds access or payment route by this pack.**
Track with [master groups #54](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/54) and [Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51).
