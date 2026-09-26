# OBREC001–005 — safety-bound recommendation review

Parent: `269d203419256bd05a2c7863cf837e1ed2647b9f` (OBSAFE001–005 accepted).
New read-only authority: `OB_RECOMMENDATION_REVIEW_V1`.

OBREC re-verifies **all** required OBSAFE lineage (OBSTRAT, portfolio/position evidence, exact OBTIME, canonical OBMODE, source danger flags, optional canonical owner fit and Effective Policy context). It refuses a status that is merely a copied safety ID or an unverified hash. It preserves safety BLOCK as BLOCKED; HOLD as EVIDENCE_PENDING; and REVIEW_ONLY as OWNER_REVIEW_READY. The last state means owner review alone: no trade intent, broker order, capital movement, manual live/Hybrid/Automated unlock or automatic contract selection.

Every candidate card points to an existing canonical frame with exact option contract or explicitly explained stock fallback, source refs and the explicit owner review selection. No system winner/rank or investment return forecast is calculated. Receipt verification recomputes from the actual upstream inputs; the non-money-bearing reference requires that entire lineage again, and still needs Tower authorization if later exposed.

This pack changes no Tower, Teller, BuyBox, OB policy, trading mode, broker, or deployed runtime. It does not claim authenticated market/broker data from historical simulation records.

Next: OBREV owner-decision and outcome review proof should consume OBREC and source-backed owner actions, retain negative-dive/overtime reasons, not fabricate manual broker fills or performance. Learning can use only verified review evidence and must remain bounded.
