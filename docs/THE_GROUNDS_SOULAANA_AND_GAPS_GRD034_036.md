# The Grounds — Soulaana and gap audit / GRD034–036

Status: **planning and source-only review checkpoint** for Grounds PR #51; neither this document nor a passing local test makes The Grounds tenant-ready. Tower crossing review stays in PR #52.

## Soulaana: in source, not fully integrated

- `grounds/soulaana.py` currently has `explain_work_order` and `explain_apartment_readiness` (GRD022). They provide **deterministic, read-only**, source-linked messages. Maintenance explanation obtains an already access-checked work order; readiness explanation consumes a Teller-marked projection. The static local `grounds/ui/preview.html` has a Soulaana explanation drawer based on fictional in-memory data.
- No real LLM/voice, chat memory, notifications, external model access or production API is wired. The owner preview uses sample data and the owner financial view must remain Teller-mediated.
- Before runtime, every explanation must use a **certified source object**, not merely a user-supplied dict claiming `source='teller'`. A trusted service must fetch/verify the current projection and the authorized property/lease/job scope. Reject stale/mismatched context rather than making a persuasive explanation out of bad data. Expose source, timestamp/revision, relevant limits, next action and explicit inability to execute. Do not surface one resident's private information in a manager/vendor/other-resident context.
- Expansion map:
  - Resident: rent due/partial/payment-failed *only from Teller*, lease dates/documents from Grounds/Vault, maintenance changes, entry permission, what to do in urgent cases, notices, appointments, renewal/move-out.
  - Maintenance tech/supervisor: scope, priority/urgency flag vs actual dispatcher decision, access permission, schedule, parts/labor, proof required, what blocks closure, hand-off when unavailable.
  - Leasing: real availability, prospect stage, tours, missing evidence and neutral status explanations. No autonomous applicant selection, legal screening or fabricated rent/availability.
  - Property/regional manager: inspections, serious finding remediation, vacancies, turnover blockers, resident issues, vendor capacity, compliance dates, budgets and CapEx dependency explanations.
  - Owner: physical property and lifecycle pulse, Teller-mediated five apartment reserve lanes, source freshness, why readiness changed, BuyBox verified-close handoff, safe Clouds summary.
  - Other scoped rooms: inspector, turnover, janitorial/grounds, renovation, vendor, compliance — only assigned records; do not give unassigned workers portfolio/tenant visibility.
- Interaction design: consistent Soulaana drawer/chip in each role's room; explain **what happened / why / source and when / what is missing / next useful action**. A suggested action is never an authorized action. Clear disclosure when an emergency report has not actually been dispatched.

## Highest-priority operational gaps

1. **Tower identity and authority.** Separate resident, employee/vendor and owner sessions. Real signed/revocable nonreplayable Tower receiver; membership and active lease/household grants; staff role/property/inspection/task scopes; delegated vendor expiry; owner step-up. Role labels and fixture callbacks are not security. PR #52 handles review, not activation.
2. **Rent/Teller handoff.** Real invoice/due-date/autopay/partial/failed/returned/refund handling, safe redirect/return and webhook replay reconciliation. Receipts come from Teller; Grounds never invents collections, directly accesses OB, or accepts a pasted checkout URL as proof.
3. **Resident lifecycle and privacy.** Household/authorized co-tenant occupancy, permissions for minors/guests, consent/records, privacy retention and move-out/ended-lease access. The local schema models one active lease row per unit and one resident ref, **not** the full resident-household model. Do not use these source-only endpoints to effect real termination/eviction.
4. **Maintenance delivery and urgency.** Real human triage/escalation, reliable urgent notifications with acknowledgment and after-hours escalation; appointments, accessibility accommodations, entry/notice permissions and re-confirmation; scoped before/after photos, labor/materials, vendors/parts and resident confirmation/reopen policy. An `emergency_flag` alone is not dispatch.
5. **Legal/compliance requirements.** Localized rental/notice/entry/deposit/records/fee policies require current jurisdiction-specific professional review before writing production rules. Add documented fair-housing and accessibility safeguards, audit logs, dispute paths and staff training rather than trying to automate legal decisions.
6. **Lease/turnover integrity.** Unit must be actually ready before lease activation; a closed inspection must belong to the exact turnover, not merely the same unit/day; trace lease-close and turnover proof. GRD034–035 now harden the *local reference model* for the first two conditions. Real lease issuance/end/renewal must require a certified Vault/Tower process, not simply a manager passing a string.
7. **Real evidence and notices.** Secure private file ingestion with type/size/scan/retention safeguards and signed Tower/Vault proof; no raw file URLs in work orders. Versioned notice templates, targeted audience, delivery/acknowledgment status and reliable audit receipts, including failure cases.
8. **Private runtime and operations.** Hosted encrypted durable datastore, migrations from SQLite local model, backups/restore drills, retention/deletion, monitoring, tenant data isolation, incident/lockback controls and a real role-based API/UI. No paid resources or real data until owner approval and security certification.
9. **Broader portfolio work.** Asset warranties/serials/replace cycles, preventive schedules, utility and insurance intelligence, tax assessment/exemption/appeal tracking, CapEx and remodel sequencing, accessibility, vendor compliance, shared-space/parking/storage and staff workloads. BuyBox remains pre-close and Clouds receives sanitized status; no duplication of authoritative ledgers.

## Sequence and non-negotiable release gates

- First: finish the source-only domain hardening, add an explicit household/occupant and assignment model, close inspection/turnover loopholes and test cross-property/role exposure.
- Then: Tower receiver + private staff/resident beta and private durable storage, both certified and staged at no paid infrastructure without owner permission.
- Then: resident Home/maintenance/notice workflow and live protected proof; Teller rent checkout with webhook/idempotency failures; Soulaana context from verified sources only.
- Then: leasing/renewal/turnover, service scheduling and staff/vendor roles; financial and physical audit/reconciliation; owner-safe Clouds and verified BuyBox close handoff.
- Finally: advanced property stewardship, tax/insurance/utilities/compliance/CapEx modules and an audited real-tenant release.

**No change in authority:** Tower controls access; Grounds owns physical property/resident operating context; Teller owns financial and payment truth; Archive Vault owns sealed proof; BuyBox owns pre-close diligence; Clouds gets permission-safe owner status; Soulaana explains but does not decide or execute. All five apartment mission lanes retain protected floors. No paid Render resources, live payment, asset acquisition, broker mode change or auto-unlock is authorized by this audit.
