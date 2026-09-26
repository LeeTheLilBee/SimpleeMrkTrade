# CAPSIM011–012 — Non-circular pre-policy simulation capital projection

## Accepted parent and branch
Parent: `e9c4c895f0635ffde1691d5fc28f49250a3dbbc9` (OBSIM006–010 accepted on main).
Feature branch: `capsim-capital-policy-promotion-capsim011-015`.

## Implemented here
- New, separate `OB_CAPITAL_POLICY_V1` pre-policy authority in `web/ob_capital_policy_authority.py`.
- Consumes owner-confirmed active Operating Profile and verified, immutable Experimental CAPSIM capital-state and OBTIME session-loss snapshots.
- Does **not** import, call, or read `OB_EFFECTIVE_POLICY_V1`; prevents policy → post-policy admission → policy recursion.
- Produces account-bound, evidence-hash-bound, six-decimal canonical restrictions for the existing owner loss/allocation/daily-loss limits.
- Uses current simulated cash/equity and equity/high-water ratios as a restriction factor, never to widen owner's baseline.
- Incomplete time coverage, exhausted daily loss, no positive capacity, or tampering fails closed.
- New focused tests and CI, with syntax, focused and complete repository regression walls.

## Exact verification
GitHub Actions push run: https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36269022249
Focused: **43 passed**.
Full: **1,271 passed**.

## Explicitly NOT claimed
This is **CAPSIM011–012 groundwork only**. It does not yet:
- activate `CAPITAL_POLICY` within Effective Policy;
- retire `PENDING_OBCAP` in the canonical authority registry;
- complete CAPSIM013–015;
- implement real/broker-verified OBCAP truth, waterfalled mission sleeves, harvest, or capital modes;
- grant any Manual Live, Hybrid, Automated, broker, or real-capital authority.

## Next implementation
CAPSIM013–015 must create a verified restriction-only adapter, activate canonical policy source and registry without a dependency cycle, update historical pending regressions, and pass the entire suite. Verify six-decimal canonical comparison rather than comparing pre-normalized raw floating-point calculations directly. Do not merge or claim family closure before those gates.
