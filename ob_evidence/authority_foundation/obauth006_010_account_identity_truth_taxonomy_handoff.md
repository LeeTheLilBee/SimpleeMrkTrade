# OBAUTH006–010 — Account Identity + Truth Taxonomy

## Sealed parent

`e444041d9a65e1411116cd199b7cbbde8db7cc56`

## Canonical authority

`OB_ACCOUNT_IDENTITY_TRUTH_V1`

## Account namespace

The existing `OB_OWNER_OPERATING_PROFILE_V1.ACCOUNT_REGISTRY` remains the namespace authority.

No second account registry was created.

Accounts:

- personal
- trust
- simplee_world_business
- simplee_on_the_go_atm
- the_grounds_apartment
- proof_demo

There is intentionally no default account.

## Truth state

- CURRENT
- UNKNOWN
- CONFLICT
- STALE

## Origin class

- REPOSITORY_STATE
- PROJECTED
- HISTORICAL
- OWNER_ENTERED
- SIMULATED
- UNKNOWN

Truth state and truth origin are separate dimensions.

A current simulated value remains SIMULATED.
A current owner-entered value remains OWNER_ENTERED.

## Hard semantics

- UNKNOWN stays UNKNOWN
- CONFLICT stays CONFLICT
- STALE stays STALE
- SIMULATED stays SIMULATED
- OWNER_ENTERED stays OWNER_ENTERED
- projections cannot overwrite operational state
- historical reporting cannot overwrite operational state
- repository state does not claim live broker reconciliation
- no source precedence guess silently resolves conflicts

## Registry transition

`PENDING_OBAUTH006_010` is retired to `OB_ACCOUNT_IDENTITY_TRUTH_V1`.

## Next

**OBPOLICY001–010 — Policy Registry + Most-Restrictive Resolver**
