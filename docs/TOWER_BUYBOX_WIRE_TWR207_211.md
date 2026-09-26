# TWR207–211 — Tower BuyBox one-time handoff wire compatibility

**Source-only, not production issuance or hosted crossing.**

Tower parent: db57752b9fd7402265dceb7a35cf93ea16015218.
Exact independently verified BuyBox receiver: PR #45 commit
3e265c79f61c02ba149c53734757d8d9fd501608, merged into the
BuyBox PR #26 development branch.

## What was implemented

tower/buybox_handoff_wire.py privately serializes the exact versioned
Tower-issued JSON packet and HMAC defined in BuyBox's receiver:
tower.buybox.owner.handoff.v1; tbh1 canonical base64url payload,
HMAC-SHA256; issuer=tower; audience=buybox-owner; purpose=owner_entry;
one-time handoff ID and scoped Tower session/actor/entity/entitlement refs;
max 60-second TTL; fixed target=/ and return=/tower/access-home.

The product-facing issue_current_owner_buybox_handoff remains **unconditionally
blocked** because the real BuyBox hosted receiver, managed durable storage,
published health and current Tower owner entitlement are not certified. No
route is registered, environment secret is read, production token issued or
BuyBox UI served by this pack. Private wire serialization is only a protocol
building block; shape validation does not authorize a requester.

GitHub Actions independently checks out the exact BuyBox receiver source,
sends a synthetic token using Tower's serializer, has BuyBox validate it,
and proves SQLite single-use replay denial survives separate DB connections.
Wrong signer, target, TTL, audience, principal ID and expiry tests are
included; existing TWR201 and TWR202–206 default-deny contracts run too.

## Remaining release gates

1. Explicit owner approval of a paid, persistent single-instance BuyBox
   hosting/storage plan and an independently tested backup/restore of SQLite
   plus encrypted originals plus recoverable document key.
2. Secure BuyBox pre-render receiver implementation; local dev password
   disabled in hosted mode; real token fragment removed before rendering
   or navigation, exact-origin POST, CSRF-safe bootstrap, no URL/log/storage
   token persistence, bounded secure server session and re-entry/return.
3. Tower owner entry only from *verified current* owner session and step-up,
   explicit effective BuyBox entitlement, real verified publication/health,
   exact approved receiver and dedicated secret; one-time server-derived
   issuer. No client-supplied Tower-context booleans are enough.
4. Authenticated integration tests with actual hosted revision/receiver and
   replay denial; owner walkthrough before availability is displayed.
5. Protected action approvals/revocation and Teller financial+capacity
   readiness, Tower-mediated Vault and Grounds/ATM operations handoffs as
   separate gates. No direct BuyBox→OB, BuyBox→Vault or broker execution.

Do not merge the BuyBox product development branch wholesale into Tower.
Do not infer provider proof from a mount-like path or synthetic CI.
