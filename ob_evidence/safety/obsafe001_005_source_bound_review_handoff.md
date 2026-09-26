# OBSAFE001–005 — restrictive source-bound safety review

Parent: `ed2d0f151d534ac4a3e3ed994e0ee21b94ee3863` (OBSTRAT001–005 accepted).
Authority: `OB_SAFETY_REVIEW_V1`.

This first OBSAFE family is a **read-only fail-closed evidence join**, not a competing risk engine. It independently revalidates OBSTRAT → OBPORT → OBPOS lineage, account identity, the exact selected source market frame and verified OBTIME receipt, and canonical OBMODE fingerprint. If a bound canonical trade intent is supplied, it recomputes the existing `evaluate_owner_fit` (including Effective Policy and mode layer) from that source, cross-checks symbol/kind/exact option-research contract and rejects mismatched account/mode evidence. This does not change the existing owner-fit or Effective Policy implementation.

Explicit, source-labelled risk signals are optional input claims, with individual tri-state values for source conflict, source stale, overreach, Negative Dive, Overtime and kill switch. Their hash is an **integrity reference, not institution authentication**. Explicit danger or canonical owner-fit NOT_YET yields BLOCK. Missing or unknown danger evidence, stale market evidence, non-regular session, unbound owner-fit, or owner-fit WATCH yields HOLD. Only complete non-danger input and canonical fit NOW can produce **REVIEW_ONLY**; this is never an order, capital or mode permission. The full source lineage must verify again before emitting the non-money-bearing proof reference.

Out of scope: creating a kill switch actuator, changing source risk limits, approving Manual Live or trading, fetching a broker, real financial balances, Tower, Teller or BuyBox. Those remain separately gated. Source alerts can tighten review; merely setting a source flag to false cannot authenticate real money or authorize a trade.

Next: OBREC consumes this safety receipt only as a separately verifiable review prerequisite, preserves BLOCK/HOLD reasons and produces owner-facing recommendation explanations without trade intent or execution.
