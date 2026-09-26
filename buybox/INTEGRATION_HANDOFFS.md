# BuyBox — cross-system integration handoffs (2026-09-26)

**Source of truth:** BuyBox draft PR #26, branch `buybox-universal-acquisition-foundation-bbx001`, in `LeeTheLilBee/SimpleeMrkTrade`. This is an implementation coordination packet, not permission to merge or deploy. Read actual code before changing any interface. No fabricated production endpoints or sample balances are authorized.

**Locked owner correction — Tower front door:** BuyBox is a Tower-launched and Tower-governed Simplee application, like the other ecosystem rooms. Tower owns its entry, identity/session, permissions, step-up, protected action routing, and allowed navigation. No separate permanent BuyBox login or independently exposed owner entrance. Runtime isolation and whether its backend is deployed within Tower's service or as a separately managed service are implementation decisions to resolve with Tower, not a unilateral separate-service requirement. The present local Flask sign-in is temporary development access only.

**Whole-product scope:** Universal acquisition/discovery, dossiers, evidence, underwriting, comparison, scenario/risk, negotiation, closing, handoff and outcomes, with ATM, multifamily, commercial, laundromat, land/farm, operating business and equipment verticals. ATM is the first detailed vertical, not the whole product. Owner UI starts with zero synthetic listings. Soulaana is integrated contextually but the live AI service is not yet connected. Local BuyBox readiness is UNKNOWN until a genuinely authenticated Teller integration exists. Protected transitions remain blocked without Tower.

**Shared integration packet proposed contract:**
- `request_id`, `idempotency_key`, `opportunity_id`, `opportunity_revision`, `input_snapshot_digest`, `vertical_id`, `requester_identity_ref`, `requester_entity_ref`, `requested_action`, `purpose`, `issued_at`, `valid_until`, `data_classification`, `correlation_id`.
- Responses include `request_id`, `issuer_system`, `issuer_authority_reference`, `source_revision/as_of`, `valid_until`, `status`, `reason_codes`, `receipt_reference`, and only the permitted, minimally necessary fields.
- Contracts must be versioned, authenticated, permission-scoped, replay-resistant, and bound to exact decision inputs; consumer handles timeouts, retries, duplicates, stale/degraded responses and revocation. Returning a receipt-shaped dictionary is not authentication. Unknown is not Ready. No silent fallback to direct OB/Vault/owned-property truth.
- Historical decision snapshots retain the exact external response they relied upon. Material change invalidates dependent readiness/authorizations rather than rewriting old snapshots.

## Handoff for THE TOWER chat

BuyBox needs Tower as its sole identity, protected-permission, step-up, routing and Vault-mediation boundary. Please inspect current Tower implementation and identify the existing canonical auth/session/launch and request-packet conventions rather than introducing parallel auth. Define a first-class Tower → BuyBox owner entry/launch route, session propagation and safe return-to-Tower navigation (subject to actual current Tower conventions); role/resource/action policies for opportunity, evidence/document intake and download, owner reviews, sensitive scenarios, decision snapshots, exceptions, LOI, closing and acquired/handoff; a verified issuer-bound approval/receipt response tied to opportunity revision/digest and expiry; and Tower-mediated document/proof request to Vault. Default deny, permission-filtered responses, immutable receipt, cancellation/revocation and re-authorization after material changes. Do not let the BuyBox local Flask password become a permanent independent identity authority; its local sign-in is an interim private workspace only. Do not modify OB/Teller or deploy live routes on assumptions. Return exact route/contract/version names, code locations, missing work, tests and branch/commit.

### Tower response received and integrated (TWR201 and TWR202–206, 2026-09-26)

Tower PR #39 has merged BuyBox into the canonical registry as **registered_future_room**, explicitly `launchable=False`; it is not yet a live doorway. Tower [PR #41](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/41), merge `db57752b9fd7402265dceb7a35cf93ea16015218`, supplied `tower.buybox.action.v1` and `tower.buybox.owner.preflight.v1`. The action contract has exact fields, all seven BuyBox vertical IDs, action/purpose pairs, source revision and SHA-256 digest, max 300-second TTL, and immutable untrusted classification. Its Tower-derived owner preflight stays unconditionally **BLOCKED** until the true hosted receiver, durable storage, Tower session/step-up, entitlement and publication health are independently certified. A source merge does not mean BuyBox can launch.

BuyBox BBX016 implements `buybox/tower_action_draft.py`: from the **current saved opportunity** it checks the exact persisted revision JSON and historical revision digest, then produces a `tower.buybox.action.v1` source-bound `UNTRUSTED_DRAFT`. It never accepts a browser-provided snapshot digest, never calls Tower or Teller, never treats claimed actor/entity/classification as authority, and cannot authorize an action. Rechecking after a change makes older drafts stale. GitHub CI checks every listed action across seven verticals against the exact merged Tower canonical module, alongside the PR #35 Vault schema tests.

The separately developed [BuyBox PR #45](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/45), BBX011–015, has also now merged into the BuyBox base branch. Its `tower.buybox.owner.handoff.v1` HMAC verifier and atomic SQLite single-use receipt ledger are **protocol primitives only**, with no HTTP route or authenticated session yet. Its hosted configuration inspection remains explicitly not provider/disk/backup proof. Do not duplicate the receiver, issue a Tower token on the BuyBox side, or expose the local Flask password publicly. The next joint Tower/BuyBox work is **issue #42**: real owner-issued handoff + protected pre-render receiver, secure persistent hosting/backup, actual session and step-up, consented entitlement, issuer-bound protected actions and a real owner walkthrough.

### BBX017–021 implementation update — protected owner receiver source

The BuyBox branch now contains `buybox/hosted_auth.py`,
`buybox/tower_session_store.py`, and a Tower-mode
`POST /tower/owner-exchange` route in `buybox/app.py`. This is the BuyBox
half of the signed `tower.buybox.owner.handoff.v1` pre-render exchange:
POST-body token only, exact HTTPS BuyBox Origin/Host, short expiry, canonical
signed claims and atomic replay denial; a separate live Tower adapter must
recheck authenticated owner session, entity, entitlement, step-up and
revocation at the exchange and every protected request. The client-visible
signed Flask cookie contains only an opaque handle, not raw Tower identity
references, and logout revokes its private SQLite binding. In Tower auth mode
the development password entrance is disabled and a fixed Return to Tower
link is displayed.

**This is source work only.** The repository has no live Tower issuer, no
trusted session-introspection implementation, no Render/provider storage
attestor and no approved paid durable disk/database/backups. `create_app`
rejects hosted mode without separately injected, actually certified
adapters and inspected private mounted storage; a passing mocked test is
not production authorization. For the Tower chat: pair this exact wire
contract with real Tower owner/session/step-up/entitlement truth, independent
provider/restore evidence, publication health, exact-origin issuer,
revocation and an owner walkthrough. Do not open `/tower/launch/buybox`
until the combined live crossing is verified. See
`docs/BUYBOX_TOWER_OWNER_CROSSING_BBX017_021.md` and Tower issue #42.

## Handoff for THE TELLER chat

BuyBox MUST ask Teller (never OB directly) for money-side deployment/readiness and management/expansion capacity. Define an authenticated request for an opportunity + version/digest + chosen business/mission account set (for ATM: Acquisition/Operations-Vault Set 1 or Set 2, reusable) + proposed price/capital stack + closing/fees + physical vault and replenishment liquidity + protected operating/replacement reserves + funding date + expected manager/staff/vendor load. Teller owns policy translation and financial-admin readiness; any underlying OB/Tower truth is mediated by Teller according to existing boundaries. Response must independently report money and management `READY/PARTIAL/BLOCKED/UNKNOWN`, aggregate readiness, spendable/deployable amount only as permitted, protected/committed amounts, shortfall, staffing gap, source/as-of/revision, expiry and issuer receipt, with explicit reasons. No new fabricated protected floors or guaranteed capital; pre-closing refresh required. Document how a changed proposal or source-state change invalidates earlier readiness and how to test fail-closed unavailable/expired answers. Teller must not gain direct OB execution authority via BuyBox. Return exact DTO/interface, tests and current blockers.

## Handoff for THE GROUNDS chat

BuyBox discovers and evaluates acquisitions; Grounds remains the source of owned-property operational truth. Please define a permission-filtered, read-only portfolio-context snapshot by relevant market/property/management capacity (existing holdings, exposure, operating obligations, major CapEx, useful comparables as allowed), with `grounds_reference`, version/as-of and a stable `Open in Grounds` link; no duplicated lease/unit/maintenance management inside BuyBox. For a property acquired through BuyBox, design a two-phase handoff: Tower-authorized close receipt + frozen acquisition decision/asset list/leases/contracts/rent roll/CapEx/insurance/obligations/30-60-90 tasks -> Grounds validates and acknowledges acceptance with its own property ID. Later Grounds may supply permissioned aggregated actual operating performance to BuyBox for predicted-versus-actual comparison; do not rewrite acquisition-time assumptions. Define owner/manager access, idempotent acceptance, duplicate handoff/failed handoff recovery and contract version.

## Handoff for VAULT / Tower–Vault chat

BuyBox's current encrypted local original-document intake is NOT the Archive Vault. Keep the doctrine: BuyBox structured proof request -> Tower checks identity, entity, role, purpose, approval, redaction and permitted output -> Tower requests or stores allowed proof via Vault -> Vault responds ONLY to Tower -> Tower returns an allowed receipt/status/reference to BuyBox. Define source artifact digest, evidence ID, opportunity/revision, retention and classification, proof/decision snapshot ID, encrypted transfer, malware screening, deduplication and immutable archival receipt. Do not enable direct BuyBox-to-Vault calls, raw Vault file paths or unredacted links. Preserve original bytes and corrective revisions; never silently overwrite. Return applicable Tower packet name, Vault API contract, evidence retention/access policy, tests and missing work.

### Newly received Vault-team handoff (reviewed 2026-09-26)

Found [PR #35](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/35), `buybox-vault-proof-evidence-contract-v1` at `1b9a3e191cf8f8b61adb59b790033983f767f42f`, based on `vault-dev` (NOT the BuyBox branch). The Vault team provided `docs/BUYBOX_TOWER_VAULT_PROOF_EVIDENCE_HANDOFF.md` plus `vault/buybox_evidence_handoff_contract.py`, Tower fail-closed preparation, and a local pending-version lineage registry. This is **metadata contract and preparation only**, with NO verified live Tower identity, original transfer, malware scan, canonical archive, receipt, retention/legal hold or protected download.

BuyBox's BBX010 implementation at `buybox/tower_evidence.py` prepares a source-bound metadata-only `buybox.vault.evidence.v1` packet after freezing a local evidence snapshot, without importing/calling Vault or exposing a web endpoint. `original_document_ref` is an opaque descriptor ID, NOT BuyBox's encrypted `storage_reference`; file bytes and raw paths are never part of the packet. The builder requires an actual uploaded artifact linked to the specific evidence ID and a matching frozen snapshot. The returned draft does NOT assert Tower authentication or archival. Even receipt-looking JSON remains untrusted and cannot become ARCHIVED in BuyBox until a real authenticated, source/digest/version-bound Tower connection verifies it. BuyBox CI checks packet compatibility against the exact canonical PR35 schema commit.

Items for coordinated future work: authenticated Tower-sourced principal/entity/policy profiles and step-up, canonical owner-signed decision snapshot, actual bounded malware-scanned transfer, Vault's verified version/receipt, durable pending/outbox/status reconciliation, correction lineage across systems, restricted downloads, and all E2E negative tests. PR35 currently excludes `text/csv`, whereas BuyBox accepts CSV for temporary local intake; this must remain a visible archival limitation until a formally approved normalized transfer/profile exists. Do not auto-convert an unsupported original and claim it was archived; preserve the original bytes.

Do NOT merge the `vault-dev` branch into BuyBox or promote either draft PR as live solely to obtain this schema. GP821–GP830 remains independent.

## Handoff for SOULAANA chat

Soulaana belongs **inside** BuyBox throughout Browse, Opportunity Dossier, Machine Portfolio, Compare, Scenario Lab/Red Team, Deal Room, Decision Desk, change brief and post-close review. The current branch implements a deterministic source-grounded `buybox/soulaana.py` context room, NOT live model inference. Design the actual permission-filtered service contract: inputs are the minimum allowed opportunity snapshot, source/claim/evidence IDs and locators, metric calculations/formula versions/periods, failed/passed rule IDs, approved scenario assumptions, Teller readiness summary (without forbidden balances), Grounds reference, Tower role scope, recent material events and owner tasks. Output must label FACT/documentary support vs SELLER CLAIM vs OWNER NOTE vs ASSUMPTION vs CALCULATED vs RULE/JUDGMENT, attach provenance, flag unknown/conflict/stale, and propose next actions. She may explain why state/score changed, evidence confidence and scenario dependencies; never silently set truth, change policy, waive hard stops, mutate budgets or approvals, sign documents, contact sellers, execute trades or make an acquisition decision. Provide service/room integration contract, source-bound hallucination tests, redaction rules, unavailable fallback and event invalidation triggers.

## Handoff for SIMPLEEONTHEGO / ATM operations chat

Upon an actually Tower-authorized ATM close, BuyBox must send an idempotent acquisition handoff rather than recreate ATM operations. Payload: complete serial-numbered acquired machine list; location and agreement rights; commissions; processor/connectivity/service relationships; actual vault/replenishment model; insurance/maintenance/seller-transition obligations; funding/debt obligations at appropriate permissions; verified trailing operating baseline; open risks, deadlines and owner-approved 30/60/90 transition plan. SimpleeOnTheGo validates and acknowledges receipt with its own route/machine IDs; ownership/title/lien/contract consent must be truly closed, not merely owner-marked. Subsequent operating actuals return to BuyBox as versioned period snapshots to compare with the frozen acquisition thesis, not to overwrite history. Reusable ATM capital accounts remain Teller-side readiness, not a new BuyBox ledger.

## Handoff for OB chat (boundary notification, not an integration request)

BuyBox does NOT access or trade through OB. OB retains its capital truth and Manual Live/Survey/Paper controls within existing authority; Teller mediates money-side readiness for BuyBox according to already-approved system boundaries. BuyBox price/scenario/evidence changes should request refreshed Teller snapshots, not query OB mission accounts or infer spendable capital. No OB trading/mode or capital-policy changes are authorized by this handoff.

## Coordination / return format for each chat

Reply with (1) verified current branch/repo/commit and what already exists, (2) exact versioned request and response names/fields, (3) permission/authority and expiry rules, (4) data ownership and prohibited direct calls, (5) failure/idempotency tests, (6) code packs needed in that system, (7) any owner decision or credential provision needed. Do not invent a currently working integration and do not merge/deploy without explicit coordination.

## Hosting selection note

**Confirmed by owner on 2026-09-26:** BuyBox's designated Render workspace is `Simplee World`, ID `tea-dag3rfu1egvs73a6s72g` (ending `a6s72g`). Existing `simplee-tower-ob` service must not be changed without verified Tower coordination. BuyBox MUST launch through Tower and use Tower identity and protected-action governance; it must not be exposed as a standalone application. Whether backend runtime is integrated into Tower's existing service or separately deployed behind Tower should be decided by the Tower architecture and hosting review. Durable protected storage remains required. Read-only inspection found no Postgres in this workspace; **do not create a public or ephemeral-storage deployment solely from workspace confirmation**. Confirm storage and access plan before creation.
