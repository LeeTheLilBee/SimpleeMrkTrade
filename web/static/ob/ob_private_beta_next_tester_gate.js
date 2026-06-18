// OBSERVATORY_V45_NEXT_TESTER_CLEARANCE_GATE_JS

(function () {
  const VERSION = "OB_V45_NEXT_TESTER_CLEARANCE_GATE";
  const ENDPOINT = "/ob/private-beta-next-tester-clearance.json";

  // V45 SMOKE MARKERS
  // Next Tester Clearance Gate
  // Tower-controlled next tester clearance
  // invite blocked conditional cleared
  // checks V44 fix verification
  // NDA invite gate
  // source feed gate
  // feedback closeout gate
  // owner clearance required
  // next tester invite does not create permission
  // private beta only
  // no public signup
  // no public launch
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let gateState = {
    status: "booting",
    httpStatus: null,
    source: "waiting",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function fixPayload() {
    if (window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44_API && window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44_API.getState) {
      const state = window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44) return window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44;

    return {
      verification_status: "PENDING OWNER VERIFICATION",
      next_tester_fix_gate: "blocked_until_verified",
      summary: {
        total_items: 3,
        pending: 3,
        verified: 0
      }
    };
  }

  function closeoutPayload() {
    if (window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43_API && window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43_API.getState) {
      const state = window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43) return window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43;

    return {
      next_tester_decision: "NO-GO",
      summary: {
        unresolved_issues: 3,
        blocker: 1,
        high: 2
      }
    };
  }

  function buildGates() {
    const fix = fixPayload();
    const closeout = closeoutPayload();
    const fixGate = safeText(fix.next_tester_fix_gate, "blocked_until_verified");
    const decision = safeText(closeout.next_tester_decision, "NO-GO");

    return [
      {
        id: "fix_verification",
        label: "V44 fix verification",
        status: fixGate === "verification_clear" ? "cleared" : "blocked",
        detail: "Must-fix and high/blocker issues must be owner-verified before another tester.",
        owner_action: fixGate === "verification_clear" ? "Keep evidence notes attached." : "Complete V44 fix verification."
      },
      {
        id: "session_closeout",
        label: "V43 session closeout",
        status: decision === "GO" ? "cleared" : decision === "CONDITIONAL GO" ? "conditional" : "blocked",
        detail: "Previous session closeout must allow another tester.",
        owner_action: decision === "GO" ? "Proceed only through Tower invite." : "Resolve closeout decision before inviting next tester."
      },
      {
        id: "nda_invite",
        label: "NDA / invite gate",
        status: "conditional",
        detail: "Next tester must be invite-only, NDA-bound, and Tower-controlled.",
        owner_action: "Confirm invite list, NDA status, and tester role before access."
      },
      {
        id: "source_feed",
        label: "Source/feed gate",
        status: "conditional",
        detail: "Tester must be told whether feed data is fresh, stale, guarded, or fallback.",
        owner_action: "Run source audit and keep trust labels visible."
      },
      {
        id: "boundary",
        label: "Execution boundary gate",
        status: "cleared",
        detail: "No broker wiring, no broker API, no auto execution, Live Auto Locked.",
        owner_action: "Do not loosen execution boundaries."
      },
      {
        id: "privacy",
        label: "Privacy/proof gate",
        status: "cleared",
        detail: "No public proof, no public signup, no public launch.",
        owner_action: "Keep feedback, proof, receipts, and session notes private."
      }
    ];
  }

  function decide(gates) {
    if (gates.some(gate => gate.status === "blocked")) return "INVITE BLOCKED";
    if (gates.some(gate => gate.status === "conditional")) return "CONDITIONAL CLEARANCE";
    return "CLEARED FOR NEXT PRIVATE TESTER";
  }

  function buildFallbackPayload() {
    const gates = buildGates();
    const clearance = decide(gates);

    return {
      version: VERSION,
      source: "v45_safe_next_tester_gate_fallback",
      clearance_status: clearance,
      next_tester_gate: clearance,
      gates,
      summary: {
        total_gates: gates.length,
        cleared: gates.filter(gate => gate.status === "cleared").length,
        conditional: gates.filter(gate => gate.status === "conditional").length,
        blocked: gates.filter(gate => gate.status === "blocked").length,
        tower_required: gates.length
      },
      owner_clearance_steps: [
        "Verify V44 fix checklist.",
        "Confirm V43 closeout allows next tester.",
        "Confirm NDA/invite through Tower.",
        "Confirm source/feed label warning for tester.",
        "Confirm no public launch, no public proof, no broker wiring.",
        "Only then send next private beta invite."
      ],
      invite_result_labels: ["INVITE BLOCKED", "CONDITIONAL CLEARANCE", "CLEARED FOR NEXT PRIVATE TESTER"],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        tower_controlled_next_tester_clearance: true,
        owner_clearance_required: true,
        no_public_signup: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        next_tester_invite_does_not_create_permission: true
      },
      warnings: [
        "Next tester clearance is private.",
        "Clearance does not create trading or execution permission.",
        "Tower controls invite access.",
        "No public launch.",
        "No broker wiring."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      clearance_status: safe.clearance_status || fallback.clearance_status,
      next_tester_gate: safe.next_tester_gate || fallback.next_tester_gate,
      gates: Array.isArray(safe.gates) ? safe.gates : fallback.gates,
      summary: { ...(fallback.summary || {}), ...(safe.summary || {}) },
      owner_clearance_steps: Array.isArray(safe.owner_clearance_steps) ? safe.owner_clearance_steps : fallback.owner_clearance_steps,
      invite_result_labels: Array.isArray(safe.invite_result_labels) ? safe.invite_result_labels : fallback.invite_result_labels,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        tower_controlled_next_tester_clearance: true,
        owner_clearance_required: true,
        no_public_signup: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        next_tester_invite_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_NEXT_TESTER_GATE_V45 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_next_tester_gate_v45: normalized,
      next_tester_gate: normalized.next_tester_gate
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaNextTesterGateUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchGate() {
    gateState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      gateState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        gateState.status = "ready";
        gateState.source = normalized.source || "next_tester_gate_snapshot";
        gateState.payload = normalized;
        gateState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        gateState.status = "guarded_fallback";
        gateState.source = "guarded_next_tester_gate_fallback";
        gateState.payload = fallback;
        gateState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      gateState.status = "error_fallback";
      gateState.source = "fetch_error_fallback";
      gateState.payload = fallback;
      gateState.fallbackActive = true;
      gateState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return gateState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("block")) return "red";
    if (text.includes("conditional") || text.includes("required")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-next-tester-gate-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function gateRow(item, index) {
    return `
      <div class="ob-beta-next-tester-gate-row">
        <div class="ob-beta-next-tester-gate-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Gate")}</strong>
          <span>${safeText(item.id, "gate")}</span>
        </div>
        <span>${safeText(item.detail, "Clearance gate.")}<br>${safeText(item.owner_action, "")}</span>
        <div class="ob-beta-next-tester-gate-status ${statusClass(item.status)}">${safeText(item.status, "review")}</div>
      </div>
    `;
  }

  function stepRow(item, index) {
    return `
      <div class="ob-beta-next-tester-gate-row">
        <div class="ob-beta-next-tester-gate-dot">✓</div>
        <div>
          <strong>Clearance step ${index + 1}</strong>
          <span>Tower-controlled</span>
        </div>
        <span>${safeText(item, "Clearance step.")}</span>
        <div class="ob-beta-next-tester-gate-status gold">required</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = gateState.payload || buildFallbackPayload();
    const summary = payload.summary || {};
    const gates = Array.isArray(payload.gates) ? payload.gates : [];
    const steps = Array.isArray(payload.owner_clearance_steps) ? payload.owner_clearance_steps : [];

    return `
      <div class="ob-beta-next-tester-gate-panel" id="obPrivateBetaNextTesterGatePanel" data-ob-v45-next-tester-gate="true">
        <div class="ob-beta-next-tester-gate-head">
          <div>
            <div class="ob-label">Next Tester Clearance Gate · V45</div>
            <div class="ob-beta-next-tester-gate-title">Tower-Controlled Next Tester Clearance</div>
            <div class="ob-beta-next-tester-gate-subtitle">${safeText(payload.clearance_status, "Owner clearance required")} · ${safeText(gateState.status, "booting")} · invite stays private and Tower-controlled.</div>
          </div>
          <div class="ob-beta-next-tester-gate-chip-row">
            <span class="ob-beta-next-tester-gate-chip ${statusClass(payload.next_tester_gate)}">${safeText(payload.next_tester_gate, "review")}</span>
            <span class="ob-beta-next-tester-gate-chip gold">Tower invite</span>
            <span class="ob-beta-next-tester-gate-chip red">No public signup</span>
          </div>
        </div>

        <div class="ob-beta-next-tester-gate-grid">
          ${card("Gates", safeText(summary.total_gates, gates.length))}
          ${card("Cleared", safeText(summary.cleared, "0"))}
          ${card("Conditional", safeText(summary.conditional, "0"))}
          ${card("Blocked", safeText(summary.blocked, "0"))}
          ${card("Tower", "required")}
          ${card("Public", "no")}
          ${card("Broker", "no")}
        </div>

        <div class="ob-beta-next-tester-gate-section">
          <div class="ob-beta-next-tester-gate-section-title">Clearance gates</div>
          <div class="ob-beta-next-tester-gate-list">${gates.map(gateRow).join("")}</div>
        </div>

        <div class="ob-beta-next-tester-gate-section">
          <div class="ob-beta-next-tester-gate-section-title">Owner clearance steps</div>
          <div class="ob-beta-next-tester-gate-list">${steps.map(stepRow).join("")}</div>
        </div>

        <div class="ob-beta-next-tester-gate-callout">
          <strong>Invite result labels</strong><br>
          ${(payload.invite_result_labels || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-next-tester-gate-note"><strong>Soulaana:</strong><br>The next door opens only when the last lesson was fixed, verified, and cleared by Tower.</div>
        <div class="ob-beta-next-tester-gate-boundary"><strong>Boundary:</strong><br>Next tester clearance is private. It does not create permission. No public signup. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaNextTesterGatePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const verification = document.getElementById("obPrivateBetaFixVerificationPanel");
    const closeout = document.getElementById("obPrivateBetaSessionCloseoutPanel");
    const triage = document.getElementById("obPrivateBetaIssueTriagePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (verification && verification.parentNode) verification.insertAdjacentElement("afterend", panel);
    else if (closeout && closeout.parentNode) closeout.insertAdjacentElement("afterend", panel);
    else if (triage && triage.parentNode) triage.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = gateState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v45-next-tester-gate", "ready");
    window.OB_V45_PRIVATE_BETA_NEXT_TESTER_GATE_STATE = {
      version: VERSION,
      status: gateState.status,
      fallbackActive: gateState.fallbackActive,
      clearanceStatus: payload.clearance_status,
      nextTesterGate: payload.next_tester_gate,
      towerControlledNextTesterClearance: true,
      ownerClearanceRequired: true,
      noPublicSignup: true,
      noPublicLaunch: true,
      noPublicProof: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchGate();
    }, 2700);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaFixVerificationUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_NEXT_TESTER_GATE_V45_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return gateState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchGate,
    renderPanel,
    setFlags
  };
})();
