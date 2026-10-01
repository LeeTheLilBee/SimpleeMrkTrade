# THE GROUNDS — recovered product decisions / GRD001–005

Status: source-only product/domain foundation, **not** deployed or tenant-ready. Based on the prior SimpleeProperty planning accepted July 11, 2026 and subsequent boundary corrections. The original agreement referred to 80 initial features plus 50 additions (130 total); the complete verbatim numbered list has not been recovered here. Do **not** represent the groupings below as a transcription of that missing numbered inventory.

## Product identity and experience

The Grounds is Simplee World's resident-facing and staff-facing owned-property operations system, not just an owner asset dashboard. One Grounds app offers property- and role-scoped workspaces for residents; maintenance technicians and supervisors; leasing agents; property managers and regional managers; inspectors, turnover teams, grounds/janitorial and renovation coordinators; compliance personnel; temporarily assigned outside vendors; and owner views.

Resident Home: current lease/unit, amount due and due date sourced from Teller, Pay Rent and autopay handoff, payments/history and receipts, notices, maintenance ticket submission/tracking, photos, entry permission, preferred appointment windows, and status updates. The resident stays in one cohesive experience; the hosted Teller payment boundary remains separate internally.

Maintenance: mobile assignment/route board, urgency/emergency flag and human triage, scope-limited necessary access details, schedule, start/pause/escalate, labor/materials/parts, equipment history, before/after proof, completion review, resident confirmation or reopening. Status path: submitted → received → under_review → scheduled → assigned → in_progress → waiting (optional) → completed → confirmation → closed/reopened; reopened returns to review. Preventive work, inspections, turnovers/make-ready, vendors, hazards, and renovations share asset-linked history.

Leasing: unit inventory and vacancy/condition, floor plans, amenities/accessibility/parking/storage, leads and tours, matching and waitlists, applications, follow-ups, rent and concession context, move-ins, renewals, turnover coordination.

Manager/owner: buildings, units, occupancy, leasing, resident issues, work queues, contractors, compliance deadlines, taxes/assessments/exemptions/appeal tracking, utilities, sustainability/infrastructure, insurance, CapEx and remodel sequencing, financing/expense context and permission-safe decision packets. Original planning also includes acquisition/close handoff, but active search/underwriting is now BuyBox-owned.

## Responsibility boundaries (latest decisions prevail)

| System | Authoritative responsibility |
| --- | --- |
| Grounds | post-close properties, buildings, units, resident/lease context, occupancy, maintenance, inspections, vendors, turnovers, asset history and resident operating experience |
| Teller | rent invoice and financial/payment status, hosted checkout, ACH/card processing, autopay, partial/failed/returned payments, refunds, reconciliation, receipts, vendor/employee payments and financial administration |
| Tower | identity, resident-to-unit and staff-to-property/assignment scoping, permissions, role grants, step-up, controlled cross-system handoffs, audit; default deny |
| Archive Vault | sealed lease, notice, inspection, work-order and payment proof via Tower-mediated references; no direct resident/Vault access |
| Clouds | owner-safe property/portfolio pulse, not an alternative operations UI |
| BuyBox | pre-close discovery, due diligence, underwriting, decision and handoff after actual verified close; Grounds does not duplicate its marketplace |
| OB | distinct capital/mission policy source, not tenant rent checkout nor direct spendable capital assumption |

Earlier language referred to a Grounds resident ledger. Following the later Teller scope decision, Grounds may hold the lease/property obligation context and present a versioned Teller financial projection; it must not establish a competing authoritative payment/invoice ledger or derive spendable acquisition capital from OB. BuyBox receives money-side readiness from Teller, not OB.

## Apartment capital and readiness planning

The apartment mission contains five separately funded lanes: Down Payment, Closing Costs, Repair/CapEx, Operating/Emergency Reserve, and Manager/Ops Remodel. Preserve the difference between current, target, hard-bottom, unused, actually available above floor, committed and protected amounts. A funded down payment with weak reserves is not a safe acquisition green light. Grounds displays Teller-mediated capital/readiness status and phases optional manager/operations remodel rather than releasing protected reserves. No direct OB connection or financial execution here.

Originally proposed manager-space remodel stages: manager office → Grounds/Teller operations room → owner office/records/resident area → Tower/Clouds wall → additional infrastructure only when cash flow supports it.

## Build order

1. GRD001–005: recover decisions, isolate source-only roles, resident/rent boundary, pure maintenance state machine and regression tests (this branch).
2. Property/building/unit/lease/occupancy model; versioned records and real persistence only behind tested property-scoped authorization.
3. Tower Grounds edge and **separate resident/staff identities** with verified role/assignment handoffs, deny-by-default, step-up on sensitive actions, security and privacy tests.
4. Resident Home, leasing/manager/maintenance workspaces and protected evidence intake with durable audit/asset history.
5. Teller rent/payment integration (no invented checkout/balances), Vault proof references, notices and resident communications; failure/replay/staleness reconciliation tests.
6. BuyBox verified-close import (not automatically trusted), Teller-mediated financial readiness, safe Clouds publisher, Soulaana context explanations, owner beta and deployment certification.
7. Broader 130-feature scope: advanced tax intelligence, utilities, capital improvements, compliance, community tools, additional staff workflows.

## Current execution constraints

- No protected `/grounds` route, Tower entitlement/launch unlock, resident login, real tenant data or live billing.
- No paid Render provisioning, synthetic production dashboard, Vault direct writes, capital movement, OB trading changes or automatic acquisitions.
- No merging this draft into main, no altering the historical `grounds-clouds-source-wave2` branch, and no claim the legacy projection publisher is a live operating system.
- Test modules are pure, standard-library source contracts. Their role input is **not authentication or authorization**: only a later Tower-attested entrypoint may invoke business mutations.
