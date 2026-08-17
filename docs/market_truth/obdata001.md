# OBDATA001 — Existing Canonical Pipeline Inventory & Authority Map

Source branch: `ob-observatory-atmosphere-obux026-030`
Source SHA: `0288927ac8c0734b475767087f92301761ebef69`

## Finding

OB already has a canonical engine/pipeline.

The problem is not the absence of canonical architecture.

The problem is the boundary between canonical engine state and web-room presentation.

## Existing pipeline

- `engine/run_full_pipeline.py`
- `engine/bootstrap_signal_universe.py`
- `engine/run_execution_selection.py`
- `engine/run_symbol_intelligence.py`
- `engine/market_universe.py`

## Existing canonical processors

- `engine/canonical_candidate.py`
- `engine/canonical_decision_gate.py`
- `engine/canonical_decision_object.py`
- `engine/canonical_execution_guard.py`
- `engine/canonical_trade_state.py`

These files remain unchanged.

## Important authority distinction

Canonical does not mean live.

A derived output inherits the provenance of its inputs.

The current bootstrap signal generator is seed/test infrastructure.
The static universe lists are discovery membership, not current market truth.

## Existing web snapshot route

Route: `/ob/engine-feed-snapshot.json`

Classification: `ROUTE_FOUND_REQUIRES_PROVENANCE_GUARD`

Detected data/canonical tokens:

- `market_universe`
- `pipeline_status`
- `positions`
- `review_summary`
- `positions_preview`
- `candidates_preview`
- `manual_live_queue`

The web projection therefore remains fail-closed when source/as-of provenance is incomplete.

See:

`evidence/market_truth/obdata001_authority_map.json`
