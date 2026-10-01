# The Grounds — permission-safe owner operating pulse / GRD066–070

Source-only continuation of [Grounds draft PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51). Tower remains under separate [review PR #52](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/52). No live Clouds publishing, hosted data, resident service, payment, dispatch or paid Render resource is enabled.

## Implemented
- `GroundsOperations.property_pulse` now includes three additional **same-property aggregate** blockers: urgent flagged work missing recorded human review; unfinished unit turnovers; unresolved major/urgent inspection findings. Includes an observed-at timestamp and keeps rent collections as `None` because Teller is the financial source.
- `grounds/owner_status.py` exposes `owner_operating_snapshot`, a local owner-scoped prospective envelope with only aggregate counts; it excludes tenant identity, exact work descriptions, lease refs, private proof, invoice/payment, capital and OB data. It explicitly reports `publisher_enabled=False` and `identity_receiver_certified=False`. This is **not** an actual Clouds integration, nor an externally authenticated message.
- Soulaana's existing property pulse explanation now includes the three blocker counts, source timestamp and next useful action, without reporting a call to emergency services, notification delivery, leasing approval, rent receipt or acquisition capital.
- Fictional fixture tests cover scope denial for resident/regional/another-property actor, absence of private strings, changes to human triage/inspection/turnover state, and Soulaana nonexecution.
- `foundation_status()` distinguishes a local sanitized snapshot from disabled live Clouds publishing.

## Next integration dependency
A future Tower-certified Grounds → Clouds publisher needs explicit audience/session/issuer, exact owner role, property ownership/assignment checks, rate/retention/incident control, stale-source rejection, signed provenance and a sanctioned redaction policy. Keep Teller financial status separate and never export resident work descriptions merely because a dashboard requests more detail. No automatic publishing or data movement is authorized in this source pack.
