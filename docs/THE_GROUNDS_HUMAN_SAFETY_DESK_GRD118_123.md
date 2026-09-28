# Grounds GRD118–123 — authenticated human safety desk (source only)

This increment exposes existing Grounds human-triage truth inside the **actual**, non-demo authenticated staff application. It does not create a messenger, telephone system, emergency response, dispatcher, provider connection, legal entry determination, live Tower identity or a new database migration.

## Source-owned workflow

- A manager, maintenance supervisor or owner with a **current Tower property grant** can use `GET /grounds/api/safety-desk?property_ref=...`. Residents, technicians, leasing, regional managers and staff with another property grant cannot access the desk. No staff/role flags arrive in the browser request.
- `GroundsSafety.staff_safety_desk` returns exact-property counts of urgent submitted work with **no corresponding human emergency review**, ordered oldest-first, first 50 metadata-only records, and all pending local `event_outbox` intents. The queue includes only work/unit/category/timestamps; no resident identity, contact details, work descriptions, lease documents, payments or proof bytes.
- A real staff action uses the preexisting server-protected `POST /grounds/api/urgency/review`. A duplicate human review remains a conflict. The next GET removes the reviewed item while retaining local undelivered event intents; a review is **not** external notification, after-hours on-call acknowledgment, first-responder contact or actual dispatch.
- The responsive staff browser has a dedicated safety card. It never appears in the resident/technician view and does not claim an empty queue proves that emergency coverage exists. Browser refreshes are context-generation-bound so stale responses from a prior property cannot replace newly selected scope.
- The endpoint and UI return source truth only. Every response is `no-store` and production requests still require a certified Tower receiver. No scheduled polling/delivery or paid external infrastructure is introduced.

## Tests and external certification

`grounds/test_grounds_safety.py` and `grounds/test_grounds_web.py` include denied roles and cross-property grant negatives, query pollution, actual fiction-only WSGI triage action, no resident description/identity exposure, and persistent pending-intent versus human review separation. Run both source contract and disposable real PostgreSQL workflows at the exact current parent PR #51 head.

**External/owner-required:** certified Tower resident/staff sessions and revocation; actual reliable recipient resolution, after-hours human contacts and escalation policy, provider acknowledgment/receipts, retry/dead-letter and local operational incident procedures; legal housing/entry/notice review and owner acceptance. A green code test is neither emergency coverage nor permission to expose Grounds to actual residents. Do not add a fake provider or flip the existing outbox `pending` state to `delivered`.

**No paid Render resources, resident data, public route, notifications, dispatch or emergency calls are created.** 
