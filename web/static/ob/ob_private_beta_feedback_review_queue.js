// OBSERVATORY_V40_OWNER_TESTER_FEEDBACK_REVIEW_QUEUE_JS

(function () {
  const VERSION = "OB_V40_OWNER_TESTER_FEEDBACK_REVIEW_QUEUE";
  const ENDPOINT = "/ob/private-beta-feedback-review-queue.json";

  // V40 SMOKE MARKERS
  // Owner Tester Feedback Review Queue
  // owner-facing queue for tester submissions
  // severity labels
  // clarity trust bug UI safety source-feed Manual Live labels
  // reviewed needs-fix accepted rejected statuses
  // owner follow-up actions
  // private feedback review
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let queueState = {
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

  function intakePayload() {
    if (window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39_API && window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39_API.getState) {
      const state = window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39_API.getState();
      if (state && state.payload) return state.payload;
    }
    if (window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39) return window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39;

    return {
      feedback_records: [
        { id: "FB-INTAKE-001", type: "confusion", room: "Dashboard", severity: "medium", prompt: "What did you think OB wanted you to do first?", owner_review: "required" },
        { id: "FB-INTAKE-002", type: "pressure_to_trade", room: "Trade Center", severity: "high", prompt: "Did anything feel like pressure to trade instead of review?", owner_review: "required" },
        { id: "FB-INTAKE-003", type: "source_feed", room: "Market Map", severity: "high", prompt: "Could you tell whether data was snapshot, stale, guarded, or fallback?", owner_review: "required" },
        { id: "FB-INTAKE-004", type: "safety_issue", room: "Trade Center", severity: "blocker", prompt: "Could you find Tower state, Live Auto Locked, and no-execution boundaries?", owner_review: "required" },
        { id: "FB-INTAKE-005", type: "room_issue", room: "All Rooms", severity: "medium", prompt: "Which room confused you most?", owner_review: "required" },
        { id: "FB-INTAKE-006", type: "bug", room: "All Rooms", severity: "medium", prompt: "What felt broken, crowded, slow, or hard to trust?", owner_review: "required" }
      ]
    };
  }

  function labelForType(type) {
    const map = {
      confusion: "clarity",
      pressure_to_trade: "safety",
      bug: "bug/UI",
      trust_issue: "trust",
      room_issue: "UI",
      source_feed: "source-feed",
      safety_issue: "safety/Manual Live"
    };
    return map[type] || "review";
  }

  function actionForRecord(record) {
    const type = safeText(record.type, "review");
    if (type === "pressure_to_trade") return "Strengthen review-only language before next tester.";
    if (type === "safety_issue") return "Pause tester expansion until safety wording and Tower boundaries are verified.";
    if (type === "source_feed") return "Run V36 source audit and refresh stale/fallback feed labels.";
    if (type === "bug") return "Patch UI bug and rerun room render checks.";
    if (type === "room_issue") return "Assign to room polish queue.";
    if (type === "trust_issue") return "Audit trust labels and source mapping.";
    return "Rewrite guidance or add clarification.";
  }

  function normalizeRecord(record, index) {
    return {
      id: safeText(record.id, "FB-QUEUE-" + String(index + 1).padStart(3, "0")),
      type: safeText(record.type, "review"),
      room: safeText(record.room, "All Rooms"),
      severity: safeText(record.severity, "medium"),
      label: labelForType(record.type),
      prompt: safeText(record.prompt, "Private tester feedback requires owner review."),
      status: record.severity === "blocker" ? "needs-fix" : "reviewed-pending",
      allowed_statuses: ["reviewed", "needs-fix", "accepted", "rejected"],
      owner_action: actionForRecord(record),
      private: true
    };
  }

  function buildFallbackPayload() {
    const intake = intakePayload();
    const records = (intake.feedback_records || []).map(normalizeRecord);
    const blocker = records.filter(item => item.severity === "blocker").length;
    const high = records.filter(item => item.severity === "high").length;
    const needsFix = records.filter(item => item.status === "needs-fix").length;

    return {
      version: VERSION,
      source: "v40_safe_feedback_review_queue_fallback",
      queue_status: "fallback",
      review_queue_label: "Owner review required",
      queue_records: records,
      summary: {
        total_records: records.length,
        blocker,
        high,
        needs_fix: needsFix,
        private_records: records.filter(item => item.private).length,
        owner_actions: records.length
      },
      severity_labels: ["blocker", "high", "medium", "low", "polish"],
      issue_labels: ["clarity", "trust", "bug", "UI", "safety", "source-feed", "Manual Live"],
      status_labels: ["reviewed", "needs-fix", "accepted", "rejected"],
      owner_follow_up_actions: [
        "Review blocker/high records before inviting another tester.",
        "Route pressure-to-trade and safety issues to immediate fix queue.",
        "Route source-feed issues to V36 source audit.",
        "Route room/UI issues to room polish.",
        "Never convert tester feedback into public proof."
      ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        private_feedback_review: true,
        owner_review_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        feedback_review_does_not_create_permission: true
      },
      warnings: [
        "Feedback review queue is private.",
        "Owner review is required.",
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
      queue_status: safe.queue_status || "normalized",
      review_queue_label: safe.review_queue_label || fallback.review_queue_label,
      queue_records: Array.isArray(safe.queue_records) ? safe.queue_records : fallback.queue_records,
      summary: { ...(fallback.summary || {}), ...(safe.summary || {}) },
      severity_labels: Array.isArray(safe.severity_labels) ? safe.severity_labels : fallback.severity_labels,
      issue_labels: Array.isArray(safe.issue_labels) ? safe.issue_labels : fallback.issue_labels,
      status_labels: Array.isArray(safe.status_labels) ? safe.status_labels : fallback.status_labels,
      owner_follow_up_actions: Array.isArray(safe.owner_follow_up_actions) ? safe.owner_follow_up_actions : fallback.owner_follow_up_actions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        private_feedback_review: true,
        owner_review_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        feedback_review_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_feedback_review_queue_v40: normalized,
      owner_feedback_review_queue: normalized.queue_records
    };
    window.dispatchEvent(new CustomEvent("obPrivateBetaFeedbackReviewQueueUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchReviewQueue() {
    queueState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, { credentials: "same-origin", headers: { "Accept": "application/json" } });
      queueState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        queueState.status = "ready";
        queueState.source = normalized.source || "feedback_review_queue_snapshot";
        queueState.payload = normalized;
        queueState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        queueState.status = "guarded_fallback";
        queueState.source = "guarded_feedback_review_queue_fallback";
        queueState.payload = fallback;
        queueState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      queueState.status = "error_fallback";
      queueState.source = "fetch_error_fallback";
      queueState.payload = fallback;
      queueState.fallbackActive = true;
      queueState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    return queueState;
  }

  function severityClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocker") || text.includes("high") || text.includes("safety")) return "red";
    if (text.includes("medium") || text.includes("needs")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-review-queue-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function recordRow(item, index) {
    return `
      <div class="ob-beta-review-queue-row">
        <div class="ob-beta-review-queue-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.id, "FB")}</strong>
          <span>${safeText(item.room, "Room")} · ${safeText(item.label, "review")}</span>
        </div>
        <span>${safeText(item.prompt, "Private tester feedback.")}<br>${safeText(item.owner_action, "")}</span>
        <div class="ob-beta-review-queue-status ${severityClass(item.severity)}">${safeText(item.status, "review")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = queueState.payload || buildFallbackPayload();
    const summary = payload.summary || {};
    const records = Array.isArray(payload.queue_records) ? payload.queue_records : [];

    return `
      <div class="ob-beta-review-queue-panel" id="obPrivateBetaFeedbackReviewQueuePanel" data-ob-v40-feedback-review-queue="true">
        <div class="ob-beta-review-queue-head">
          <div>
            <div class="ob-label">Owner Feedback Review Queue · V40</div>
            <div class="ob-beta-review-queue-title">Tester feedback review queue</div>
            <div class="ob-beta-review-queue-subtitle">${safeText(payload.review_queue_label, "Owner review required")} · ${safeText(queueState.status, "booting")} · private tester feedback becomes owner actions.</div>
          </div>
          <div class="ob-beta-review-queue-chip-row">
            <span class="ob-beta-review-queue-chip gold">Owner review</span>
            <span class="ob-beta-review-queue-chip green">Private queue</span>
            <span class="ob-beta-review-queue-chip red">No public proof</span>
          </div>
        </div>

        <div class="ob-beta-review-queue-grid">
          ${card("Records", safeText(summary.total_records, records.length))}
          ${card("Blocker", safeText(summary.blocker, "0"))}
          ${card("High", safeText(summary.high, "0"))}
          ${card("Needs fix", safeText(summary.needs_fix, "0"))}
          ${card("Private", safeText(summary.private_records, records.length))}
          ${card("Labels", safeText((payload.issue_labels || []).length, "7"))}
          ${card("Statuses", safeText((payload.status_labels || []).length, "4"))}
        </div>

        <div class="ob-beta-review-queue-section">
          <div class="ob-beta-review-queue-section-title">Review records</div>
          <div class="ob-beta-review-queue-list">${records.map(recordRow).join("")}</div>
        </div>

        <div class="ob-beta-review-queue-callout">
          <strong>Owner follow-up actions</strong><br>
          ${(payload.owner_follow_up_actions || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-review-queue-note"><strong>Soulaana:</strong><br>Feedback is not noise. It is a map of where the beta still feels unclear, unsafe, broken, or hard to trust.</div>
        <div class="ob-beta-review-queue-boundary"><strong>Boundary:</strong><br>Private feedback review only. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaFeedbackReviewQueuePanel");
    if (existing) existing.remove();
    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const feedback = document.getElementById("obPrivateBetaFeedbackIntakePanel");
    const invite = document.getElementById("obPrivateBetaInvitePacketPanel");
    const launch = document.getElementById("obPrivateBetaLaunchControlPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (feedback && feedback.parentNode) feedback.insertAdjacentElement("afterend", panel);
    else if (invite && invite.parentNode) invite.insertAdjacentElement("afterend", panel);
    else if (launch && launch.parentNode) launch.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = queueState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v40-feedback-review-queue", "ready");
    window.OB_V40_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_STATE = {
      version: VERSION,
      status: queueState.status,
      fallbackActive: queueState.fallbackActive,
      queueStatus: payload.queue_status,
      ownerReviewRequired: true,
      privateFeedbackReview: true,
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
      fetchReviewQueue();
    }, 2100);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaFeedbackIntakeUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_V40_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return queueState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchReviewQueue,
    renderPanel,
    setFlags
  };
})();
