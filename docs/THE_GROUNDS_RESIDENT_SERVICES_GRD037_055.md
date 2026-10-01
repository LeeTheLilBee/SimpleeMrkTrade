# The Grounds — resident services, Soulaana and release-readiness / GRD037–055

**Current state:** source-only, local-testable code on [draft Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51). It must **not** be deployed as a resident product, activated from Tower, provisioned on paid Render or fed real tenant data until the separate security and integration gates below are met. The authoritative Tower counterpart is [draft Tower PR #52](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/52), targeting `tower-dev`. The latter is an inspectable requirements PR, not an actual identity integration.

## Implemented in this batch

| Packs | Local developer implementation | Reality boundary |
| --- | --- | --- |
| GRD037–040 | `lease_members` and append-only events; primary member registered on lease activation, certified-proof-granted co-tenants/authorized occupants and proof-gated revocation; all resident Home, own-job visibility and intake recheck active membership. Lease end ends members transactionally. | An occupant never inherits signing/payment rights by association. Grounds denial does not itself revoke a Tower session; Tower must also revoke grants. Certified proof callbacks in tests are local fixtures. |
| GRD041–044 | Notice read records per resident (not delivery), maintenance appointment request → staff proposal → resident acceptance/cancellation, timezone-aware window checks and revision/audit events. | No SMS/email/push, real calendar, staff dispatch, authorized entry or legal notice service. Co-tenants may not view each other's private requests by default. |
| GRD045–047 | Protected inspection/turnover summary selectors and source-scoped Soulaana explanations for resident lease, **fresh and explicitly verified Teller rent**, verified apartment readiness, appointments, inspections/findings, turnovers, leasing unit lifecycle and owner property pulse. | This is deterministic, read-only explanation code, not a live conversational/voice model. Sources/revisions/scopes must be checked by the actual service; cannot authorize a housing, payment or access decision. Legacy `explain_apartment_readiness` is an internal helper for an already verified projection; the untrusted-input entrypoint is `explain_verified_apartment_readiness`. |
| GRD048–049 | Dark-glass local preview now has all **13** documented role rooms, with role switching, in-tab fictional maintenance, local notice read, appointment proposal/acceptance and Soulaana drawer. | The eight additional staff rooms are source/design previews awaiting real assignment-specific data and integration. No external network, storage, login or provider calls. |
| GRD050–054 | Human urgency review record; flagged urgent work cannot proceed from submitted to received before reviewed. Local entry preference revision/history, with explicit 'no entry' blocking job start. Transactional, metadata-only pending event intents for work state changes, urgent intake and notices. | Human acknowledgement is **not emergency dispatch**. Pending outbox is **not delivery**. Appointment acceptance, work in progress and even recorded entry preference are **not legal entry notice or certified permission**. Notifications need dedicated trusted worker, receipt, recipient consent and emergency escalation policy. |
| GRD055 | `foundation_status()` explicitly identifies the above local functions and preserves false flags for live Tower, Teller, Vault, payment, emergency dispatch, notification delivery and live Soulaana. | Green source-only tests do not unlock runtime or grant identities. |

All developer tests use fictitious properties, units and residents. In particular, do **not** copy the fixture verifier lambdas into any web service.

## Remaining critical gates — do not conflate specification with activation

1. **Tower:** certify separate resident/staff/owner identity sessions, member/grant verification for exact lease/property/unit and time period; inspector/vendor/technician job assignments and expiry, household consent and revocation, owner sensitive-action step-up, nonce/session/audience/replay protection, audit and lockback. Resolve authoritative Tower branch with PR #52 before integrating.
2. **Teller:** formal verified invoice and checkout/return/reconciliation contract, pending/failed/partial/returned payments, autopay, refunds, receipts, replay/idempotency and disconnection behavior. Grounds shows Teller-sourced money facts and cannot route money directly or infer spendable acquisition cash from OB.
3. **Archive Vault:** sealed lease/notice/inspection/work-photo/turnover proof intake with content protections (file type/size/malware/retention), restricted ownership and exact work/lease/finding bind. No unverified arbitrary proof refs, public URLs or direct tenant Vault portal.
4. **Durable private application:** real, authenticated Grounds API/UI; hosted database and migration from local SQLite model; tenant data encryption and separation, backup/restore test, retention/audit/security review, emergency/manual fallback, monitoring and revocation rechecks. No paid resources under the owner's standing restriction.
5. **Resident operations:** contact/communication preferences, physical-entry consent and any applicable notice rules, accessibility and urgent human response path, failure receipts, actual notification sender, lease renewal/move-out rules, staff inspection/vendor assignments, real receipts, and privacy/household controls.
6. **Next business capability:** assets/warranties/service history, maintenance parts/labor/scheduling, tax/insurance/utilities, preventive work and CapEx, resident dispute workflows, owner/regional management, Clouds permission-safe snapshots, Soulaana on certified live source adapters and BuyBox's post-verified-close import.
7. **Jurisdictional review:** rental/lease/fee/deposit/entry/notice/accessibility/fair-housing rules must be reviewed against applicable properties and requirements before launching. The current code is not legal advice, legal notice delivery or an automated screening engine.

## Security invariants

- New lease activation requires actual `ready` unit; a turnkey task cannot substitute for a verified turnover-specific inspection and its final proof.
- Resident visibility requires BOTH current Tower scope AND active Grounds membership. Revoke/lease-end immediately removes Grounds resident access even if Tower has stale grants, and triggers a separate Tower session invalidation requirement.
- Staff scope is strictly property/assignment-bound. Inspector and temporary vendor self-service remain locked until Tower certifies concrete assignments.
- A serious inspection finding cannot be closed without certified, finding-bound resolution evidence.
- A resident's urgent flag is a human triage signal, **not** a report that emergency services were called.
- An in-app read receipt, appointment, work-status change or Soulaana explanation never substitutes for actual communication delivery, resident permission, regulated notice or money movement.

This checkpoint does not assert that the complete earlier 130-feature numbered list was recovered or implemented. The scope is the known original grouped plan plus latest integration corrections.
