// OBSERVATORY_V42_PRIVATE_BETA_ISSUE_TRIAGE_FIX_PRIORITY_JS

(function () {
  const VERSION = "OB_V42_PRIVATE_BETA_ISSUE_TRIAGE_FIX_PRIORITY";
  const ENDPOINT = "/ob/private-beta-issue-triage.json";

  // V42 SMOKE MARKERS
  // Private Beta Issue Triage
  // Fix Priority
  // feedback into fix priorities
  // blocker high medium low polish labels
  // UI issue
  // safety issue
  // data issue
  // wording issue
  // owner decides must-fix before next tester
  // issue triage does not create permission
  // private beta only
  // no public proof
  // no public launch
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let triageState = {
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

  function reviewQueuePayload() {
    if (window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API && window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API.getState) {
      const state = window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40) return window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40;

    return {
      queue_records: [
        {
          id: "FB-QUEUE-001",
          type: "confusion",
          room: "Dashboard",
          severity: "medium",
          label: "clarity",
          prompt: "What did you think OB wanted you to do first?",
          status: "reviewed-pending",
          owner_action: "Rewrite guidance or add clarification.",
          private: true
        },
        {
          id: "FB-QUEUE-002",
          type: "pressure_to_trade",
          room: "Trade Center",
          severity: "high",
          label: "safety",
          prompt: "Did anything feel like pressure to trade instead of review?",
          status: "needs-fix",
          owner_action: "Strengthen review-only language before next tester.",
          private: true
        },
        {
          id: "FB-QUEUE-003",
          type: "source_feed",
          room: "Market Map",
          severity: "high",
          label: "source-feed",
          prompt: "Could you tell whether data was snapshot, stale, guarded, or fallback?",
          status: "needs-fix",
          owner_action: "Run V36 source audit and refresh stale/fallback feed labels.",
          private: true
        },
        {
          id: "FB-QUEUE-004",
          type: "safety_issue",
          room: "Trade Center",
          severity: "blocker",
          label: "safety/Manual Live",
          prompt: "Could you find Tower state, Live Auto Locked, and no-execution boundaries?",
          status: "needs-fix",
          owner_action: "Pause tester expansion until safety wording and Tower boundaries are verified.",
          private: true
        }
      ],
      summary: {
        blocker: 1,
        high: 2,
        needs_fix: 3
      }
    };
  }

  function priorityFor(record) {
    const severity = safeText(record.severity, "").toLowerCase();
    const label = safeText(record.label, "").toLowerCase();
    const type = safeText(record.type, "").toLowerCase();

    if (severity.includes("blocker") || type.includes("safety_issue")) return "blocker";
    if (severity.includes("high") || label.includes("safety") || label.includes("source-feed")) return "high";
    if (severity.includes("medium") || label.includes("clarity") || label.includes("ui")) return "medium";
    if (severity.includes("polish")) return "polish";
    return "low";
  }

  function issueTypeFor(record) {
    const label = safeText(record.label, "").toLowerCase();
    const type = safeText(record.type, "").toLowerCase();

    if (label.includes("safety") || type.includes("pressure") || type.includes("safety")) return "safety issue";
    if (label.includes("source") || type.includes("source")) return "data issue";
    if (label.includes("bug") || label.includes("ui") || type.includes("bug") || type.includes("room")) return "UI issue";
    if (label.includes("clarity") || type.includes("confusion")) return "wording issue";
    if (label.includes("trust")) return "trust issue";
    return "review issue";
  }

  function mustFix(record) {
    const priority = priorityFor(record);
    return priority === "blocker" || priority === "high";
  }

  function normalizeIssue(record, index) {
    const priority = priorityFor(record);
    const issueType = issueTypeFor(record);

    return {
      id: "TRIAGE-" + safeText(record.id, String(index + 1)).replace(/[^A-Z0-9-]/gi, "").toUpperCase(),
      feedback_id: safeText(record.id, "FB-" + (index + 1)),
      room: safeText(record.room, "All Rooms"),
      issue_type: issueType,
      priority,
      must_fix_before_next_tester: mustFix(record),
      summary: safeText(record.prompt, "Private beta feedback issue requires triage."),
      owner_action: safeText(record.owner_action, "Owner decides whether this must be fixed before next tester."),
      decision_status: mustFix(record) ? "must-fix" : "owner-decision",
      private: true
    };
  }

  function buildFallbackPayload() {
    const queue = reviewQueuePayload();
    const issues = (queue.queue_records || []).map(normalizeIssue);
    const blocker = issues.filter(item => item.priority === "blocker").length;
    const high = issues.filter(item => item.priority === "high").length;
    const medium = issues.filter(item => item.priority === "medium").length;
    const mustFixCount = issues.filter(item => item.must_fix_before_next_tester).length;

    let nextTesterStatus = "GO";
    if (blocker > 0) nextTesterStatus = "NO-GO";
    else if (high > 0 || mustFixCount > 0) nextTesterStatus = "CONDITIONAL GO";

    return {
      version: VERSION,
      source: "v42_safe_issue_triage_fallback",
      triage_status: "fallback",
      next_tester_status: nextTesterStatus,
      issues,
      summary: {
        total_issues: issues.length,
        blocker,
        high,
        medium,
        low: issues.filter(item => item.priority === "low").length,
        polish: issues.filter(item => item.priority === "polish").length,
        must_fix_before_next_tester: mustFixCount
      },
      priority_labels: ["blocker", "high", "medium", "low", "polish"],
      issue_type_labels: ["UI issue", "safety issue", "data issue", "wording issue", "trust issue"],
      owner_decision_rules: [
        "Blocker issues make the next tester no-go.",
        "High safety/source-feed issues require owner decision before next tester.",
        "Medium clarity/UI issues can be conditional if clearly labeled.",
        "No issue may remove Tower, NDA, private beta, or no-execution boundaries.",
        "Tester feedback cannot become public proof."
      ],
      must_fix_actions: issues.filter(item => item.must_fix_before_next_tester).map(item => item.owner_action),
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        issue_triage_private: true,
        owner_decides_next_tester: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        issue_triage_does_not_create_permission: true
      },
      warnings: [
        "Issue triage is private.",
        "Owner decides must-fix before next tester.",
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
      triage_status: safe.triage_status || "normalized",
      next_tester_status: safe.next_tester_status || fallback.next_tester_status,
      issues: Array.isArray(safe.issues) ? safe.issues : fallback.issues,
      summary: { ...(fallback.summary || {}), ...(safe.summary || {}) },
      priority_labels: Array.isArray(safe.priority_labels) ? safe.priority_labels : fallback.priority_labels,
      issue_type_labels: Array.isArray(safe.issue_type_labels) ? safe.issue_type_labels : fallback.issue_type_labels,
      owner_decision_rules: Array.isArray(safe.owner_decision_rules) ? safe.owner_decision_rules : fallback.owner_decision_rules,
      must_fix_actions: Array.isArray(safe.must_fix_actions) ? safe.must_fix_actions : fallback.must_fix_actions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        issue_triage_private: true,
        owner_decides_next_tester: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        issue_triage_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_issue_triage_v42: normalized,
      private_beta_fix_priorities: normalized.issues
    };
    window.dispatchEvent(new CustomEvent("obPrivateBetaIssueTriageUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchTriage() {
    triageState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, { credentials: "same-origin", headers: { "Accept": "application/json" } });
      triageState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        triageState.status = "ready";
        triageState.source = normalized.source || "issue_triage_snapshot";
        triageState.payload = normalized;
        triageState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        triageState.status = "guarded_fallback";
        triageState.source = "guarded_issue_triage_fallback";
        triageState.payload = fallback;
        triageState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      triageState.status = "error_fallback";
      triageState.source = "fetch_error_fallback";
      triageState.payload = fallback;
      triageState.fallbackActive = true;
      triageState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    return triageState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocker") || text.includes("high") || text.includes("no-go") || text.includes("must")) return "red";
    if (text.includes("medium") || text.includes("conditional") || text.includes("owner")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-issue-triage-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function issueRow(item, index) {
    return `
      <div class="ob-beta-issue-triage-row">
        <div class="ob-beta-issue-triage-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.feedback_id, item.id)}</strong>
          <span>${safeText(item.room, "Room")} · ${safeText(item.issue_type, "issue")}</span>
        </div>
        <span>${safeText(item.summary, "Private beta issue.")}<br>${safeText(item.owner_action, "")}</span>
        <div class="ob-beta-issue-triage-status ${statusClass(item.priority)}">${safeText(item.priority, "review")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = triageState.payload || buildFallbackPayload();
    const summary = payload.summary || {};
    const issues = Array.isArray(payload.issues) ? payload.issues : [];

    return `
      <div class="ob-beta-issue-triage-panel" id="obPrivateBetaIssueTriagePanel" data-ob-v42-issue-triage="true">
        <div class="ob-beta-issue-triage-head">
          <div>
            <div class="ob-label">Private Beta Issue Triage · V42</div>
            <div class="ob-beta-issue-triage-title">Fix Priority</div>
            <div class="ob-beta-issue-triage-subtitle">${safeText(payload.next_tester_status, "Owner decision")} · ${safeText(triageState.status, "booting")} · feedback becomes private fix priorities.</div>
          </div>
          <div class="ob-beta-issue-triage-chip-row">
            <span class="ob-beta-issue-triage-chip ${statusClass(payload.next_tester_status)}">${safeText(payload.next_tester_status, "review")}</span>
            <span class="ob-beta-issue-triage-chip gold">Owner decides</span>
            <span class="ob-beta-issue-triage-chip red">No public proof</span>
          </div>
        </div>

        <div class="ob-beta-issue-triage-grid">
          ${card("Issues", safeText(summary.total_issues, issues.length))}
          ${card("Blocker", safeText(summary.blocker, "0"))}
          ${card("High", safeText(summary.high, "0"))}
          ${card("Medium", safeText(summary.medium, "0"))}
          ${card("Low", safeText(summary.low, "0"))}
          ${card("Polish", safeText(summary.polish, "0"))}
          ${card("Must-fix", safeText(summary.must_fix_before_next_tester, "0"))}
        </div>

        <div class="ob-beta-issue-triage-section">
          <div class="ob-beta-issue-triage-section-title">Triage issues</div>
          <div class="ob-beta-issue-triage-list">${issues.map(issueRow).join("")}</div>
        </div>

        <div class="ob-beta-issue-triage-callout">
          <strong>Owner decision rules</strong><br>
          ${(payload.owner_decision_rules || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-issue-triage-note"><strong>Soulaana:</strong><br>Feedback becomes priorities. Priorities become fixes. Fixes protect the next tester.</div>
        <div class="ob-beta-issue-triage-boundary"><strong>Boundary:</strong><br>Issue triage is private. It cannot create permission. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaIssueTriagePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const runbook = document.getElementById("obPrivateBetaSessionRunbookPanel");
    const queue = document.getElementById("obPrivateBetaFeedbackReviewQueuePanel");
    const feedback = document.getElementById("obPrivateBetaFeedbackIntakePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (runbook && runbook.parentNode) runbook.insertAdjacentElement("afterend", panel);
    else if (queue && queue.parentNode) queue.insertAdjacentElement("afterend", panel);
    else if (feedback && feedback.parentNode) feedback.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = triageState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v42-issue-triage", "ready");
    window.OB_V42_PRIVATE_BETA_ISSUE_TRIAGE_STATE = {
      version: VERSION,
      status: triageState.status,
      fallbackActive: triageState.fallbackActive,
      nextTesterStatus: payload.next_tester_status,
      issueTriagePrivate: true,
      ownerDecidesNextTester: true,
      noPublicProof: true,
      noPublicLaunch: true,
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
      fetchTriage();
    }, 2340);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaFeedbackReviewQueueUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return triageState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchTriage,
    renderPanel,
    setFlags
  };
})();
