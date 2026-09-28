# SIMPLEE SOVEREIGN CLOUD — SC012 OWNER PILOT DECISION PACKET

Prepared September 27, 2026. Source baseline: merged `vault-dev` commit `34d61cbb78dc5d85c8b3bc8de5afde46abe20c5e` (SC001–SC011). This is an owner planning and handoff document, **NOT deployment authorization**.

## One-page state

| Area | Established in repository | Still required |
| --- | --- | --- |
| Cloud source | Separate `simplee_cloud/` product, default-disabled operations; SC002 primary and SC005B backup durable idempotent intents; SC007/007B payload-bound audit events; SC004/004B signed-grant source shape | Independently authenticated actual live Tower issuer, Vault peer/registry/receipt receiver, protected replay store and current policy |
| Vault compatibility | Actual merged Vault AES-GCM VLT1, archival workflow journal and canonical registry tested in SC006/SC008; Cloud ACK does not set `ARCHIVED` | Real scan/original authentication, protected Vault canonical receipt transaction, retention/legal hold and independently verified read/restore decisions |
| Physical provider | Explicit source provider port and disclosure/evidence fields in SC003; no provider selected | Owner-approved operator and actual physical-server owner, jurisdiction/subprocessors, private policy/conditional create, versioning/Object Lock and real retention evidence |
| Recovery | SC009 synthetic primary-directory-loss source rehearsal, separate SCB1 encryption; SC005/SC010/SC011 signed checkpoint source/read-back/lineage | Truly separate physical failure domain and key custody, independently authenticated offsite latest tip, real site-loss/Vault original recovery drill and measured owner-approved RPO/RTO |
| Owner desk | `python -m simplee_cloud.owner_preflight` returns 10 explicit review gates, never a GO | Actual external evidence and separately recorded owner release decision |

Evidence: [SC011 PR #137](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/137) merged after its exact-head Cloud source suite passed 157 tests and all 18 GitHub checks. Passing source CI is not equivalent to live security or disaster recovery certification.

## Ownership and routing doctrine

BuyBox/Teller → Tower → Archive Vault → Simplee Cloud. Tower alone owns real identity/authority/step-up/routing, Vault owns originals, scans, canonical versions, retention, legal hold, records and canonical archival/recovery receipts, and Cloud owns opaque encrypted infrastructure/integrity/backup/physical recovery substrate. The older executive `clouds/` is a separate product and cannot become a document storage backdoor. Soulaana can explain safe status but never confer an authorization. There is no direct BuyBox/Teller/browser public object-body access.

Owning this source code or the corporate product does **not** mean owning a cloud vendor's hardware, datacenter, network, domain, subprocessors or sovereign jurisdiction. Every proposed vendor must disclose the software operator, physical-server owner, location and dependencies. Black American ownership preference may guide sourcing if factually verified; no business or owner is preselected by this document.

## Safe current default

**Remain source-only and $0 new paid infrastructure.** No new Render paid services, provider enrollment, billing instrument, production secret, external object store, live personal document, hosted Cloud route or automatic Manual Live change is authorized. Tower/Vault can separately develop and review source contracts while the owner retains control of spending.

The existing [Tower/Vault handoff issue #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99) remains open. It needs (1) real Tower signer/key custody/rotation/current decision+approval+step-up+revocation, (2) independently verified private Vault service identity, (3) Vault canonical trusted scope/original hash/scan/version/retention and final receipt transaction, and (4) adversarial end-to-end proofs for replay, outage, wrong entity/purpose/object/digest, backup uncertainty and rollback. Neither synthetic source callbacks nor client JSON flags may satisfy these gates.

## Stage-gated owner decisions — only when ready to consider infrastructure

**Stage A — sourcing permission, no spending:** Identify candidates and compare private storage, actual hardware ownership, physical jurisdiction, subprocessors, conditional create and immutable retention capability, operator security response, separate backup keys and failure domain. Do not use ownership claims without verifiable evidence. A vendor must not be chosen solely because it says “sovereign” or offers an S3-compatible API.

**Stage B — proposed private hosted pilot:** Present the owner with a named real operator, location, actual physical-server owner, proposed backup operator/domain, any one-time and recurring charges and cancellation terms, credential/KMS custody plan, provider limits/retention and provider policy evidence, expected test/data scope and manual off switch. Default decision is HOLD until explicitly approved.

**Stage C — real operational acceptance:** Actual Tower/Vault authenticated source, private provider tests using non-sensitive test ciphertext only, witnessed/recorded fail-closed access/replay and object-lock assertions, independently signed offsite journal/custody, measured outage/restore and Vault original authentication, alert delivery, owner-approved RPO/RTO, and separate source-to-hosted revision evidence. Only then consider real evidence/production data in an independently approved release.

**Stage D — owner-owned office hardware and later hybrid:** A future design must address premises/permits, fire safety, drainage, security, ventilation/cooling, redundant connectivity, protected power and physical storage, backups in a different failure domain, provider exit/cutover and rollback. It is a separate funded build, not implied by Stage B. Do not collapse app ownership, physical hardware ownership or offsite disaster recovery into one claim.

## Owner review fields (intentionally unset)

| Decision field | Current recorded state |
| --- | --- |
| Continue source-only with no new spending | Default YES |
| Permit provider sourcing without signup/payment | No new vendor selected |
| Approve any paid pilot and exact monthly/one-time ceilings | NOT PROVIDED; no payment/provisioning |
| Proposed primary provider, actual server owner/location/subprocessors | UNSELECTED / unverified |
| Proposed separately operated backup domain and independent key custodian | UNSELECTED / unverified |
| Target RPO and RTO, including acceptable data loss/downtime | OWNER DECISION PENDING; do not invent SLA |
| Retention/legal hold policy and evidence classification | Must come from Vault/actual policy; not Cloud |
| Alerts/incident response owner and tested channel | External proof pending |
| Final hosted and real-document release approval | NO_GO; must be explicit and separately recorded |

**Only ask the owner for a vendor/budget/RPO/RTO/release choice when an actual candidate and verified cost/evidence packet is ready or the owner explicitly requests sourcing.** Do not equate a planning answer with permission to spend or provision. Until then continue appropriate source tests and Tower/Vault handoffs, leaving the default operational gate closed.

For detail, refer to [Cloud tracker #66](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/66), [Tower/Vault issue #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99), `docs/SIMPLEE_SOVEREIGN_CLOUD_SC006_MERGED_SOURCE_READINESS.md` and `simplee_cloud/readiness.py`.
