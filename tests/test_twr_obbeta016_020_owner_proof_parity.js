/* TWR-OBBETA016–020: exercise the ACTUAL currently served OBUX091 owner
 * contract. A self-reported browser or API verified flag is not independent
 * capital/source authentication. This is a behavioral negative test.
 */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("web/static/ob/ob_owner_dashboard_contract.js", "utf8");

async function run(responses, globals = {}) {
  const window = {...globals, dispatchEvent() {}};
  const fetched = [];
  const context = {
    window, Date,
    CustomEvent: function(name,payload) {this.name=name;this.payload=payload;},
    fetch: async (url,options) => {
      fetched.push([url,options]);
      const value=responses[url];
      if (value==="NETWORK_DOWN")throw Error("offline");
      return {ok:value!=="HTTP_DENIED",status:value==="HTTP_DENIED"?403:200,
        json:async()=>value};
    }
  };
  vm.runInNewContext(source,context,{filename:"ob_owner_dashboard_contract.js"});
  const api=window.OB_OWNER_DASHBOARD_CONTRACT_V21;
  const contract=await api.hydrate();
  return {contract,api,fetched};
}

(async () => {
  const {contract:spoofed,api,fetched}=await run({
    "/ob/engine-feed-trust-labels.json": {
      verified:true, source:"live", trust:{label:"Verified",safeToDisplay:"safe"}
    },
    "/ob/manual-live-operator-confidence-readiness-checkpoint.json": {
      verified:true, readiness_scorecard:{readiness_score:99,readiness_label:"GO"},
      remaining_live_blockers:[{blocker_id:"PROVIDER_PENDING",label:"Provider pending"}]
    },
    "/ob/private-beta-launch-control.json":{verified:true,status:"GO"}
  },{
    OB_OWNER_CAPITAL_LANE_SNAPSHOT:{
      verified:true,lanes:[{lane_id:"trust",actual_capital_known:true,
        actual_capital_value:999999,capital_progress_known:true,
        capital_progress_percent:100,verified_snapshot:true}]
    },
    OB_OWNER_MISSION_SNAPSHOT:{verified:true,missions:[
      {mission_id:"trust",actual_capital_value:1000000}]},
    OB_OWNER_CHANGE_HISTORY:{verified:true,items:[{title:"Invented win"}]}
  });
  assert.equal(api.version,"OBUX091_095_OWNER_INTELLIGENCE_CONTRACT");
  assert.equal(fetched.length,3,"only existing protected owner evidence endpoints");
  for (const [url,options] of fetched) {
    assert.ok(url.startsWith("/ob/"));
    assert.equal(options.credentials,"same-origin");
  }
  for (const key of ["trust","readiness","private_beta"]) {
    assert.equal(spoofed.source_state[key].verified,false,key);
    assert.equal(spoofed.source_state[key].source_observed,true,key);
    assert.equal(spoofed.source_state[key].independent_provenance_authenticated,false,key);
  }
  assert.equal(spoofed.trust.verified,false);
  assert.match(spoofed.trust.label,/independently unverified/);
  assert.equal(spoofed.readiness.verified,false);
  assert.equal(spoofed.readiness.operator_practice_source_observed,true);
  assert.equal(spoofed.readiness.score,99);
  assert.equal(spoofed.readiness.score_is_practice_only,true);
  assert.equal(spoofed.readiness.real_manual_live_ready,false);
  assert.equal(spoofed.readiness.production_manual_live_permission,false);
  assert.equal(spoofed.readiness.tower_owner_clearance_verified,false);
  assert.equal(spoofed.beta.verified,false);
  assert.equal(spoofed.beta.actual_hosted_beta_access_verified,false);
  assert.equal(spoofed.beta.public_launch_enabled,false);
  assert.equal(spoofed.history.may_claim_change_history,false);
  assert.equal(spoofed.history.may_claim_cross_lane_performance_patterns,false);
  assert.equal(spoofed.capital_lanes.length,6);
  assert.ok(spoofed.capital_lanes.every(x => x.actual_capital_known===false &&
    x.verified_snapshot===false && x.actual_capital_value===null));
  for (const key of ["broker_api_enabled","broker_order_submission_enabled",
    "real_capital_movement_enabled","auto_execution_enabled"]) {
    assert.equal(spoofed.boundaries[key],false,key);
  }
  assert.equal(spoofed.boundaries.live_auto_locked,true);

  const {contract:guarded}=await run({
    "/ob/engine-feed-trust-labels.json":"HTTP_DENIED",
    "/ob/manual-live-operator-confidence-readiness-checkpoint.json":"NETWORK_DOWN",
    "/ob/private-beta-launch-control.json":null
  });
  for (const key of ["trust","readiness","private_beta"]) {
    assert.equal(guarded.source_state[key].verified,false,key);
    assert.equal(guarded.source_state[key].source_observed,false,key);
  }
  assert.equal(guarded.readiness.real_manual_live_ready,false);
  assert.equal(guarded.beta.public_launch_enabled,false);
  assert.ok(guarded.capital_lanes.every(x=>x.actual_capital_known===false));
  console.log("OBUX091 real owner contract: 3 source spoof negatives + 6 capital lanes + denied sources passed");
})().catch(error=>{console.error(error);process.exitCode=1;});
