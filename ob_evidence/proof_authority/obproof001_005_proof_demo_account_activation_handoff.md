# OBPROOF001–005 — Proof / Demo Account Activation

## Sealed parent

`7e5981a2dede05a5240e6c3a7efec45f5c0c614e`

## Activated authority

`OB_PROOF_DEMO_ACCOUNT_V1` activates the existing canonical `proof_demo` account as an isolated simulated backend account.

## Flow

```text
CANONICAL ENGINE
      ↓
OWNER-FIT ELIGIBILITY
      ↓
NOW
      ↓
EXPLICIT OWNER SELECTION
      ↓
PROOF / DEMO ACCOUNT
      ↓
PAPER / SAMPLE POSITION
      ↓
RECORDED DEMO ACCOUNT STATE
```

## Boundaries

- existing owner-profile account registry reused
- no second mission-account registry
- explicit simulated opening balance required
- no invented balance
- no real capital
- no broker link or submission
- owner-fit `NOW` required
- explicit owner selection required
- no automatic contract selection
- explicit option multiplier required
- durable local simulated account/position/event state
- no live mark-to-market claim
- no live broker-equity claim
- no Flask route
- no `app.py` change
- no Tower change
- Hybrid execution false
- automatic execution false
- Live Auto locked

## Deferred

Sanitized scoreboard projection remains `PENDING_OBPROOF006_010`.
Real mode authority remains `PENDING_OBMODE`.

## Next

**OBPROOF006–010 — Sanitized Scoreboard Projection**
