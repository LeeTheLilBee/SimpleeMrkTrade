# THE GROUNDS — implementation checkpoint / GRD006–019

Status: **source-only, local-testable developer build on draft PR #51**. This work advances the recovered GRD001–005 agreement without deploying resident login, activating a Tower door, using live resident records, creating payments, allocating capital, or provisioning a provider. Source-only means a real implementation exists in the repository for local tests and preview, NOT that it is connected to a real host.

## Delivered source

| Files | Capability |
| --- | --- |
| `grounds/access.py` | Deny-default normalized Tower scope, property/unit/role/assignment constraints and 5-minute maximum lifespan. A real issuer/signature/session/replay verifier is **injected and still missing**. The shape is an internal normalized form, not an assertion of wire compatibility with Tower. |
| `grounds/storage.py` | SQLite development data model: verified-close property record, buildings, units, one active lease per unit, work orders, append-only work events, notices, prospective lease/tour references and Vault work-proof references. PostgreSQL migration and hosted private storage are still future work. |
| `grounds/operations.py` | Verified-close-only property import boundary, staff-recorded buildings/units/leases, resident lease/unit cross-check before request/home, manager triage, scoped technician assignment, stale-revision denial, resident reopen, append-only event history, property notices and owner pulse with no fabricated collections data. |
| `grounds/teller.py` | Verified Teller-source projection tied to exact resident, property, unit and lease, 300s freshness ceiling, no raw checkout URL and no payment action. Display is `awaiting_verified_projection` until external Teller verification is provided. |
| `grounds/leasing.py` | Privacy-minimal unit availability, opaque contact reference, prospect stages and tour planning, all property scoped. No screening, applicant PII, approvals, external booking or notices. |
| `grounds/evidence.py` | Append-only references after externally verified sealed Vault proof; no file uploads/raw file URLs or direct Vault access. Photo refs submitted to unsupported intake explicitly fail, rather than silently disappearing. |
| `grounds/ui/preview.html` | Accessible/responsive, dark-glass local preview: Resident Home (lease, notices, rent unavailable, demo maintenance form/tracker), maintenance assigned queue, manager triage, leasing inventory and owner pulse. In-memory fictional work orders support role switching and review → assignment → technician completion → resident reopen. Browser refresh resets all data. |
| `grounds/test_*.py` / workflow | Pure data/authorization/state/financial-boundary regressions plus HTML preview and JavaScript syntax check. No real identities, payment network calls or provider secrets. |

## Boundaries required for live implementation

1. Tower must certify a real Grounds audience/issuer, separate resident and staff identity flows, property/unit and job-specific grants, revocation, CSRF, session/replay protection and auditable handoff/return. The test fixtures use identity verifier lambdas solely in `test_*.py`; **never expose them in an app server**.
2. The Grounds application needs a secure runtime, migrations from SQLite development schema to private PostgreSQL, encryption/access at rest, object/evidence referencing, real staff roster synchronization, durable audit/recovery and reliable notifications.
3. Teller must certify signed source-specific rent snapshots, amounts, autopay/invoice status and Tower-mediated hosted checkout intent. Grounds never processes ACH/card or invents balances, and cannot use OB balances as rent truth. The old term “resident ledger” means Grounds shows property/lease context and the versioned Teller financial projection; Teller remains the payment/financial ledger.
4. Vault must certify protected file/lease/notices/work-order evidence and only return Tower-mediated opaque proof metadata, not allow direct resident/vendor Vault access. Never pass unchecked photo references as sealed proof.
5. BuyBox may offer a close-handoff but a certified closing proof must be verified independently before writing ownership here. Grounds cannot automatically import a listing, infer a purchase or authorize acquisition.
6. Clouds receives sanitized owner-safe property status only from a signed operational publisher once actual source records and deployment have been certified. The older `grounds-clouds-source-wave2` branch is projection-only and remains untouched.
7. Soulaana explains the owner/manager/resident views using source evidence and permissions. She never performs legal screening, autonomous property mutations, payment routing, or capital decisions.

## Scope still to implement

The accepted original 80+50 feature scope remains the destination. The original exact numbered list was not available in retrieved materials, so this checkpoint does not claim to complete or restate it verbatim. Remaining operational work includes verified Tower receiver and UI, Teller checkout, real Vault evidence, hosted deployment with backups/restore proof, staff/vendor assignment and notifications, preventative maintenance, inspections, move-in/out, turnover, warranties/assets, application/tour workflows, taxes and assessment appeal tracking, utilities/insurance/CapEx, capital readiness, accessibility/resident needs, owner/regional controls and a real private owner beta.

## Build safety decisions

- All preview data is fictional, in-memory, and visibly labeled.
- Do not add `/tower/launch/grounds` merely because an app appears in a registry.
- Keep existing OB/Teller/Tower/Vault source branches, prior signed contracts, mission-account floors and payment controls unchanged.
- No real tenant details in this branch or the local preview; no production claims on a green contract test.
