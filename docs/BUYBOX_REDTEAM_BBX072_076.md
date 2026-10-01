# BBX072–076 — Owner Red Team / source-bound financial stress

**Status:** Draft PR #129 into the isolated BuyBox working branch. No production launch, Tower permission, Teller capital readiness, professional verification, or paid Render resource is authorized by this source change.

This is a real owner workflow, not a demonstration storefront. The owner enters explicit stress multipliers and a rationale against actual persisted annual revenue/expense records, both tied to encrypted uploaded originals, exact source evidence IDs and an identical reporting period. The records must have an owner-reviewed documentary state. BuyBox reads and checks each encrypted original's SHA-256 before rendering an available base or persisting an owner's scenario.

The new `buybox/red_team.py` refuses missing originals, unsupported metrics, periods that disagree, non-decimal factors, negative/oversized factors, changed current opportunity records and a broken saved revision/digest. The owner record freezes its exact source revision and digest, source evidence IDs/hash references, model inputs, base operating difference, stress operating difference and delta. It does **not** alter underlying metrics, claim historical performance, decide whether to buy, or claim money/capacity readiness.

The owner interface is `/opportunities/<id>/red-team`. Soulaana uses those actual saved records to explain the owner's assumption, its financial-only scope, supporting evidence, current vs historical revision, and unavailable external readiness. Focus Desk includes actual owner stress events. No values are manufactured in a new owner's opportunity.

A subsequent opportunity revision makes an earlier stress **HISTORICAL_RECHECK_REQUIRED**. The earlier record remains immutable. All computations use decimal arithmetic and this pack only supports a simple alternative operating-revenue/expense multiplier. It is not a vertical-specific event engine. Asset risks such as contract assignability, lost ATM locations, title/liens, water access, property taxes, insurance, repairs, physical cash timing or financing covenants need dedicated evidence and modeling contracts. Even a positive stress cannot waive a hard evidence or Tower/Teller gate.

Run `python -m unittest discover -s buybox/tests -v` for tests, including actual temporary encrypted source uploads, model integrity, stale writes, missing evidence, unauthorized requests and source tamper rejection. Test fixtures never populate owner data. No direct OB, Vault or lender integrations are introduced.
