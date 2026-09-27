/* OBBETA011–015 — observed source is not independently authenticated. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const contractSource = fs.readFileSync("web/static/ob/ob_owner_dashboard_contract.js", "utf8");

async function hydrateWith(payloads) {
  const window = {};
  const responses = {
    "/ob/engine-feed-trust-labels.json": payloads.trust,
    "/ob/manual-live-operator-confidence-readiness-checkpoint.json": payloads.practice,
    "/ob/private-beta-launch-control.json": payloads.beta,
  };
  const context = {
    window,
    fetch: async (url) => {
      const item = responses[url];
      if (item === "network-error") throw new Error("network unavailable");
      return { ok: item !== "http-error", json: async () => item };
    },
  };
  vm.runInNewContext(contractSource, context, { filename: "ob_owner_dashboard_contract.js" });
  return window.OB_OWNER_DASHBOARD_CONTRACT_V21.hydrate();
}

(async () => {
  const falselyTrusted = await hydrateWith({
    trust: { verified: true, independently_authenticated: true, trust: { label: "Verified" } },
    practice: {
      verified: true, readiness_scorecard: { readiness_score: 99 },
      remaining_live_blockers: ["BROKER_PROOF_MISSING"],
    },
    beta: { verified: true, owner_go_no_go_status: "GO", hosted_verified: true },
  });
  assert.equal(falselyTrusted.trust.verified, false);
  assert.equal(falselyTrusted.trust.source_observed, true);
  assert.equal(falselyTrusted.trust.independent_provenance_authenticated, false);
  assert.match(falselyTrusted.trust.label, /independently unverified/);
  assert.equal(falselyTrusted.readiness.operator_practice_source_observed, true);
  assert.equal(falselyTrusted.readiness.score, 99);
  assert.equal(falselyTrusted.readiness.score_is_practice_only, true);
  assert.equal(falselyTrusted.readiness.real_manual_live_ready, false);
  assert.equal(falselyTrusted.readiness.tower_owner_clearance_verified, false);
  assert.equal(falselyTrusted.beta.verified, false);
  assert.equal(falselyTrusted.beta.source_observed, true);
  assert.equal(falselyTrusted.beta.actual_hosted_beta_access_verified, false);
  assert.equal(falselyTrusted.beta.public_launch_enabled, false);
  for (const key of ["trust", "readiness", "private_beta"]) {
    assert.equal(falselyTrusted.source_state[key].verified, false);
    assert.equal(falselyTrusted.source_state[key].source_observed, true);
    assert.equal(falselyTrusted.source_state[key].independent_provenance_authenticated, false);
  }

  const unmarked200 = await hydrateWith({
    trust: { trust: { label: "Fresh" } },
    practice: { readiness_scorecard: { readiness_score: 30 } },
    beta: { status: "READY" },
  });
  assert.equal(unmarked200.trust.verified, false);
  assert.equal(unmarked200.readiness.operator_practice_source_observed, true);
  assert.equal(unmarked200.readiness.score, 30);
  assert.equal(unmarked200.beta.verified, false);

  const badResponses = await hydrateWith({
    trust: {},
    practice: "network-error",
    beta: "http-error",
  });
  assert.equal(badResponses.source_state.trust.status, "guarded");
  assert.equal(badResponses.source_state.trust.verified, false);
  assert.equal(badResponses.source_state.readiness.source_observed, false);
  assert.equal(badResponses.source_state.readiness.verified, false);
  assert.equal(badResponses.source_state.private_beta.status, "guarded");
  assert.equal(badResponses.beta.source_observed, false);
  assert.equal(badResponses.beta.verified, false);
  console.log("OBBETA011–015 source-label behavioral tests passed");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
