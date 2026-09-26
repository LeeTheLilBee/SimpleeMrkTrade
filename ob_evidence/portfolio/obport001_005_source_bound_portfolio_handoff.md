# OBPORT001–005 — read-only lane portfolio comparison

Parent: `9dd6996591a7b273dc670244717e52b1386528dd` (OBPOS001–005 accepted).

`OB_PORTFOLIO_VIEW_V1` consumes exactly three verified, same-account, same-time OBPOS source snapshots over the same OBSIM harness. It reuses the existing source-position fill/mark math and captures each Control, Integrated and Experimental lane independently. Projected stock and option exposure use canonical multipliers and last source marks. It checks source equity/cash/exposure equality, retains source position IDs, trade/receipt roots, and hashes the immutable comparison.

No automatic strategy ranking, promotion, pooled capital, actual bank or broker authentication, available acquisition money, trading-mode change, execution/capital movement or direct BuyBox connection. The reference is non-money-bearing and requires Tower permission; Teller remains the financial deployment/readiness interface.

Next OBSTRAT family must treat this as source-backed portfolio context and maintain separate explicit human strategy/contract choices. It may produce explainable, reviewable candidate packets but may not create an autonomous strategy selection or bypass Effective Policy, safety, review and owner-level execution gates.
