"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");

const src=fs.readFileSync("web/static/ob/ob_engine_feed_adapter.js","utf8");
const window={};
const document={readyState:"loading",addEventListener(){}};
vm.runInNewContext(src,{window,document,Date,Math,Number,String,Boolean,Object,Array,Set,Map,JSON,console});
const api=window.OB_ENGINE_FEED_ADAPTER_V25;
assert.equal(api.endpoint,"/ob/engine-feed-snapshot.json");
const doc={
  version:"OBDATA009_HOSTED_PROVIDER_NOT_CONFIGURED",
  market_data_state:"provider_not_configured",
  source:null,as_of:null,reason:"No authorized data source connected.",
  // Even a maliciously included market fixture must never leak to active room views.
  sectors:[{name:"Untrusted example",symbols:["SAMPLE"]}],
  positions_preview:[{symbol:"SAMPLE"}],
  candidates_preview:[{symbol:"SAMPLE"}],
  manual_live_queue:[{symbol:"SAMPLE"}],
};
const p=api.projectPayload(doc);
assert.equal(p.market_data_state,"provider_not_configured");
assert.equal(p.projection_status,"unavailable");
assert.equal(p.current_eligible,false);
assert.equal(p.display_eligible,false);
assert.match(p.reason,/No authorized data source connected/);
assert.equal(p.source_identified,false);
assert.equal(p.timestamp_identified,false);
assert.equal(p.sectors.length,0);
assert.equal(p.positions_preview.length,0);
assert.equal(p.candidates_preview.length,0);
assert.equal(p.manual_live_queue.length,0);
assert.equal(api.safety.broker_api_enabled,false);
assert.equal(api.safety.order_submission_enabled,false);
assert.equal(api.safety.capital_movement_enabled,false);
assert.equal(api.safety.auto_execution_enabled,false);
console.log("OBDATA009: provider pending remains unavailable, empty, and execution-locked.");
