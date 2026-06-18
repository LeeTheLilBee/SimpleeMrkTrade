// OBSERVATORY_V43_PRIVATE_BETA_SESSION_CLOSEOUT_REPORT_JS

(function () {
  const VERSION = "OB_V43_PRIVATE_BETA_SESSION_CLOSEOUT_REPORT";
  const ENDPOINT = "/ob/private-beta-session-closeout.json";

  // V43 SMOKE MARKERS
  // Private Beta Session Closeout Report
  // tester session outcome
  // go conditional go no-go for next tester
  // unresolved issues
  // session outcome summary
  // next tester decision
  // confirms no public launch
  // confirms no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let closeoutState = {
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

  function triagePayload() {
    if (window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API && window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API.getState) {
      const state = window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42) return window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42;

    return {
      next_tester_status: "NO-GO",
      summary: {
        total_issues: 4,
        blocker: 1,
        high: 2,
        must_fix_before_next_tester: 3
      },
      issues: [
        {
          id: "TRIAGE-FB-QUEUE-004",
          feedback_id: "FB-QUEUE-004",
          room: "Trade Center",
          issue_type: "safety issue",
          priority: "blocker",
          must_fix_before_next_tester: true,
          summary: "Tester must find Tower state, Live Auto Locked, and no-execution boundaries.",
          owner_action: "Pause tester expansion until safety wording and Tower boundaries are verified."
        }
      ]
    };
  }

  function buildFallbackPayload() {
    const triage = triagePayload();
    const summary = triage.summary || {};
    const issues = Array.isArray(triage.issues) ? triage.issues : [];

    let finalDecision = safeText(triage.next_tester_status, "CONDITIONAL GO");
    if (Number(summary.blocker || 0) > 0) finalDecision = "NO-GO";
    else if (Number(summary.high || 0) > 0 || Number(summary.must_fix_before_next_tester || 0) > 0) finalDecision = "CONDITIONAL GO";
    else finalDecision = "GO";

    const unresolved = issues.filter(item => item.must_fix_before_next_tester || item.priority === "blocker" || item.priority === "high");

    return {
      version: VERSION,
      source: "v43_safe_session_closeout_fallback",
      closeout_status: "fallback",
      session_outcome: finalDecision,
      next_tester_decision: finalDecision,
      tester_session_result: finalDecision === "GO" ? "ready_for_next_private_tester" : finalDecision === "CONDITIONAL GO" ? "owner_fix_required_before_next_tester" : "stop_next_tester_until_fixed",
      summary: {
        total_issues: Number(summary.total_issues || issues.length),
        unresolved_issues: unresolved.length,
        blocker: Number(summary.blocker || 0),
        high: Number(summary.high || 0),
        must_fix_before_next_tester: Number(summary.must_fix_before_next_tester || 0),
        public_launch: "no",
        broker_wiring: "no",
        auto_execution: "no"
      },
      unresolved_issues: unresolved,
      closeout_sections: [
        {
          title: "Session outcome",
          detail: "Private beta session closes with owner-facing next tester decision.",
          status: finalDecision
        },
        {
          title: "Unresolved issues",
          detail: unresolved.length ? "Unresolved high/blocker issues remain before next tester." : "No high/blocker unresolved issues in fallback closeout.",
          status: unresolved.length ? "needs-owner-review" : "clear"
        },
        {
          title: "Public launch boundary",
          detail: "Closeout confirms this is not public launch and not public proof.",
          status: "confirmed-private"
        },
        {
          title: "Execution boundary",
          detail: "No broker wiring, no broker API, no auto execution, Live Auto Locked.",
          status: "locked"
        }
      ],
      owner_next_actions: finalDecision === "NO-GO"
        ? [
            "Fix blocker issues before another tester.",
            "Re-run V40/V41/V42 after fixes.",
            "Confirm no tester saw broker/API/execution implication.",
            "Do not invite next tester yet."
          ]
        : finalDecision === "CONDITIONAL GO"
          ? [
              "Fix or accept high-priority issues before next tester.",
              "Document owner decision.",
              "Re-run closeout before next tester.",
              "Keep all proof and feedback private."
            ]
          : [
              "Proceed to next private tester only through Tower invite/NDA.",
              "Monitor source labels and feedback intake.",
              "Keep no broker wiring and Live Auto Locked."
            ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        session_closeout_private: true,
        owner_go_no_go_only: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        session_closeout_does_not_create_permission: true
      },
      warnings: [
        "Session closeout is private.",
        "Go/conditional/no-go is for private tester sequencing only.",
        "No public launch.",
        "No public proof.",
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
      closeout_status: safe.closeout_status || "normalized",
      session_outcome: safe.session_outcome || fallback.session_outcome,
      next_tester_decision: safe.next_tester_decision || fallback.next_tester_decision,
      tester_session_result: safe.tester_session_result || fallback.tester_session_result,
      summary: { ...(fallback.summary || {}), ...(safe.summary || {}) },
      unresolved_issues: Array.isArray(safe.unresolved_issues) ? safe.unresolved_issues : fallback.unresolved_issues,
      closeout_sections: Array.isArray(safe.closeout_sections) ? safe.closeout_sections : fallback.closeout_sections,
      owner_next_actions: Array.isArray(safe.owner_next_actions) ? safe.owner_next_actions : fallback.owner_next_actions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        session_closeout_private: true,
        owner_go_no_go_only: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        session_closeout_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_session_closeout_v43: normalized,
      next_private_beta_tester_decision: normalized.next_tester_decision
    };
    window.dispatchEvent(new CustomEvent("obPrivateBetaSessionCloseoutUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchCloseout() {
    closeoutState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, { credentials: "same-origin", headers: { "Accept": "application/json" } });
      closeoutState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        closeoutState.status = "ready";
        closeoutState.source = normalized.source || "session_closeout_snapshot";
        closeoutState.payload = normalized;
        closeoutState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        closeoutState.status = "guarded_fallback";
        closeoutState.source = "guarded_session_closeout_fallback";
        closeoutState.payload = fallback;
        closeoutState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      closeoutState.status = "error_fallback";
      closeoutState.source = "fetch_error_fallback";
      closeoutState.payload = fallback;
      closeoutState.fallbackActive = true;
      closeoutState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    return closeoutState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("no-go") || text.includes("blocker") || text.includes("stop")) return "red";
    if (text.includes("conditional") || text.includes("review") || text.includes("fix")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-session-closeout-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function sectionRow(item, index) {
    return `
      <div class="ob-beta-session-closeout-row">
        <div class="ob-beta-session-closeout-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.title, "Closeout section")}</strong>
          <span>${safeText(item.status, "review")}</span>
        </div>
        <span>${safeText(item.detail, "Private session closeout section.")}</span>
        <div class="ob-beta-session-closeout-status ${statusClass(item.status)}">${safeText(item.status, "review")}</div>
      </div>
    `;
  }

  function issueRow(item, index) {
    return `
      <div class="ob-beta-session-closeout-row">
        <div class="ob-beta-session-closeout-dot">!</div>
        <div>
          <strong>${safeText(item.feedback_id || item.id, "Issue")}</strong>
          <span>${safeText(item.room, "Room")} · ${safeText(item.issue_type, "issue")}</span>
        </div>
        <span>${safeText(item.summary, "Unresolved issue.")}<br>${safeText(item.owner_action, "")}</span>
        <div class="ob-beta-session-closeout-status ${statusClass(item.priority)}">${safeText(item.priority, "review")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = closeoutState.payload || buildFallbackPayload();
    const summary = payload.summary || {};
    const sections = Array.isArray(payload.closeout_sections) ? payload.closeout_sections : [];
    const unresolved = Array.isArray(payload.unresolved_issues) ? payload.unresolved_issues : [];

    return `
      <div class="ob-beta-session-closeout-panel" id="obPrivateBetaSessionCloseoutPanel" data-ob-v43-session-closeout="true">
        <div class="ob-beta-session-closeout-head">
          <div>
            <div class="ob-label">Private Beta Session Closeout · V43</div>
            <div class="ob-beta-session-closeout-title">Session Closeout Report</div>
            <div class="ob-beta-session-closeout-subtitle">${safeText(payload.next_tester_decision, "Owner decision")} · ${safeText(closeoutState.status, "booting")} · private next tester sequencing only.</div>
          </div>
          <div class="ob-beta-session-closeout-chip-row">
            <span class="ob-beta-session-closeout-chip ${statusClass(payload.next_tester_decision)}">${safeText(payload.next_tester_decision, "review")}</span>
            <span class="ob-beta-session-closeout-chip gold">Private closeout</span>
            <span class="ob-beta-session-closeout-chip red">No public launch</span>
          </div>
        </div>

        <div class="ob-beta-session-closeout-grid">
          ${card("Outcome", safeText(payload.session_outcome, "review"))}
          ${card("Unresolved", safeText(summary.unresolved_issues, unresolved.length))}
          ${card("Blocker", safeText(summary.blocker, "0"))}
          ${card("High", safeText(summary.high, "0"))}
          ${card("Must-fix", safeText(summary.must_fix_before_next_tester, "0"))}
          ${card("Public", safeText(summary.public_launch, "no"))}
          ${card("Broker", safeText(summary.broker_wiring, "no"))}
        </div>

        <div class="ob-beta-session-closeout-section">
          <div class="ob-beta-session-closeout-section-title">Closeout sections</div>
          <div class="ob-beta-session-closeout-list">${sections.map(sectionRow).join("")}</div>
        </div>

        <div class="ob-beta-session-closeout-section">
          <div class="ob-beta-session-closeout-section-title">Unresolved issues</div>
          <div class="ob-beta-session-closeout-list">
            ${unresolved.length ? unresolved.map(issueRow).join("") : `
              <div class="ob-beta-session-closeout-row">
                <div class="ob-beta-session-closeout-dot">✓</div>
                <div><strong>No unresolved high/blocker issues</strong><span>private closeout</span></div>
                <span>No unresolved high/blocker issues are listed in the current closeout payload.</span>
                <div class="ob-beta-session-closeout-status green">clear</div>
              </div>
            `}
          </div>
        </div>

        <div class="ob-beta-session-closeout-callout">
          <strong>Owner next actions</strong><br>
          ${(payload.owner_next_actions || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-session-closeout-note"><strong>Soulaana:</strong><br>Closeout decides the next door: go, conditional go, or no-go. Private only. Clean only. Protected only.</div>
        <div class="ob-beta-session-closeout-boundary"><strong>Boundary:</strong><br>Session closeout is private. It does not create permission. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaSessionCloseoutPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const triage = document.getElementById("obPrivateBetaIssueTriagePanel");
    const runbook = document.getElementById("obPrivateBetaSessionRunbookPanel");
    const queue = document.getElementById("obPrivateBetaFeedbackReviewQueuePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (triage && triage.parentNode) triage.insertAdjacentElement("afterend", panel);
    else if (runbook && runbook.parentNode) runbook.insertAdjacentElement("afterend", panel);
    else if (queue && queue.parentNode) queue.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = closeoutState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v43-session-closeout", "ready");
    window.OB_V43_PRIVATE_BETA_SESSION_CLOSEOUT_STATE = {
      version: VERSION,
      status: closeoutState.status,
      fallbackActive: closeoutState.fallbackActive,
      nextTesterDecision: payload.next_tester_decision,
      privateCloseout: true,
      ownerGoNoGoOnly: true,
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
      fetchCloseout();
    }, 2460);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaIssueTriageUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_SESSION_CLOSEOUT_V43_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return closeoutState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchCloseout,
    renderPanel,
    setFlags
  };
})();
