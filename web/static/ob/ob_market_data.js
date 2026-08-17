
// OBSERVATORY — OBDATA002
// LIVE-PATH STATIC MARKET FIXTURE QUARANTINE
//
// The former static market fixture was moved to:
//
//   web/static/ob/demo/ob_market_data_demo.js
//
// Git history also preserves the original.
//
// Live Observatory rooms are not allowed to silently consume static/demo
// sector or symbol state as current market truth.

window.OB_MARKET_DATA = Object.freeze({
  status: "quarantined",
  authority: "DEMO_ONLY",
  live_eligible: false,
  current_market_truth: false,
  sectors: [],
  symbols: [],
  signals: [],
  reason:
    "Static Observatory market fixtures are quarantined from the live/current data path."
});

window.OB_MARKET_DATA_DEMO_ONLY = true;
