// OBSERVATORY_V39_TESTER_FEEDBACK_INTAKE_CONFUSION_REPORT_PACKET_JS

(function () {
  const VERSION = "OB_V39_TESTER_FEEDBACK_INTAKE_CONFUSION_REPORT_PACKET";
  const ENDPOINT = "/ob/private-beta-feedback-intake.json";

  // V39 SMOKE MARKERS
  // Tester Feedback Intake
  // Confusion Report Packet
  // private tester feedback records
  // confusion report
  // pressure-to-trade concern
  // bug report
  // trust issue
  // room issue
  // source-feed issue
  // safety issue
  // feedback stays private
  // owner review required
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let feedbackState = {
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

  function invitePacketPayload() {
    if (window.OB_PRIVATE_BETA_INVITE_PACKET_V38_API && window.OB_PRIVATE_BETA_INVITE_PACKET_V38_API.getState) {
      const state = window.OB_PRIVATE_BETA_INVITE_PACKET_V38_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_INVITE_PACKET_V38) return window.OB_PRIVATE_BETA_INVITE_PACKET_V38;

    return {
      invite_status: "owner_review_required",
      nda_status: "required_before_access",
      feedback_requirements: [
        { id: "feedback_1", question: "What did you think OB wanted you to do first?", required: true },
        { id: "feedback_2", question: "Did anything feel like pressure to trade instead of review?", required: true },
        { id: "feedback_3", question: "Could you tell whether data was snapshot, stale, guarded, or fallback?", required: true },
        { id: "feedback_4", question: "Could you find Tower state, Live Auto Locked, and no-execution boundaries?", required: true },
        { id: "feedback_5", question: "Which room confused you most?", required: true },
        { id: "feedback_6", question: "What felt broken, crowded, slow, or hard to trust?", required: true }
      ],
      rooms_to_visit: [
        { room: "Dashboard" },
        { room: "Market Map" },
        { room: "Symbol Page" },
        { room: "Trade Center" },
        { room: "Review Center" },
        { room: "Owner Console" }
      ]
    };
  }

  function categories() {
    return [
      {
        id: "confusion",
        label: "Confusion report",
        severity: "medium",
        description: "Tester did not understand what to do, what the room meant, or what a label meant.",
        owner_action: "Rewrite copy, add guidance, simplify flow, or add room-level explanation."
      },
      {
        id: "pressure_to_trade",
        label: "Pressure-to-trade concern",
        severity: "high",
        description: "Tester felt pushed toward trading instead of reviewing.",
        owner_action: "Strengthen review-only language and remove pressure wording."
      },
      {
        id: "bug",
        label: "Bug report",
        severity: "medium",
        description: "Tester found broken UI, missing panel, bad route, bad render, or confusing state.",
        owner_action: "Patch bug and rerun room render checks."
      },
      {
        id: "trust_issue",
        label: "Trust issue",
        severity: "high",
        description: "Tester did not trust data source, freshness label, candidate card, or safety boundary.",
        owner_action: "Check source audit, trust labels, and room mapping."
      },
      {
        id: "room_issue",
        label: "Room issue",
        severity: "medium",
        description: "Tester had a room-specific issue with Dashboard, Market Map, Symbol Page, Trade Center, Review Center, or Owner Console.",
        owner_action: "Assign issue to room owner queue."
      },
      {
        id: "source_feed",
        label: "Source-feed issue",
        severity: "high",
        description: "Tester saw stale, missing, guarded, fallback-only, or unclear feed data.",
        owner_action: "Run V36 source audit and regenerate data before tester reliance."
      },
      {
        id: "safety_issue",
        label: "Safety issue",
        severity: "blocker",
        description: "Tester saw public proof risk, broker/API implication, execution confusion, NDA concern, or Tower boundary confusion.",
        owner_action: "Stop beta expansion until fixed."
      }
    ];
  }

  function starterRecords() {
    return [
      {
        id: "FB-INTAKE-001",
        type: "confusion",
        room: "Dashboard",
        severity: "medium",
        prompt: "What did you think OB wanted you to do first?",
        status: "private_intake",
        owner_review: "required",
        private: true
      },
      {
        id: "FB-INTAKE-002",
        type: "pressure_to_trade",
        room: "Trade Center",
        severity: "high",
        prompt: "Did anything feel like pressure to trade instead of review?",
        status: "private_intake",
        owner_review: "required",
        private: true
      },
      {
        id: "FB-INTAKE-003",
        type: "source_feed",
        room: "Market Map",
        severity: "high",
        prompt: "Could you tell whether data was snapshot, stale, guarded, or fallback?",
        status: "private_intake",
        owner_review: "required",
        private: true
      },
      {
        id: "FB-INTAKE-004",
        type: "safety_issue",
        room: "Trade Center",
        severity: "blocker",
        prompt: "Could you find Tower state, Live Auto Locked, and no-execution boundaries?",
        status: "private_intake",
        owner_review: "required",
        private: true
      },
      {
        id: "FB-INTAKE-005",
        type: "room_issue",
        room: "All Rooms",
        severity: "medium",
        prompt: "Which room confused you most?",
        status: "private_intake",
        owner_review: "required",
        private: true
      },
      {
        id: "FB-INTAKE-006",
        type: "bug",
        room: "All Rooms",
        severity: "medium",
        prompt: "What felt broken, crowded, slow, or hard to trust?",
        status: "private_intake",
        owner_review: "required",
        private: true
      }
    ];
  }

  function buildFallbackPayload() {
    const invite = invitePacketPayload();
    const feedbackQuestions = Array.isArray(invite.feedback_requirements) ? invite.feedback_requirements : [];
    const rooms = Array.isArray(invite.rooms_to_visit) ? invite.rooms_to_visit : [];
    const records = starterRecords();

    return {
      version: VERSION,
      source: "v39_safe_feedback_intake_fallback",
      intake_status: "fallback",
      feedback_packet_status: "private_owner_review",
      invite_status: invite.invite_status || "owner_review_required",
      nda_status: invite.nda_status || "required_before_access",
      categories: categories(),
      feedback_records: records,
      feedback_questions: feedbackQuestions,
      rooms_available: rooms.map(item => safeText(item.room, "Room")),
      intake_summary: {
        total_categories: categories().length,
        total_records: records.length,
        required_questions: feedbackQuestions.length || 6,
        private_records: records.filter(item => item.private).length,
        owner_review_required: records.filter(item => item.owner_review === "required").length,
        blocker_categories: categories().filter(item => item.severity === "blocker").length,
        high_categories: categories().filter(item => item.severity === "high").length
      },
      report_packet: {
        confusion_report: true,
        pressure_to_trade_concern: true,
        bug_report: true,
        trust_issue: true,
        room_issue: true,
        source_feed_issue: true,
        safety_issue: true,
        private_feedback_records: true,
        owner_review_required: true
      },
      owner_instructions: [
        "Read every tester feedback record before inviting another tester.",
        "Treat pressure-to-trade and safety issues as high/blocker priority.",
        "Do not turn tester feedback into public proof.",
        "Do not change execution permissions because of feedback.",
        "Route bugs and room issues into the owner review queue."
      ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        feedback_stays_private: true,
        owner_review_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        feedback_intake_does_not_create_permission: true
      },
      warnings: [
        "Feedback intake is private.",
        "Feedback does not grant access.",
        "Feedback does not create execution permission.",
        "No public proof.",
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
      intake_status: safe.intake_status || "normalized",
      feedback_packet_status: safe.feedback_packet_status || fallback.feedback_packet_status,
      invite_status: safe.invite_status || fallback.invite_status,
      nda_status: safe.nda_status || fallback.nda_status,
      categories: Array.isArray(safe.categories) ? safe.categories : fallback.categories,
      feedback_records: Array.isArray(safe.feedback_records) ? safe.feedback_records : fallback.feedback_records,
      feedback_questions: Array.isArray(safe.feedback_questions) ? safe.feedback_questions : fallback.feedback_questions,
      rooms_available: Array.isArray(safe.rooms_available) ? safe.rooms_available : fallback.rooms_available,
      intake_summary: {
        ...(fallback.intake_summary || {}),
        ...(safe.intake_summary || {})
      },
      report_packet: {
        ...(fallback.report_packet || {}),
        ...(safe.report_packet || {})
      },
      owner_instructions: Array.isArray(safe.owner_instructions) ? safe.owner_instructions : fallback.owner_instructions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        feedback_stays_private: true,
        owner_review_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        feedback_intake_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_feedback_intake_v39: normalized,
      private_feedback_records: normalized.feedback_records
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaFeedbackIntakeUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchFeedbackIntake() {
    feedbackState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      feedbackState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        feedbackState.status = "ready";
        feedbackState.source = normalized.source || "feedback_intake_snapshot";
        feedbackState.payload = normalized;
        feedbackState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(buildFallbackPayload());

        feedbackState.status = "guarded_fallback";
        feedbackState.source = "guarded_feedback_intake_route_fallback";
        feedbackState.payload = fallback;
        feedbackState.fallbackActive = true;
        feedbackState.error = "Feedback intake route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(buildFallbackPayload());

        feedbackState.status = "http_fallback";
        feedbackState.source = "http_" + response.status + "_fallback";
        feedbackState.payload = fallback;
        feedbackState.fallbackActive = true;
        feedbackState.error = "Feedback intake route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());

      feedbackState.status = "error_fallback";
      feedbackState.source = "fetch_error_fallback";
      feedbackState.payload = fallback;
      feedbackState.fallbackActive = true;
      feedbackState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return feedbackState;
  }

  function severityClass(value) {
    const text = safeText(value, "").toLowerCase();

    if (text.includes("blocker") || text.includes("high") || text.includes("safety")) return "red";
    if (text.includes("medium") || text.includes("review")) return "gold";
    if (text.includes("low") || text.includes("private")) return "green";
    return "aqua";
  }

  function card(label, value) {
    return `
      <div class="ob-beta-feedback-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function categoryRow(item, index) {
    return `
      <div class="ob-beta-feedback-row">
        <div class="ob-beta-feedback-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Feedback category")}</strong>
          <span>${safeText(item.id, "category")}</span>
        </div>
        <span>${safeText(item.description, "Private feedback category.")}<br>${safeText(item.owner_action, "")}</span>
        <div class="ob-beta-feedback-status ${severityClass(item.severity)}">${safeText(item.severity, "review")}</div>
      </div>
    `;
  }

  function recordRow(item, index) {
    return `
      <div class="ob-beta-feedback-row">
        <div class="ob-beta-feedback-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.id, "FB")}</strong>
          <span>${safeText(item.room, "Room")} · ${safeText(item.type, "feedback")}</span>
        </div>
        <span>${safeText(item.prompt, "Private tester feedback prompt.")}</span>
        <div class="ob-beta-feedback-status ${severityClass(item.severity)}">${safeText(item.owner_review, "required")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = feedbackState.payload || buildFallbackPayload();
    const summary = payload.intake_summary || {};
    const categories = Array.isArray(payload.categories) ? payload.categories : [];
    const records = Array.isArray(payload.feedback_records) ? payload.feedback_records : [];

    return `
      <div class="ob-beta-feedback-panel" id="obPrivateBetaFeedbackIntakePanel" data-ob-v39-private-beta-feedback-intake="true">
        <div class="ob-beta-feedback-head">
          <div>
            <div class="ob-label">Private Beta Feedback Intake · V39</div>
            <div class="ob-beta-feedback-title">Confusion Report Packet</div>
            <div class="ob-beta-feedback-subtitle">
              ${safeText(payload.feedback_packet_status, "private owner review")} · ${safeText(feedbackState.status, "booting")} · tester feedback stays private.
            </div>
          </div>

          <div class="ob-beta-feedback-chip-row">
            <span class="ob-beta-feedback-chip gold">Owner review required</span>
            <span class="ob-beta-feedback-chip green">Private records</span>
            <span class="ob-beta-feedback-chip red">No public proof</span>
          </div>
        </div>

        <div class="ob-beta-feedback-grid">
          ${card("Categories", safeText(summary.total_categories, categories.length))}
          ${card("Records", safeText(summary.total_records, records.length))}
          ${card("Questions", safeText(summary.required_questions, "6"))}
          ${card("Private", safeText(summary.private_records, records.length))}
          ${card("Owner review", safeText(summary.owner_review_required, records.length))}
          ${card("High", safeText(summary.high_categories, "0"))}
          ${card("Blocker", safeText(summary.blocker_categories, "0"))}
        </div>

        <div class="ob-beta-feedback-callout">
          <strong>Packet purpose</strong>
          <span>Tester feedback is intake for owner review. It is not public proof, not a testimonial, not access approval, and not permission to trade.</span>
        </div>

        <div class="ob-beta-feedback-section">
          <div class="ob-beta-feedback-section-title">Feedback categories</div>
          <div class="ob-beta-feedback-list">
            ${categories.map(categoryRow).join("")}
          </div>
        </div>

        <div class="ob-beta-feedback-section">
          <div class="ob-beta-feedback-section-title">Starter private feedback records</div>
          <div class="ob-beta-feedback-list">
            ${records.map(recordRow).join("")}
          </div>
        </div>

        <div class="ob-beta-feedback-note">
          <strong>Soulaana:</strong><br>
          Confusion is useful. Pressure is a warning. Bugs are receipts. Trust issues matter. But all of it stays private until the owner reviews it.
        </div>

        <div class="ob-beta-feedback-boundary">
          <strong>Boundary:</strong><br>
          Feedback stays private. Owner review required. No public proof. No public launch. No broker wiring. No broker API. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaFeedbackIntakePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const invite = document.getElementById("obPrivateBetaInvitePacketPanel");
    const launch = document.getElementById("obPrivateBetaLaunchControlPanel");
    const audit = document.getElementById("obOwnerSourceAuditPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (invite && invite.parentNode) {
      invite.insertAdjacentElement("afterend", panel);
    } else if (launch && launch.parentNode) {
      launch.insertAdjacentElement("afterend", panel);
    } else if (audit && audit.parentNode) {
      audit.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = feedbackState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-v39-private-beta-feedback-intake", "ready");
    window.OB_V39_PRIVATE_BETA_FEEDBACK_INTAKE_STATE = {
      version: VERSION,
      status: feedbackState.status,
      fallbackActive: feedbackState.fallbackActive,
      intakeStatus: payload.intake_status,
      feedbackPacketStatus: payload.feedback_packet_status,
      feedbackStaysPrivate: true,
      ownerReviewRequired: true,
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
      fetchFeedbackIntake();
    }, 1980);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obPrivateBetaInvitePacketUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_FEEDBACK_INTAKE_V39_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return feedbackState; },
    categories,
    starterRecords,
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchFeedbackIntake,
    renderPanel,
    setFlags
  };
})();
