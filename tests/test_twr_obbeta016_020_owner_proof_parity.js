/* TWR-OBBETA016-020: run the real older Tower owner contract, don't trust self-claims. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("web/static/ob/ob_owner_dashboard_contract.js", "utf8");

async function run(responses, globals = {}) {
  const window = { ...globals, dispatchEvent() {} };
  const context = {
    window,
    Date,
    CustomEvent: function(name, payload) { this.name = name; this.payload = payload; },
    fetch: async (url) => {
      const value = responses[url];
      if (value === "NETWORK_DOWN") throw new Error("offline");
      return { ok: value !== "HTTP_DENIED", status: value === "HTTP_DENIED" ? 403 : 200,
        json: async () => value };
    }
  };
  vm.runInNewContext(source, context, { filename: "ob_owner_dashboard_contract.js" });
  return window.OB_OWNER_DASHBOARD_CONTRACT_V21.hydrate();
}

(async () => {
  const spoofed = await run({
    "/ob/account-experience.json": { verified: true, owner_mission_accounts: [
      { account_id: "ob_acct_trust", actual_capital_known: true, actual_capital_value: 1000000 }
    ] },
    "/ob/engine-feed-trust-labels.json": {
      verified: true, source: "live", trust: { label: "Verified", safeToDisplay: "safe" }
    },
    "/ob/manual-live-operator-confidence-readiness-checkpoint.json": {
      verified: true, readiness_scorecard: { readiness_score: 99, readiness_label: "GO" },
      remaining_live_blockers: [{ blocker_id: "PROVIDER_PENDING", label: "Provider pending" }]
    },
    "/ob/private-beta-launch-control.json": { verified: true, status: "GO" },
  }, {
    OB_OWNER_MISSION_SNAPSHOT: {
      verified: true, missions: [{ mission_id: "trust", actual_capital_known: true,
        actual_capital_value: 999999, capital_progress_known: true, capital_progress_percent: 100 }]
    },
    OB_OWNER_CHANGE_HISTORY: { verified: true, items: [{ title: "Fake history" }] }
  });
  for (const key of ["account_experience", "engine_trust", "manual_live_readiness", "private_beta"]) {
    assert.equal(spoofed.source_state[key].verified, false);
    assert.equal(spoofed.source_state[key].source_observed, true);
    assert.equal(spoofed.source_state[key].independent_provenance_authenticated, false);
  }
  assert.equal(spoofed.trust.verified, false);
  assert.match(spoofed.trust.label, /independently unverified/);
  assert.equal(spoofed.readiness.verified, false);
  assert.equal(spoofed.readiness.operator_practice_source_observed, true);
  assert.equal(spoofed.readiness.score, 99);
  assert.equal(spoofed.readiness.score_is_practice_only, true);
  assert.equal(spoofed.readiness.real_manual_live_ready, false);
  assert.equal(spoofed.readiness.tower_owner_clearance_verified, false);
  assert.equal(spoofed.beta.verified, false);
  assert.equal(spoofed.beta.actual_hosted_beta_access_verified, false);
  assert.equal(spoofed.beta.public_launch_enabled, false);
  assert.equal(spoofed.interpretation_state.all_critical_sources_verified, false);
  assert.equal(spoofed.interpretation_state.may_claim_capital_progress, false);
  assert.equal(spoofed.interpretation_state.may_claim_change_history, false);
  assert.equal(spoofed.interpretation_state.may_claim_cross_mission_performance_patterns, false);
  assert.ok(spoofed.mission_sky.every(x => x.actual_capital_known === false && x.verified_snapshot === false));
  assert.equal(spoofed.since_you_were_here.verified, false);

  const guarded = await run({
    "/ob/account-experience.json": {},
    "/ob/engine-feed-trust-labels.json": "HTTP_DENIED",
    "/ob/manual-live-operator-confidence-readiness-checkpoint.json": "NETWORK_DOWN",
    "/ob/private-beta-launch-control.json": null
  });
  for (const key of ["account_experience", "engine_trust", "manual_live_readiness", "private_beta"]) {
    assert.equal(guarded.source_state[key].verified, false);
    assert.equal(guarded.source_state[key].source_observed, false);
  }
  assert.equal(guarded.readiness.real_manual_live_ready, false);
  assert.equal(guarded.beta.public_launch_enabled, false);
  console.log("TWR-OBBETA016-020 behavioral source and fake-capital denial passed");
})().catch(error => { console.error(error); process.exitCode = 1; });
