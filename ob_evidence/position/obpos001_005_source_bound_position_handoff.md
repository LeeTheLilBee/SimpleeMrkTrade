# OBPOS001–005 — source-backed position view and no-second-ledger closure

Parent: `5ac50de5b37be8b34640222a2cdc9df95e1ddf67` (OBSIM011–015 accepted).
Canonical read-only authority: `OB_POSITION_TRUTH_V1`.

The implementation **does not create a position execution/fill engine**. It uses canonical OBSIM lane-specific positions, fills, decisions, receipts and latest market frames. It independently reconciles open/close trade IDs, frame/instrument keys, quantities, stock/option multiplier, source prices, fill cash effects, realized/unrealized P&L and open positions into a deterministic integrity-hash-bound per-lane view. Cross-lane state is not pooled. Corrupted receipt chain, anomalous fill, duplicate source or position/ledger divergence fails closed. Snapshot is explicitly **SIMULATED**, not authenticated live broker truth or execution authorization.

The repository source path delegates to existing `OB_ENGINE_ACCOUNT_AUTHORITY_V1` `build_account_authority()` and `build_position_authority()`. It reports the actual open/closed store's `explicit_store` vs `unresolved` state and raw record counts without manufacturing positions from count, historical reporting, or a missing/unreadable file. An explicit empty list yields count zero *only as an explicit repository source observation*, not a verified broker flat book. Its caller-supplied source hash proves no bank/broker authentication.

Boundaries: explicit canonical account identity, source lane, source record role and state; no real provider adapter; no trade execution, broker order, capital transfer, OB mode change, Teller readiness, Tower changes or OB–BuyBox connector.

Next OBPOS work: extend evidence-driven repository position-row normalization only when exact source field/instrument/provenance contract is verified; retain prior open/closed state and mark freshness instead of inventing a current mark. OBPORT should consume accepted OBPOS views, not create its own position math. Real holdings require an authenticated provider-specific read-only adapter and independent reconciliation before any live claim.
