# OBSCAN → OBINTEL → Tower dependency audit — 2026-09-29

## Source chain verified at exact PR heads

| Source | Requires | Purpose / approval |
|---|---|---|
| OB #205 | existing `main` | typed, rights-gated symbol/event/equity/option intake; source only |
| OB #206 | #205 | multi-provider gateway, independent source/product rights, request budgets; source only |
| OB #207 | #206 | provider-review state machine and a disconnected owner Market Data Desk UI; source only |
| Tower #209 | current hosted Tower + **selectively staged** #205–207 files | exact `/ob/data-desk` GET/HEAD, owner session + fresh step-up + OB admission, honest disconnected catalog; draft, unmerged, undeployed |
| OB #210 | #207 | separately reviewed historical daily bars, exact-CIK SEC facts, source-bound research and optional nonpromoting V2/room overlays; source only |
| Tower #212 | **exact #209 head**, selectively staged #210 files | additive research modules and conditional room UI; draft, unmerged, undeployed |
| Tower #199 | independent hosted Tower base | exact guarded canonical feed status read; remains separate, not a provider or a dependency already satisfied by the catalog |

The old OB #207 navigation is **not** a safe whole-file replacement of current hosted Tower: it would resurrect legacy `/trade-center` and `/review-center` hrefs and lose reciprocal OB → Tower return. Tower #209 and #212 preserve current navigation and server-enabled Desk link. Tower #199 changes the same hosted entrypoint and exact guard as #209; integrate selectively if/when approved and re-run both route test suites. No unreviewed cross-branch merges.

## Security gaps found in the expanded audit and addressed on #212 only

1. Owner-display is not an AI-use right. Until the source rights model has separately reviewed AI permission for issuer-event text and provider-source metadata, the Soulaana projection strips event texts/links and source IDs; history without an explicit AI grant strips counts, dates and snapshot references as well as price observations.
2. Direct `history_context` / `fundamental_context` owner-facing numeric views independently require their owner-display grants, not merely internal research approval in their parent envelope.
3. The transient source-reference memory ledger rechecks source rights at its research capture time, rejects expired/history/SEC references and credential-like URL-query/control-character references. This is NOT a production retention/expiry/revocation solution: durable Tower/Vault policies and live receipt validation remain separate.

Tests cover denied AI-use, missing owner-display, rights expired at capture, unsafe reference rejection, source-only disabled live route and existing hosted room navigation. Parent OB #210 must reconcile/cherry-pick the fixes rather than later overwrite them from its stale ancestor.

## Activation still blocked on independent evidence
Real provider account/rights per equity vs options product, canonical source/exchange/event timestamp and actual session, business/internal display/AI/history-retention rights, persistent verified provider connection and audit log, issuer directory↔CIK provenance, transactional Vault expiry/revoke policy, and fresh Tower owner acceptance are NOT supplied by these source PRs. Static or synthetic source fixtures must never appear as current prices, fills, performance, capital or trading authorization. No paid resources or live broker activity.
