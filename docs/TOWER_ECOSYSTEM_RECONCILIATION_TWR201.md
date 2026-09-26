# Tower ecosystem reconciliation — TWR201 / 2026-09-26

**Starting point:** Tower's dedicated canonical branch `tower-hosted-runtime-identity-twr081-085` at `f287a3cb5ce2e1f3ba292b8483abddc1b374640f`. This is a source-only inventory and a fail-closed registry addition, NOT authorization to merge/deploy or activate a new product.

## Verified source branches

| System | Verified source checkpoint | State / relevance to Tower |
| --- | --- | --- |
| Tower | `f287a3cb5ce2e1f3ba292b8483abddc1b374640f` | Dedicated Render service `simplee-tower-ob`; owner access and Teller v2 source merged and previously deployed. Existing separate `main` service must not be changed by this pack. |
| BuyBox | `buybox-universal-acquisition-foundation-bbx001` at `f227a051429799c5b174b04129b58e4b0ab1e247`, PR #26 | Draft, seven-category saved-record owner workspace. Its local Flask password is development-only; Tower must own production login, permission, launch and protected routing. Not automatically safe for public hosting. |
| BuyBox ↔ Tower ↔ Vault | `buybox-vault-proof-evidence-contract-v1` at `1b9a3e191cf8f8b61adb59b790033983f767f42f`, PR #35 | Metadata-only `buybox.vault.evidence.v1`; no authenticated live archive or proof. Tower preparation accepts supplied context booleans; a future route MUST derive all authorization from actual Tower session/policy, never trust submitted `identity_verified` flags. |
| Vault real operations | `vault-real-operations-managed-storage-v1` at `4dd2cdca37326abeaf09a01cbfc6deadd0200a74`, PR #38 | Encryption and managed ciphertext adapters are source preparations; no approved provider, KMS, scanning, real Tower middleware or final receipt transport. |
| Clouds | `clouds-rebuild-dev` at `9606ccef44045634eaf977f1df641751aefd866b` | Dedicated owner-wide projection/decision/navigation work; preserve Tower authorization and permission-filtered deep-link/return. |
| Grounds | `grounds-clouds-source-wave2` at `4034f967d714b9db44016ea8dfba380ddd95b0a0` | Clouds status publisher bootstrap, not a proved production acquisition handoff or full Grounds runtime. |
| ATM operations | `atm-operations-clouds-source-wave2` at `9f5aa9f220b4cd72bc54ff200a46dcacdf985fac` | Clouds publisher bootstrap, not authorization for route/machine ownership or funding. |
| Teller | Separate `LeeTheLilBee/The-Teller`, sealed receiver `fd430134295167c6ee10e8c2d27a59592fa5d353` | Tower → Teller owner v2 source contract implemented; live persistence acceptance remains a separate gate. |

## TWR201 scope

Adds **BuyBox** to the canonical `tower.app_registry` as `registered_future_room`, with only `/tower/app-registry` as its descriptive listing. It is not a `/tower/launch/buybox` route, and no BuyBox receiver, production login, security claim, publication/availability truth, entitlement or service endpoint is manufactured. Tower's app-truth projection must continue to show `launchable=False`. Other system code is unchanged.

Do **not** merge the BuyBox/OB, Vault or Clouds development branches into the hosted Tower branch to obtain a single contract. No second login or direct BuyBox–Vault / BuyBox–OB / BuyBox–Grounds operations path.

## Required Tower integration work (not implemented by TWR201)

1. **Owner entry and receiver:** define `/tower/launch/buybox` only after an actual authenticated BuyBox receiver exists. Existing Tower owner session + step-up + explicit BuyBox entitlement + verified publication/health + exact allowed destination + short-lived one-time scoped handoff; safe return to Tower. No permanent separate BuyBox password.
2. **Versioned protected actions:** permissions for read/update opportunity, evidence intake/download, scenarios, snapshots, exceptions, LOI, closing and acquired/handoff. Bind decision to opportunity ID, revision, digest, entity, exact action/purpose, TTL, idempotency and source/receipt; revocation, recheck on material change and auditable denies.
3. **Teller readiness corridor:** BuyBox → Tower-permitted Teller request, not OB balance access. Teller alone supplies financial + management-capacity readiness; retain Set 1/Set 2 ATM sleeves and protected floors. Unknown/stale/changed terms are NOT READY; signed issuer-bound fresh responses only.
4. **Vault corridor:** BuyBox drafts `buybox.vault.evidence.v1` metadata → Tower derives identity/policy/step-up/approval from its own authoritative state → controlled encrypted original transfer + malware scan → Vault independent authorization and canonical receipt → Tower returns only safe status/reference. Current PR #35 boolean context is preparation-only, never a security boundary. Preserve correction lineage, retention, protected downloads and audit. CSV currently accepted in BuyBox local intake but excluded from the canonical Vault mime allowlist; do not claim it archived.
5. **Grounds and SimpleeOnTheGo:** two-phase owner-authorized, idempotent close-to-operations handoffs. Grounds accepts actual owned-property operational state with its own ID; ATM operations accepts serial-numbered verified machine inventory/contracts. Neither gets funding or title authority from BuyBox stage alone.
6. **Clouds/Soulaana:** Clouds receives permitted status/attention projections and uses Tower-protected “Open in” deep links; Soulaana is contextual source-referenced explanation, never a permissions/approval engine.
7. **Hosted gates:** dedicated Tower branch and new BuyBox backend topology, durable encrypted data/object storage, exact-origin receiver, real Teller/Vault secret/provider binding, tests, runtime revision, authenticated walkthrough and rollback plan. Keep other Render service and `main` untouched.

## Non-authorizations

No broker/Manual Live/Live Auto, capital transfer, ATM funding, payroll/payment, title/closing, raw Vault access, public BuyBox hosting, fake readiness, default external API provider, or release from source tests. App registration is not availability or authorization.
