# OBSIM011–015 — adverse historical replay regression wall

Parent: `9804f461504a904e0df2a8844b0586d7f3dc6fa2`.

Scope is a **test-only** defense extension of the accepted OBSIM006–010 replay; no changes to replay implementation, positions, capital admission, policy, Tower, Teller, or modes. Uses pre-authored OBTIME-bound option market frames to exercise a severe option-price collapse, explicit full close after shock, later tampered market-time receipt, duplicate frame / missing lane, and Experimental excessive declared loss. Existing OBSIM fill/accounting/receipt chains remain the only simulation trade source.

Acceptance:
- Control and Integrated preserve independent cash/positions and can show shock loss; Experimental remains untouched without explicit admitted trade.
- Shock mark is unrealized until actual simulation close, then canonical OBSIM commission/fill math establishes realized loss.
- Invalid inputs cannot mutate caller history; per-lane receipt chains remain valid.
- No automatic winner selection, strategy promotion, real capital, broker order or live/Hybrid/Automated unlock.
- Focused OBSIM tests and full repository regression must pass. These adversarial tests do **not** prove market profitability, execution feasibility, or live source authenticity.

Continuation after this: OBPOS source-backed position-view authority must reuse existing OBSIM position/fill records and OBENG explicit operational source roles without creating a competing ledger or claiming a repository file is verified broker truth.
