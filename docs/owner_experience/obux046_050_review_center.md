# The Observatory — Canonical Review Center / OBUX046–050

Base:

`c864c3940268ce2face5df170ed2bf00efd7786b`

Branch:

`ob-review-center-obux046-050`

## OBUX046 — Canonical Review Center shell

Replaces the legacy static/list-heavy Review Center with:

- attention queue
- selected hero review
- outcome vs process
- trade replay
- Negative Dive
- cause analysis
- lesson extraction
- compact truth filters

The room no longer presents hardcoded sample performance as product truth.

## OBUX047 — Canonical review projection

Review Center reads existing OB lifecycle/review sources rather than creating a competing datastore.

Sources include, where available:

- Review Center receipt foundation
- position monitor / exit / close capture
- final trade review / performance receipt
- durable dry-run outcome finalizations
- materialized outcome receipts
- OB server review / receipt / close projections

Missing records remain missing.

No fake review row is synthesized.

## OBUX048 — Negative Dive / Overtime

Canonical review model supports:

- planned entry
- actual entry
- planned exit
- actual exit
- intended hold minutes
- actual hold minutes
- overtime minutes
- MAE
- MFE
- deepest drawdown
- time negative
- time below stop

Metrics are only displayed when source data provides enough information.

## OBUX049 — Process truth + causes + lessons

Outcome and process are independent.

Examples:

- profitable result + poor process
- loss + clean process

Cause taxonomy supports:

- late exit
- stop ignored
- stale candidate
- fill slippage
- alert delay
- owner hesitation
- broker confirmation gap
- market reversal
- contract decay
- spread/liquidity failure
- mission-account rule stress
- thesis deterioration
- entry chase
- oversized position
- hold-time violation
- source/data problem

Causes are not guessed merely because a trade lost.

## OBUX050 — Truth boundary

Review Center keeps separate:

- Manual Live
- Paper
- Rehearsal
- Proof
- Quarantined

Only Manual Live and Paper are eligible for official-performance classification in this browser projection.

Review Center cannot:

- submit broker orders
- read broker accounts
- auto close
- auto execute
- unlock Live Auto

## Product doctrine

A profitable trade can still be a bad process.

A losing trade can still be a clean process.

Wins and losses receive the same forensic review.
