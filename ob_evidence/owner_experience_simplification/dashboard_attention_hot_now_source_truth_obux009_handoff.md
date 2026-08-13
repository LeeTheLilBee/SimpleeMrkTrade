# OBUX009 — Dashboard Attention and Hot-Now Source Truth

## Evidence hash

4bc2313fb614886692857b2f5650e73829e72ca272e343784738b3819fb8aed4

## Gate state

dashboard_attention_hot_now_source_truth_sealed

## Recommendation

GO_FOR_DASHBOARD_SIMPLIFICATION

## Dashboard doctrine

The normal Dashboard answers one question:

> What matters right now?

Soulaana leads before raw data.

Interesting does not mean actionable.

Fallback/watch context cannot create a confirmed position or trading instruction.

Engineering and proof panels remain available behind Show me why.

## Safety

- GP066 remains parked.
- Owner acceptance walkthrough remains incomplete.
- Manual Live remains owner-only.
- Live Auto remains locked.
- Broker submission remains locked.
- Real-capital movement remains locked.

## Payload

{
  "dashboard_contract_preferred": true,
  "engine_feed_allowed": true,
  "gate_state": "dashboard_attention_hot_now_source_truth_sealed",
  "hardcoded_mu_amd_intc_open_position_fallback_removed": true,
  "interesting_equals_actionable": false,
  "package": "OBUX009",
  "recommendation": "GO_FOR_DASHBOARD_SIMPLIFICATION",
  "route_sample_signals_consumed": false,
  "static_fallback_actionable": false,
  "static_fallback_confirmed_position": false,
  "static_market_data_fallback_only": true,
  "title": "Dashboard Attention and Hot-Now Source Truth"
}
