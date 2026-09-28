# The Grounds — Resident Maintenance Completion GRD212–216

## Purpose

The maintenance loop previously let a technician mark work completed and a manager move it into confirmation, but the resident had no explicit source-backed way to say **yes, this looks resolved**. A resident could technically reopen a confirmation/closed record through the generic lifecycle, but that was not a clear completion experience and created no structured feedback record.

GRD212–216 adds a narrow, current-lease resident completion response.

## Resident outcomes

When and only when a work order is in `confirmation`, the current original requesting resident can submit one of two outcomes:

- `resolved` → Grounds records the resident response and closes the work order.
- `still_needs_attention` → Grounds records the resident response and reopens the work order for management review.

An optional plain-text note is limited to 800 characters. The response is written transactionally with the work-state revision, work event and local notification intent. Exact retries are idempotent; changed retries, stale revisions and responses outside the confirmation state fail closed.

The responder is revalidated against the current Tower scope, exact property/unit, original work creator and active lease. A roommate/other resident who did not create the request, an old lease member, staff member or cross-property user cannot submit the resident response.

## Truth boundaries

A `resolved` response means only that the resident told Grounds the repair looks resolved. It is **not**:

- a waiver, release or settlement of resident rights;
- an inspection or habitability certification;
- legal notice or proof of external delivery;
- permission for future physical entry;
- a rent, deposit, reimbursement or payment decision;
- proof that an outside vendor/provider completed contractual obligations.

A `still_needs_attention` response reopens the Grounds work record; it does not itself contact emergency services or prove staff/provider notification.

## UI and timeline

Residents see **Confirm or reopen this repair** only while their authorized request is in `confirmation`. They can choose “Yes · looks resolved” or “No · still needs attention” and optionally record a note.

Authorized maintenance timelines include resident completion responses without exposing the resident subject identifier. Staff and resident views therefore share the outcome and note, while private identity remains governed by the existing current lease and Tower scope.

## Persistence and tests

`work_completion_events` is an append-only ledger in the fresh SQLite fixture and PostgreSQL baseline. PostgreSQL preflight and local developer integrity require the table and index, preventing an older schema from silently claiming compatibility.

The domain tests cover resolved close, still-needs-attention reopen, manager return to review, exact retry, changed retry, stale state, wrong resident/staff denial and note bounds. WSGI tests cover CSRF/idempotency, current-requester scope and timeline projection.

This source addition creates no public service, provider delivery, live resident account, payment, legal action, emergency call, or production schema migration. Parent Grounds remains draft pending the independent external release gates already documented.
