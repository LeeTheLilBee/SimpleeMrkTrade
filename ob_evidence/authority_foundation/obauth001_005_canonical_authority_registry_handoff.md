# OBAUTH001–005 — Canonical Authority Registry

## Sealed parent

`94732965cd1bf980f3314a5b7eeb94d81ee58b8e`

## Canonical authority

`OB_CANONICAL_AUTHORITY_REGISTRY_V1`

Record schema: `OB_AUTHORITY_RECORD_V1`

## Repo-fit decision

`web/ob_engine_account_authority.py` remains byte-exact and untouched.

Its existing authority registry is preserved as a compatibility projection.

All new canonical authority registration begins in:

`web/ob_authority_registry.py`

## Current canonical authorities

- existing_canonical_engine_feed
- OB_OPTIONS_RESEARCH_V1
- OB_ENGINE_ACCOUNT_AUTHORITY_V1
- OB_OWNER_OPERATING_PROFILE_V1
- OB_TRADE_INTENT_V1
- OB_OWNER_FIT_ELIGIBILITY_V1
- OB_PROOF_DEMO_ACCOUNT_V1
- OB_PROOF_SANITIZED_SCOREBOARD_V1

## Historical aliases

- PENDING_OBRISK006_010 -> OB_OWNER_FIT_ELIGIBILITY_V1
- PENDING_OBRISK -> OB_OWNER_FIT_ELIGIBILITY_V1
- PENDING_OBPROOF006_010 -> OB_PROOF_SANITIZED_SCOREBOARD_V1

Historical sealed contracts are not rewritten.

## Authority discipline

Each active authority declares ownership, inputs, policy inputs, triggers,
bounded effects, mutation scope, forbidden effects, failure behavior,
explanation, evidence, Review visibility, temporal validity, and learning boundary.

## Explicitly pending

- OBAUTH006–010 account identity + truth taxonomy
- OBPOLICY
- OBEVENT
- OBMODE
- OBDATA source provenance
- OBTIME temporal context
- OBCTX decision context

## Execution boundary

The authority registry grants no broker submission, capital movement,
automatic contract selection, Hybrid execution, or automatic execution.

## Next

**OBAUTH006–010 — Account Identity + Truth Taxonomy**
