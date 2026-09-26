# OBSTRAT001–005 — explicit option-first strategy review, no automatic trading

Parent: `c226d4463f6596780eb860b24f670f020b7471a0` (OBPORT001–005 accepted).

The `OB_STRATEGY_REVIEW_V1` evidence packet is tied to the accepted three-lane OBPORT comparison and exact pre-existing OBSIM market frame instrument references. Multiple candidate labels may be reviewed without rank or default selection. An option requires an exact contract ID; a stock candidate requires an explicit owner-declared fallback rationale and a canonical STOCK source frame. All source refs are source assertions, not proof of external institution authentication.

A user may explicitly confirm one candidate **for review**; that does not create an executable trade intent, allocate capital, admit risk, submit a broker order, modify operating modes, select a winning simulation lane or waive downstream safety/review checks. There are no real-market feed or broker integrations here. Existing OBTIME, CAPSIM, OBPOS and OBPORT remain authoritative in their respective boundaries. Tower and Teller remain separate and BuyBox never reads OB strategy choices.

Next gating families: OBSAFE (explicit safety restrictions and denial), OBREC (reviewable recommendation packet consuming existing strategy/market/policy evidence); no execution or Manual Live without separately verified identity, mode, capital, broker, compliance and owner approval.
