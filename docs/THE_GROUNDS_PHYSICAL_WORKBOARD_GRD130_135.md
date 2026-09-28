# Grounds GRD130–135 — physical-operations workboard (source only)

This package projects actual Grounds physical-domain records to the already protected resident/staff web application. It does **not** schedule a provider, authorize entry, create an inspection attestation, open a Vault proof, spend money or grant an assignment.

## Authorized workboard

`GroundsStewardship.physical_workboard(actor, property_ref)` revalidates an authenticated current TowerScope on every call. Only owner, property manager and maintenance supervisor may see asset and due-preventive-plan indices and open inspection metadata for their property. Turnover metadata and its count are **completely omitted** for supervisors (null count, empty list, `turnover_view_authorized=false`); it is available only to owner/property manager with exact property grant. Residents, technicians, leasing and unrelated properties fail closed.

All collections are capped to 100 metadata-only rows, with independent total counts to prevent a truncated view from looking like a complete workload. There are no resident names, lease content, billing details, inspection proof bytes, contact information or open Vault links. The `as_of` date is computed by Grounds; caller-provided dates and role flags are rejected at the web boundary.

`GET /grounds/api/physical-desk?property_ref=...` enters the same authenticated, no-store WSGI boundary as the other private Grounds API. The actual browser shows read-only due plans, pending inspections, owner/manager-only turnovers and current counters. Any failed current-source fetch displays Unavailable rather than clearing safety/inspection obligations. A stale response from another selected property cannot replace the current workspace.

Provider dispatch, completed external inspection sign-off, legal entry/notice, Vault retrieval and capital approval stay explicitly false. Soulaana can explain separately grounded states but cannot perform any of those actions.

## Verification and external dependencies

Unit, HTTP and real disposable PostgreSQL integration tests cover permitted manager/owner and supervisor privacy, resident/cross-property denial, due plans, current counts and no fake provider truth. Both exact-source and PostgreSQL CI must pass before merging to draft parent Grounds PR #51. Real credentials, premises and private tenant data are not included.

Actual live work still requires independently certified Tower grants/revocation; approved private Postgres with restore drill; real sealed Vault originals/proof checks; real on-call and recipient-delivery receipts; applicable housing/notice/entry/inspection review; Teller-mediated finance; and owner acceptance. No paid Render resource, hosted route, production migration, inspection completion or real user account is authorized by this source package.
