# SIMPLEE SOVEREIGN CLOUD — SC017 LEGACY AUTHORITY SHAPE REJECTION

Date: September 28, 2026. Source baseline: merged `vault-dev` commit `c55c25caca151bdb72a28a197e49f546fc040901` after SC016. Production remains **NO_GO**.

## Why this exists

The repository correctly contains several older or separate source shapes whose names can look authoritative if taken out of context:

- Tower's `archive_vault_handoff.py` produces a redacted **queue item** and explicitly marks its Archive Vault evidence stub not ready.
- Vault's `TowerStorageDecision` contains a legacy/internal `verified_by_tower` boolean and documents that it is a typed internal contract, not an authentication mechanism.

None of these objects can replace SC004/SC004B's signed Ed25519 one-use Tower grant, independently authenticated Vault service peer, current Tower policy check, durable nonce replay ledger or independently resolved canonical Vault scope.

## Regression wall

SC017 imports the **actual merged repository modules** and proves that their objects are rejected by Cloud before any provider GET/PUT:

1. The real Tower Archive Vault handoff record remains queued and its sensitive token field is redacted.
2. A Tower handoff dictionary, a real `TowerStorageDecision(verified_by_tower=True)`, and a plain dictionary containing `verified_by_tower: true` are all rejected as the Cloud `SignedTowerGrant` type.
3. Manually flipping the queue stub's `ready_for_archive_vault` or status fields cannot turn it into authorization.
4. The legacy Vault decision may still validate its own internal source contract, which makes the distinction explicit: local typed validation is not cryptographic Cloud authority.
5. Only the existing source-test signed-grant shape can cross the Cloud authority type/signature/current-policy/replay checks—and even that source harness truthfully reports no real Tower issuer, no independently certified private peer transport and no production authorization.

The tests use a backend that raises if touched, proving the rejection happens before physical storage access.

## Ownership boundary

This does **not** change Tower or Vault owning code. It is a Cloud-side compatibility wall against an unsafe shortcut, scoped only to authority-shaped modules already merged on this `vault-dev` baseline. The real implementation still belongs to Tower/Vault handoff issue #99: real signer and rotation/revocation roots, actual private Vault service identity, current approval/step-up/policy checks, canonical record/scan/retention/receipt authority and end-to-end private transport.

No provider, secret, paid resource, hosted route or production data is introduced. SC015's consolidated Vault/Cloud workflow should cover this test without adding another duplicate CI workflow.
