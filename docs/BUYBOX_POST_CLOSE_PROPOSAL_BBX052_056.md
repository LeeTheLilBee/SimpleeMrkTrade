# BBX052–056 — source-only close-to-operations proposal

BuyBox's saved acquisition work cannot automatically create owned properties,
ATM route ownership or operational records. After the separate owner-approved
verified closing and title/contracts, Tower must mediate a two-phase
idempotent handoff that the correct recipient independently accepts.

This pack reads BuyBox's actual persisted revision and locally verified
snapshot digest, derives Grounds only for multifamily or SimpleeOnTheGo only
for ATM, and reports a local acquisition-stage/included-machine count. No
private documents or serial numbers are transmitted. Even a locally stored
ACQUIRED stage remains source data, not verified Tower closing or legal title.
The return is always SOURCE_ONLY_UNSENT; independent closing/title/receiver
receipts are absent, all operational and funding permissions false, and no
external request is sent.

A future protected implementation needs:
1. Current Tower owner identity, entity, step-up, action and revocation proof.
2. Independently verified close/title/asset contract receipt bound to exact
   opportunity/revision/digest and appropriate entity; lien and included
   machine serial/ownership evidence for ATM routes.
3. Two-phase scoped request with a stable issuer-bound idempotency key, exact
   recipient, short TTL, retries/reconciliation and audit denial trail.
4. Grounds or SimpleeOnTheGo's independent current receiver acceptance with
   its own stable property/route IDs and operations-specific truth. The
   current ATM Operations branch is only a Clouds publisher bootstrap; do
   not fake an ownership receiver. Grounds remains owner/resident source
   development, not activated for real tenant traffic.
5. Teller separately checks financial and management readiness and protected
   ATM sleeve floors; neither BuyBox stage nor a close draft transfers funds.

No Tower/Grounds/ATM/OB/Teller/Vault/Clouds implementation or Render change.
The owner's source-only/no paid-resources instruction remains authoritative.
