// OBSERVATORY_V41_GUIDED_PRIVATE_BETA_SESSION_RUNBOOK_JS

(function () {
  const VERSION = "OB_V41_GUIDED_PRIVATE_BETA_SESSION_RUNBOOK";
  const ENDPOINT = "/ob/private-beta-session-runbook.json";

  // V41 SMOKE MARKERS
  // Guided Private Beta Session Runbook
  // step-by-step tester session path
  // Dashboard Market Map Symbol Page Trade Center Review Center
  // owner notes per room
  // tester observation goals
  // stop conditions
  // do not continue if confused
  // private beta session path
  // no public launch
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let runbookState = {
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

  function queuePayload() {
    if (window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API && window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API.getState) {
      const state = window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API.getState();
      if (state && state.payload) return state.payload;
    }
    if (window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40) return window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40;

    return {
      summary: { blocker: 1, high: 2, needs_fix: 1 },
      review_queue_label: "Owner review required"
    };
  }

  function sessionSteps() {
    return [
      {
        step: 1,
        room: "Dashboard",
        route: "/ob/dashboard",
        tester_goal: "Understand what matters now: mode, Tower state, mission account, source trust, and next action.",
        owner_note: "Ask tester what they think they should do first.",
        stop_condition: "Stop if tester thinks OB is telling them to trade immediately."
      },
      {
        step: 2,
        room: "Market Map",
        route: "/ob/market-map",
        tester_goal: "Read the constellation/sky view and identify fresh/stale/fallback labels.",
        owner_note: "Ask tester whether the sky feels like observation, not orders.",
        stop_condition: "Stop if tester cannot identify source freshness labels."
      },
      {
        step: 3,
        room: "Symbol Page",
        route: "/ob/symbol/MU",
        tester_goal: "Open one symbol and understand one-star context, reasons, risk, and permission boundaries.",
        owner_note: "Ask tester whether one-symbol context feels explainable.",
        stop_condition: "Stop if tester reads the symbol page as an execution command."
      },
      {
        step: 4,
        room: "Trade Center",
        route: "/ob/trade-center",
        tester_goal: "Review candidates and Manual Live wording without assuming broker connection.",
        owner_note: "Ask tester to find No broker API, No auto execution, and Live Auto Locked.",
        stop_condition: "Stop if tester thinks the system will place a trade."
      },
      {
        step: 5,
        room: "Review Center",
        route: "/ob/review-center",
        tester_goal: "Confirm receipts, proof/demo, and feedback are private review materials.",
        owner_note: "Ask tester whether proof feels private or public.",
        stop_condition: "Stop if tester thinks proof/demo is public-facing."
      },
      {
        step: 6,
        room: "Owner Console",
        route: "/ob/owner-console",
        tester_goal: "Owner reviews source audit, feedback queue, launch status, and session notes.",
        owner_note: "Owner-only unless tester has clearance.",
        stop_condition: "Stop if owner controls are visible to a tester without clearance."
      }
    ];
  }

  function stopConditions() {
    return [
      "Do not continue if tester feels pressured to trade.",
      "Do not continue if tester cannot identify Live Auto Locked.",
      "Do not continue if tester thinks OB has broker API access.",
      "Do not continue if tester thinks proof/demo/receipts are public.",
      "Do not continue if tester cannot tell fresh/stale/fallback labels apart.",
      "Do not continue if owner-only controls appear to normal tester.",
      "Do not continue if any safety issue or blocker feedback appears."
    ];
  }

  function buildFallbackPayload() {
    const queue = queuePayload();
    const steps = sessionSteps();
    return {
      version: VERSION,
      source: "v41_safe_session_runbook_fallback",
      runbook_status: "fallback",
      session_label: "Guided private beta session",
      steps,
      stop_conditions: stopConditions(),
      owner_opening_script: [
        "You are testing clarity and safety, not trading.",
        "Tell me immediately if anything feels like a trading instruction.",
        "Tell me immediately if you cannot tell whether data is fresh, stale, guarded, or fallback.",
        "Do not screenshot, share, export, or invite anyone."
      ],
      owner_closeout_questions: [
        "What did you think OB wanted you to do first?",
        "Which room confused you most?",
        "Did anything feel like pressure to trade?",
        "Could you find Tower state and Live Auto Locked?",
        "Did proof/demo feel private?",
        "What should be fixed before another tester?"
      ],
      runbook_summary: {
        total_steps: steps.length,
        stop_conditions: stopConditions().length,
        owner_notes: steps.length,
        queue_blockers: (queue.summary || {}).blocker || 0,
        queue_high: (queue.summary || {}).high || 0
      },
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        guided_session_only: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        session_runbook_does_not_create_permission: true
      },
      warnings: [
        "Runbook is private and owner-guided.",
        "Stop if tester is confused about execution boundaries.",
        "No public launch.",
        "No broker wiring.",
        "No execution permission changed."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};
    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      runbook_status: safe.runbook_status || "normalized",
      session_label: safe.session_label || fallback.session_label,
      steps: Array.isArray(safe.steps) ? safe.steps : fallback.steps,
      stop_conditions: Array.isArray(safe.stop_conditions) ? safe.stop_conditions : fallback.stop_conditions,
      owner_opening_script: Array.isArray(safe.owner_opening_script) ? safe.owner_opening_script : fallback.owner_opening_script,
      owner_closeout_questions: Array.isArray(safe.owner_closeout_questions) ? safe.owner_closeout_questions : fallback.owner_closeout_questions,
      runbook_summary: { ...(fallback.runbook_summary || {}), ...(safe.runbook_summary || {}) },
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        guided_session_only: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        session_runbook_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRIVATE_BETA_SESSION_RUNBOOK_V41 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_session_runbook_v41: normalized,
      guided_private_beta_session_path: normalized.steps
    };
    window.dispatchEvent(new CustomEvent("obPrivateBetaSessionRunbookUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchRunbook() {
    runbookState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, { credentials: "same-origin", headers: { "Accept": "application/json" } });
      runbookState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        runbookState.status = "ready";
        runbookState.source = normalized.source || "session_runbook_snapshot";
        runbookState.payload = normalized;
        runbookState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        runbookState.status = "guarded_fallback";
        runbookState.source = "guarded_session_runbook_fallback";
        runbookState.payload = fallback;
        runbookState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      runbookState.status = "error_fallback";
      runbookState.source = "fetch_error_fallback";
      runbookState.payload = fallback;
      runbookState.fallbackActive = true;
      runbookState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    return runbookState;
  }

  function card(label, value) {
    return `<div class="ob-beta-session-runbook-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function stepRow(item) {
    return `
      <div class="ob-beta-session-runbook-row">
        <div class="ob-beta-session-runbook-dot">${safeText(item.step, "•")}</div>
        <div>
          <strong>${safeText(item.room, "Room")}</strong>
          <span>${safeText(item.route, "/ob")}</span>
        </div>
        <span>${safeText(item.tester_goal, "Tester observes this room.")}<br>${safeText(item.owner_note, "")}</span>
        <div class="ob-beta-session-runbook-status gold">guided</div>
      </div>
    `;
  }

  function stopRow(item, index) {
    return `
      <div class="ob-beta-session-runbook-row">
        <div class="ob-beta-session-runbook-dot">!</div>
        <div>
          <strong>Stop condition ${index + 1}</strong>
          <span>do not continue if confused</span>
        </div>
        <span>${safeText(item, "Stop condition.")}</span>
        <div class="ob-beta-session-runbook-status red">stop</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = runbookState.payload || buildFallbackPayload();
    const summary = payload.runbook_summary || {};
    const steps = Array.isArray(payload.steps) ? payload.steps : [];
    const stops = Array.isArray(payload.stop_conditions) ? payload.stop_conditions : [];

    return `
      <div class="ob-beta-session-runbook-panel" id="obPrivateBetaSessionRunbookPanel" data-ob-v41-session-runbook="true">
        <div class="ob-beta-session-runbook-head">
          <div>
            <div class="ob-label">Guided Private Beta Session Runbook · V41</div>
            <div class="ob-beta-session-runbook-title">Step-by-step tester session path</div>
            <div class="ob-beta-session-runbook-subtitle">${safeText(payload.session_label, "Guided private beta session")} · ${safeText(runbookState.status, "booting")} · owner-guided, private, and stop-rule protected.</div>
          </div>
          <div class="ob-beta-session-runbook-chip-row">
            <span class="ob-beta-session-runbook-chip green">Guided session</span>
            <span class="ob-beta-session-runbook-chip gold">Stop rules</span>
            <span class="ob-beta-session-runbook-chip red">No broker wiring</span>
          </div>
        </div>

        <div class="ob-beta-session-runbook-grid">
          ${card("Steps", safeText(summary.total_steps, steps.length))}
          ${card("Stops", safeText(summary.stop_conditions, stops.length))}
          ${card("Owner notes", safeText(summary.owner_notes, steps.length))}
          ${card("Path", "5 rooms")}
          ${card("Manual Live", "locked")}
          ${card("Proof", "private")}
          ${card("Public", "no")}
        </div>

        <div class="ob-beta-session-runbook-section">
          <div class="ob-beta-session-runbook-section-title">Session path</div>
          <div class="ob-beta-session-runbook-list">${steps.map(stepRow).join("")}</div>
        </div>

        <div class="ob-beta-session-runbook-section">
          <div class="ob-beta-session-runbook-section-title">Stop conditions</div>
          <div class="ob-beta-session-runbook-list">${stops.map(stopRow).join("")}</div>
        </div>

        <div class="ob-beta-session-runbook-callout">
          <strong>Owner opening script</strong><br>
          ${(payload.owner_opening_script || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-session-runbook-note"><strong>Soulaana:</strong><br>A beta session is not a tour for hype. It is a controlled walk through confusion, trust, safety, and clarity.</div>
        <div class="ob-beta-session-runbook-boundary"><strong>Boundary:</strong><br>Private guided session only. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaSessionRunbookPanel");
    if (existing) existing.remove();
    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const queue = document.getElementById("obPrivateBetaFeedbackReviewQueuePanel");
    const feedback = document.getElementById("obPrivateBetaFeedbackIntakePanel");
    const invite = document.getElementById("obPrivateBetaInvitePacketPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (queue && queue.parentNode) queue.insertAdjacentElement("afterend", panel);
    else if (feedback && feedback.parentNode) feedback.insertAdjacentElement("afterend", panel);
    else if (invite && invite.parentNode) invite.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = runbookState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v41-session-runbook", "ready");
    window.OB_V41_PRIVATE_BETA_SESSION_RUNBOOK_STATE = {
      version: VERSION,
      status: runbookState.status,
      fallbackActive: runbookState.fallbackActive,
      runbookStatus: payload.runbook_status,
      guidedSessionOnly: true,
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
      fetchRunbook();
    }, 2220);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaFeedbackReviewQueueUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_SESSION_RUNBOOK_V41_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return runbookState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchRunbook,
    renderPanel,
    setFlags
  };
})();
