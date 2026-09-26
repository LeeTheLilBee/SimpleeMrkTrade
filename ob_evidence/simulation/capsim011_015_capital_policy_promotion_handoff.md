# CAPSIM011–015 — Capital Policy source promotion and family closure

## Exact accepted parent
`e9c4c895f0635ffde1691d5fc28f49250a3dbbc9` (OBSIM006–010 merged into main).

## Canonical split
`OB_CAPITAL_POLICY_V1` in `web/ob_capital_policy_authority.py` is the **pre-Effective-Policy** producer. It consumes active owner profile plus verified immutable Experimental simulation capital state and canonical OBTIME session-loss evidence. It never resolves Effective Policy or calls CAPSIM admission. The pre-policy result has a stable projection ID, fingerprint, provenance references, normalized limits, explicit readiness/block state and a simulation-only mark.

`OB_EFFECTIVE_POLICY_V1` consumes an **explicit** verified READY `CAPITAL_POLICY` restriction layer. It preserves the existing most-restrictive primitive. All execution/capital capability values remain false; capital layer validation requires the explicit simulation-only, pre-policy, Experimental and restriction-only contract. Missing and malformed layers fail closed.

`OB_CAPITAL_SIMULATION_V1` remains **post-policy** Experimental admission, owning daily realized-loss checks and exact OBSIM OPEN-cost/fill delegation. It does not import `OB_CAPITAL_POLICY_V1` or become an Effective Policy input. Therefore the prohibited dependency cycle is absent.

## Family steps
- CAPSIM011: separate pre-policy projection authority.
- CAPSIM012: verified source-bound capital capacity projection, explicit BLOCK, six-decimal floor, no new owner policy thresholds and no widening.
- CAPSIM013: explicit restriction-only Effective Policy adapter; malformed/forged layer checks and canonical six-decimal equality regression. Prior local test failure compared normalized `0.417517` with pre-normalized `0.417517354022`; integration now binds normalized values.
- CAPSIM014: canonical registry activates `capital_policy`; Effective Policy depends on this pre-policy source, which does not depend on Effective Policy; `PENDING_OBCAP` resolves as retired alias. Owner-profile events correctly invalidate the new dependent authority.
- CAPSIM015: post-policy simulation contract and historical regression expectations updated, independent lanes remain untouched, full-suite evidence checked.

## GitHub verification on exact implementation head
Commit: `5170e6161e6df1eceddb97a7b98896e0248c5e14`
PR run: https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36269408412
Push run: https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36269405932

**Focused: 48 passed. Full repository: 1,276 passed.**
No Tower source files changed.

## Strict scope
This activates the **simulation-only** pre-policy capital restriction input. It does NOT assert that the broad real-money OBCAP program is finished: independent broker-verified capital truth, settled/protected/committed/surplus capital, mission sleeves, waterfall, profit harvesting, high-water ratchet, drawdown modes, and real-account reconciliation remain later work. There is no broker submission, real capital movement, automatic contract selection, Manual Live unlock, Hybrid unlock, Automated unlock, or deployment.

## Next work path
Preserve this accepted CAPSIM/OBSIM foundation and proceed with canonical **OBCAP real-money capital truth and waterfall/modes**, or the next dependency-safe core state **OBPOS** only after its required capital/source boundaries are specified. Then OBPORT, OBSTRAT, OBSAFE, OBREC, OBREV, OBLEARN, OBGUARD, OBSOUL, OBATTN, OBRES, OBML, OBHYB, OBAUTO, OBPERF, and OBUX. No automatic graduation from simulated results into Live authority.
