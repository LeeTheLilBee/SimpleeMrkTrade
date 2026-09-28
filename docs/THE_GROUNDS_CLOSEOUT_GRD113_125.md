# The Grounds — close-out integration handoff (GRD113–125)

**Scope:** complete the Grounds-owned side of the remaining integration seams without creating paid infrastructure, real tenant accounts, provider credentials, public routes, payments, or false external receipts.

Grounds remains behind Tower and PR #51 remains the parent development line. This packet does not certify a tenant launch. It makes the receiving and verification boundaries concrete so the remaining Tower/Teller/Vault/provider work can plug into tested Grounds contracts instead of requiring another product rewrite.

## GRD113–117 — verified BuyBox/Tower post-close → Grounds acceptance

`grounds/acquisition_handoff.py` is the receiving half of the two-phase multifamily handoff.

Grounds now creates an owned property from this path only when a **server-owned verifier** authenticates an exact, fresh `tower.grounds.multifamily.post_close.v1` message with:

- source `tower`, audience `grounds`, kind `multifamily_post_close`;
- exact owner and newly granted property scope;
- BuyBox opportunity ID/revision, input snapshot digest and proposal fingerprint;
- `vertical_id=multifamily`, proposed recipient `grounds`;
- independently completed closing, verified ownership, and recorded encumbrance review;
- unique Tower close, title-proof and encumbrance-review references;
- a maximum five-minute handoff lifetime.

A BuyBox local `ACQUIRED` label or its `SOURCE_ONLY_UNSENT` post-close proposal cannot satisfy this receiver.

Acceptance is transactional and append-only. The property and `property_acquisition_receipts` lineage record are committed together. An exact handoff retry returns the original acceptance; a changed replay, reused external proof, or second conflicting close fails. No money moves and no Teller/OB authority is created.

## GRD118–120 — verified Teller rent reaches the real resident UI

Grounds already had `resident_rent_projection()`, which verifies source/audience, exact resident/property/unit/lease, freshness, USD amount, invoice state and due date.

The real WSGI app now has an authenticated `GET /grounds/api/rent` path. It remains disconnected unless **both** server-owned Teller source and verifier adapters are injected. When connected, the browser renders only the verified amount/status/due date for the resident's current exact lease.

No amount is inferred from Grounds, OB, a browser field or an old lease. Checkout execution remains disabled; the UI explicitly says payment execution belongs to the certified Tower/Teller handoff.

## GRD121–123 — real delivery receipt ledger without fake delivery claims

`grounds/delivery.py` adds append-only receipt intake for the existing transactional `event_outbox`.

A trusted receipt verifier must authenticate exact `tower.grounds.delivery.receipt.v1` messages from `tower_delivery_gateway`. The receipt is bound to the existing outbox event, property, event kind, resource and source revision before it can be persisted.

Two receipt classes are supported:

- `notification_delivery`: accepted / delivered / failed.
- `urgent_human_escalation`: queued / human_acknowledged / failed, and only for `urgent_intake_requires_human_review` events.

Exact retry is idempotent; changed replay and provider-receipt reuse fail closed. Safety views can now distinguish verified provider receipts and verified on-call human acknowledgment from mere local intent.

These records **do not** prove legal service, physical entry consent, or emergency-services dispatch.

## GRD124 — truth and integrity reconciliation

The source/release truth now explicitly reports that these Grounds-owned seams exist while keeping all live connections false.

Local fixture integrity and private PostgreSQL preflight now require the acquisition and delivery receipt ledgers. The fresh PostgreSQL baseline contains both tables and their indexes. There is still no automatic production migration.

## What still belongs outside Grounds

The remaining items cannot be completed honestly by adding another local fixture or changing a boolean:

1. **Tower:** implement/certify `tower.grounds_runtime_receiver` plus current resident/staff/owner grants, lease/member revocation, staff directory/resolver, session/logout/replay/health and the protected Grounds route.
2. **Private hosting:** owner-approved PostgreSQL/host, TLS/network/secret controls, reviewed schema application, encrypted backup and a successful restore drill.
3. **Teller:** actual invoice source/verifier adapter, Tower-mediated checkout, partial/failed/returned/refund paths and authoritative receipt/reconciliation.
4. **Vault:** authenticated private upload/intake/scanning, lease/work proof, retention/revocation/recovery and protected retrieval.
5. **Delivery/on-call:** actual delivery gateway/provider, recipient resolution, retry/dead-letter, current after-hours roster and on-call escalation. Grounds is ready to persist verified receipts once these exist.
6. **Housing/privacy/accessibility:** jurisdiction-specific legal review for entry/notices/leases, privacy, fair access and accessibility.
7. **Owner acceptance:** hosted revision, recovery/security contacts and actual resident/staff/owner walkthrough before tenant release.

## Release discipline

Green source/PostgreSQL CI means the Grounds code behaves as tested. It does not itself prove real Tower identity, provider availability, tenant privacy controls, money settlement, legal notice, recovery, or owner launch acceptance.

No paid Render resource, public Grounds service, real resident record, provider credential, payment, external notification, emergency dispatch, Vault upload, OB/broker action or live authorization is created by GRD113–125.
