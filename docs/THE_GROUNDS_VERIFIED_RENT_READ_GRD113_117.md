# Grounds GRD113–117 — current-lease Teller read surface (SOURCE ONLY)

**Branch:** `grounds-verified-rent-read-grd113-117` (child of the draft Grounds PR #51). This increment joins existing `grounds/teller.py::resident_rent_projection` to authenticated `grounds/web.py` and the actual resident browser. It creates **no rent collection, account, production provider, public route, hosted service, real tenant data or paid Render resource**.

## Exact flow

1. `GET /grounds/api/rent?property_ref=...&unit_ref=...` enters the same WSGI Tower receiver required by all protected UI/API requests. It is resident-only; parameters do not grant scope.
2. `GroundsOperations.resident_home` rechecks the current Tower unit grant **and** current Grounds lease/household membership. An old lease, another person's lease, ended grant or other property cannot reach a Teller source.
3. Optional **server-owned** `teller_document_source(actor,home)` retrieves the original signed Teller read document, then an independently configured `teller_verifier(document)` verifies source authenticity, recipient, replay and signature. Both must be configured, or neither. They must never be furnished via request headers, query or browser JSON. Test lambdas are fictional and are not acceptable production implementations.
4. `resident_rent_projection` independently binds `source=teller`, `audience=grounds`, exact subject/property/unit/current lease, observed/expiry (maximum five-minute window), USD, nonnegative integer cents and invoice state. A mismatch returns a non-leaking denial.
5. With no actual adapter, the read returns `status=not_connected`, `amount_due_cents=null`, `checkout_url=null` and `checkout_execution_enabled=false`. The UI distinguishes an unavailable source from **$0 due**, and a stale/failed read never becomes a paid claim. A real verified read displays only the amount, due date and status as a **snapshot**, without a payment action. Current route always has `no-store`.
6. Generation-bound browser refreshes prevent a late rent response from overwriting a newly selected unit/property context.

## Boundary: NOT rent checkout

Even a valid Teller handoff reference is only an opaque read projection here. Grounds does not accept cards, ACH, deposits, direct OB balances, unsigned invoice claims, untrusted links or a browser-supplied verification callback. No checkout button, redirect, receipt write or reconciliation is available. It would require a separate current authenticated Tower→Teller launch/return contract, independently proven idempotency, partial/failed/returned/reversed payments, exact current lease, actual provider receipts, and owner/privacy acceptance.

## Integration requested of Tower / Teller

- Certified server-owned, per-request Tower scope including current resident/household/lease revocation.
- Independently certified original Teller read fetcher and signature/replay/recipient verifier for the exact current lease. The future production entrypoint **does not inject these yet**; it remains disconnected by default rather than accepting a fixture or env-supplied self-certification.
- Explicit owner-approved rent checkout contract and reconciliation in Teller and Tower, not through Grounds direct debit or the OB.
- Source CI / real PostgreSQL CI and real hosted privacy/recovery validation on exact final heads. Both source checks prove only code/fixture behavior.

Run the isolated synthetic test: `python -m unittest grounds.test_grounds_rent_web -v`. It verifies exact-current-lease authorization, scope isolation, ended lease denial before source access, no fake zero balance, no checkout, signed-document mismatch/freshness denial and paired adapter configuration.

**Release status:** Draft/source-only, no actual user rent amount or payment accepted. Separate certified service and real owner acceptance remain HOLD.
