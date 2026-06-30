// OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE";
  const ENDPOINT = "/ob/owner-rehearsal-engine.json";

  // SMOKE MARKERS
  // Owner Rehearsal Engine
  // owner rehearsal mode
  // fake candidate walkthrough
  // demo candidate library
  // rehearsal session id
  // mission account rehearsal choice
  // decision packet rehearsal state
  // safety preflight rehearsal state
  // broker checklist rehearsal state
  // fill not placed rehearsal state
  // monitor exit close rehearsal state
  // final review rehearsal state
  // rehearsal receipt preview
  // rehearsal lifecycle state machine
  // owner rehearsal only
  // no real market order
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no public proof
  // no direct Vault upload
  // Manual Live owner-only
  // beta Survey Paper only
  // Live Auto Locked

  let rehearsalState = {
    status: "booting",
    httpStatus: null,
    source: "fallback",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_011_safe_fallback",
      engine_state: {
        engine_id: "ob_owner_rehearsal_engine_001",
        label: "Owner Rehearsal Engine",
        status: "owner_rehearsal_mode_ready",
        mode: "fake_demo_candidate_only",
        owner_only: true,
        beta_locked: true,
        creates_real_order: false,
        reads_broker: false,
        rehearsal_session_required: true
      },
      demo_candidate_library: [
        {
          candidate_id: "demo_mu_call_rehearsal_001",
          symbol: "MU",
          asset_type: "option_demo",
          strategy: "momentum pullback demo",
          side: "BUY_TO_OPEN rehearsal",
          account_fit: "Personal OB Account rehearsal",
          confidence_label: "system_generated_demo",
          freshness_label: "demo_static",
          risk_label: "moderate demo",
          purpose: "Practice full Manual Live L1 flow using fake option-style candidate.",
          status: "available"
        },
        {
          candidate_id: "demo_amd_stock_rehearsal_002",
          symbol: "AMD",
          asset_type: "stock_demo",
          strategy: "trend continuation demo",
          side: "BUY rehearsal",
          account_fit: "Proof/Demo OB Account rehearsal",
          confidence_label: "system_generated_demo",
          freshness_label: "demo_static",
          risk_label: "low demo",
          purpose: "Practice stock fallback-style Manual Live flow without real order.",
          status: "available"
        },
        {
          candidate_id: "demo_reject_bad_spread_003",
          symbol: "NVDA",
          asset_type: "option_demo",
          strategy: "bad spread rejection demo",
          side: "WATCH_OR_REJECT rehearsal",
          account_fit: "Proof/Demo OB Account rehearsal",
          confidence_label: "needs_verification_demo",
          freshness_label: "demo_static",
          risk_label: "blocked demo",
          purpose: "Practice rejecting or watching candidate because spread/liquidity fails.",
          status: "available"
        }
      ],
      rehearsal_session_template: {
        session_id: "ob_rehearsal_session_demo_001",
        session_type: "owner_manual_live_l1_rehearsal",
        selected_candidate_id: "demo_mu_call_rehearsal_001",
        selected_mission_account: "Proof/Demo OB Account",
        mode: "owner_rehearsal",
        started_by: "owner",
        status: "not_started",
        sensitivity: "owner_only",
        vault_ready: true,
        no_direct_vault_upload: true
      },
      rehearsal_state_machine: [
        {
          step_id: "select_demo_candidate",
          label: "Select demo candidate",
          source: "demo_candidate_library",
          expected_owner_action: "Pick a fake/demo candidate.",
          linked_gp: "GP002",
          status: "ready"
        },
        {
          step_id: "choose_rehearsal_account",
          label: "Choose rehearsal account",
          source: "/ob/account-experience.json",
          expected_owner_action: "Choose Proof/Demo or owner mission account rehearsal lane.",
          linked_gp: "GP001",
          status: "ready"
        },
        {
          step_id: "review_decision_packet",
          label: "Review decision packet",
          source: "/ob/manual-live-decision-packet.json",
          expected_owner_action: "Approve checklist, reject, or watch in rehearsal.",
          linked_gp: "GP006",
          status: "ready"
        },
        {
          step_id: "run_safety_preflight",
          label: "Run safety preflight",
          source: "/ob/manual-live-safety-preflight-gate.json",
          expected_owner_action: "Walk through policy, mode, kill switch, freshness, confidence, exposure, protected-floor, and broker warnings.",
          linked_gp: "GP005",
          status: "ready"
        },
        {
          step_id: "complete_manual_checklist",
          label: "Complete manual checklist",
          source: "/ob/manual-broker-checklist-fill-capture.json",
          expected_owner_action: "Practice confirming broker account, symbol/contract, side, limit, stop, target, liquidity, options approval, and PDT warning.",
          linked_gp: "GP007",
          status: "ready"
        },
        {
          step_id: "capture_fake_fill_or_not_placed",
          label: "Capture fake fill or not placed",
          source: "/ob/manual-broker-checklist-fill-capture.json",
          expected_owner_action: "Enter fake fill details or not-placed reason.",
          linked_gp: "GP007",
          status: "ready"
        },
        {
          step_id: "monitor_fake_position",
          label: "Monitor fake position",
          source: "/ob/position-monitor-exit-close-capture.json",
          expected_owner_action: "Review fake monitor placeholder and exit alert states.",
          linked_gp: "GP008",
          status: "ready"
        },
        {
          step_id: "capture_fake_close",
          label: "Capture fake close",
          source: "/ob/position-monitor-exit-close-capture.json",
          expected_owner_action: "Enter fake close price, time, quantity, reason, and result.",
          linked_gp: "GP008",
          status: "ready"
        },
        {
          step_id: "complete_final_review",
          label: "Complete final review",
          source: "/ob/final-trade-review-performance-receipt.json",
          expected_owner_action: "Record fake result, rule review, lessons, and performance receipt.",
          linked_gp: "GP009",
          status: "ready"
        },
        {
          step_id: "readiness_confirmed",
          label: "Readiness confirmed",
          source: "/ob/manual-live-l1-readiness-checkpoint.json",
          expected_owner_action: "Confirm rehearsal completed and note remaining blockers before real Manual Live.",
          linked_gp: "GP010",
          status: "ready"
        }
      ],
      rehearsal_outputs: {
        decision_rehearsal_record: "owner_rehearsal_decision_record_preview",
        preflight_rehearsal_record: "owner_rehearsal_preflight_record_preview",
        checklist_rehearsal_record: "owner_rehearsal_checklist_record_preview",
        fill_or_not_placed_rehearsal_record: "owner_rehearsal_fill_or_not_placed_record_preview",
        monitor_rehearsal_record: "owner_rehearsal_monitor_record_preview",
        close_rehearsal_record: "owner_rehearsal_close_record_preview",
        final_review_rehearsal_record: "owner_rehearsal_final_review_record_preview",
        rehearsal_receipt: "owner_manual_live_l1_rehearsal_receipt_preview",
        review_center_destination: "Review Center / Owner rehearsal records",
        vault_ready: true,
        no_direct_vault_upload: true
      },
      rehearsal_quality_checks: [
        {
          check_id: "all_steps_available",
          label: "All steps available",
          purpose: "GP001-GP010 path is available to rehearse.",
          result: "ready"
        },
        {
          check_id: "owner_only_boundary",
          label: "Owner-only boundary",
          purpose: "Rehearsal is for owner/operator, not beta users.",
          result: "locked"
        },
        {
          check_id: "fake_data_only",
          label: "Fake/demo data only",
          purpose: "Rehearsal does not use real broker or real order data.",
          result: "locked"
        },
        {
          check_id: "receipt_preview_only",
          label: "Receipt preview only",
          purpose: "Rehearsal creates future record shapes and receipt previews only.",
          result: "ready"
        },
        {
          check_id: "no_execution_boundary",
          label: "No execution boundary",
          purpose: "No broker API, no broker read, no order submit, no auto execution.",
          result: "locked"
        }
      ],
      blocked_actions: [
        "use_real_broker_account",
        "read_broker_account",
        "submit_order_from_ob",
        "submit_close_order_from_ob",
        "auto_execute",
        "auto_close_position",
        "hybrid_submit",
        "automated_live",
        "create_public_proof",
        "publish_rehearsal",
        "upload_direct_to_vault",
        "use_beta_user_as_owner_rehearsal"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        fake_candidate_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        no_real_market_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      engine_state: { ...(fallback.engine_state || {}), ...(safe.engine_state || {}) },
      demo_candidate_library: Array.isArray(safe.demo_candidate_library) ? safe.demo_candidate_library : fallback.demo_candidate_library,
      rehearsal_session_template: { ...(fallback.rehearsal_session_template || {}), ...(safe.rehearsal_session_template || {}) },
      rehearsal_state_machine: Array.isArray(safe.rehearsal_state_machine) ? safe.rehearsal_state_machine : fallback.rehearsal_state_machine,
      rehearsal_outputs: { ...(fallback.rehearsal_outputs || {}), ...(safe.rehearsal_outputs || {}) },
      rehearsal_quality_checks: Array.isArray(safe.rehearsal_quality_checks) ? safe.rehearsal_quality_checks : fallback.rehearsal_quality_checks,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        fake_candidate_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        no_real_market_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_OWNER_REHEARSAL_ENGINE_GP011 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_rehearsal_engine_gp011: normalized,
      owner_rehearsal_only: true,
      fake_candidate_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_order_submit: true,
      no_auto_execution: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obOwnerRehearsalEngineUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchRehearsal() {
    rehearsalState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      rehearsalState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        rehearsalState.status = "ready";
        rehearsalState.source = normalized.source || "server";
        rehearsalState.payload = normalized;
        rehearsalState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        rehearsalState.status = "guarded_fallback";
        rehearsalState.source = "guarded_fallback";
        rehearsalState.payload = fallback;
        rehearsalState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      rehearsalState.status = "error_fallback";
      rehearsalState.source = "error_fallback";
      rehearsalState.payload = fallback;
      rehearsalState.fallbackActive = true;
      rehearsalState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return rehearsalState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("no ") || text.includes("fake")) return "red";
    if (text.includes("ready") || text.includes("available")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-rehearsal-engine-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-rehearsal-engine-row">
        <div class="ob-owner-rehearsal-engine-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.candidate_id || item.step_id || item.check_id, "Item")}</strong>
          <span>${safeText(item.symbol || item.linked_gp || item.status || item.check_id || "rehearsal", "rehearsal")}</span>
        </div>
        <span>${safeText(item.purpose || item.expected_owner_action || item.strategy || item.result, "detail")}</span>
        <div class="ob-owner-rehearsal-engine-status ${tone(item.status || item.result || item.asset_type)}">${safeText(item.status || item.result || item.asset_type, "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-rehearsal-engine-row">
        <div class="ob-owner-rehearsal-engine-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP011 owner rehearsal boundaries.</span>
        <div class="ob-owner-rehearsal-engine-status red">blocked</div>
      </div>
    `;
  }

  function outputRows(outputs) {
    return Object.keys(outputs || {}).map((key) => {
      return `
        <div class="ob-owner-rehearsal-engine-row">
          <div class="ob-owner-rehearsal-engine-dot">O</div>
          <div>
            <strong>${key}</strong>
            <span>output contract</span>
          </div>
          <span>${safeText(outputs[key], "output")}</span>
          <div class="ob-owner-rehearsal-engine-status gold">preview</div>
        </div>
      `;
    }).join("");
  }

  function panelHtml() {
    const payload = rehearsalState.payload || buildFallbackPayload();
    const engine = payload.engine_state || {};
    const candidates = Array.isArray(payload.demo_candidate_library) ? payload.demo_candidate_library : [];
    const session = payload.rehearsal_session_template || {};
    const steps = Array.isArray(payload.rehearsal_state_machine) ? payload.rehearsal_state_machine : [];
    const outputs = payload.rehearsal_outputs || {};
    const quality = Array.isArray(payload.rehearsal_quality_checks) ? payload.rehearsal_quality_checks : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-rehearsal-engine-panel" id="obOwnerRehearsalEnginePanel" data-ob-giant-pack-011="true">
        <div class="ob-owner-rehearsal-engine-head">
          <div>
            <div class="ob-label">OB Giant Pack 011 · Owner Rehearsal Engine</div>
            <div class="ob-owner-rehearsal-engine-title">Owner Rehearsal Mode</div>
            <div class="ob-owner-rehearsal-engine-subtitle">
              ${safeText(rehearsalState.status, "booting")} · ${safeText(engine.status, "owner_rehearsal_mode_ready")} · fake/demo candidate only.
            </div>
          </div>
          <div class="ob-owner-rehearsal-engine-chip-row">
            <span class="ob-owner-rehearsal-engine-chip green">Demo candidates</span>
            <span class="ob-owner-rehearsal-engine-chip gold">Owner rehearsal only</span>
            <span class="ob-owner-rehearsal-engine-chip red">No broker API</span>
            <span class="ob-owner-rehearsal-engine-chip red">No real order</span>
          </div>
        </div>

        <div class="ob-owner-rehearsal-engine-stat-grid">
          ${card("Candidates", String(candidates.length))}
          ${card("Steps", String(steps.length))}
          ${card("Outputs", String(Object.keys(outputs).length))}
          ${card("Quality checks", String(quality.length))}
          ${card("Mode", safeText(engine.mode, "fake_demo_candidate_only"))}
        </div>

        <div class="ob-owner-rehearsal-engine-grid">
          <div>
            <div class="ob-owner-rehearsal-engine-card">
              <span>Purpose</span>
              <strong>Practice the full Manual Live Level 1 flow with fake/demo data before real Manual Live.</strong>
              <div class="ob-owner-rehearsal-engine-callout">
                <strong>Flow:</strong><br>
                Pick fake candidate → choose rehearsal account → decision → preflight → checklist → fake fill/not placed → monitor → fake close → final review.
              </div>
              <div class="ob-owner-rehearsal-engine-boundary">
                <strong>Boundary:</strong><br>
                This does not read broker data, submit orders, auto execute, publish proof, or upload directly to Vault.
              </div>
            </div>

            <div class="ob-owner-rehearsal-engine-card" style="margin-top: 11px;">
              <span>Session template</span>
              <strong>${safeText(session.session_id, "rehearsal session")}</strong>
              <div class="ob-owner-rehearsal-engine-callout">
                ${safeText(session.session_type, "owner rehearsal")} · ${safeText(session.selected_mission_account, "Proof/Demo OB Account")} · ${safeText(session.mode, "owner_rehearsal")}
              </div>
            </div>

            <div class="ob-owner-rehearsal-engine-card" style="margin-top: 11px;">
              <span>Rehearsal outputs</span>
              <div class="ob-owner-rehearsal-engine-list">${outputRows(outputs)}</div>
            </div>
          </div>

          <div>
            <div class="ob-owner-rehearsal-engine-section">
              <div class="ob-owner-rehearsal-engine-section-title">Demo candidate library</div>
              <div class="ob-owner-rehearsal-engine-list">${candidates.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-owner-rehearsal-engine-section">
              <div class="ob-owner-rehearsal-engine-section-title">Rehearsal lifecycle state machine</div>
              <div class="ob-owner-rehearsal-engine-list">${steps.map((item, index) => row(item, index)).join("")}</div>
            </div>

            <div class="ob-owner-rehearsal-engine-section">
              <div class="ob-owner-rehearsal-engine-section-title">Quality checks</div>
              <div class="ob-owner-rehearsal-engine-list">${quality.map((item, index) => row(item, index, "Q")).join("")}</div>
            </div>

            <div class="ob-owner-rehearsal-engine-section">
              <div class="ob-owner-rehearsal-engine-section-title">Blocked actions</div>
              <div class="ob-owner-rehearsal-engine-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-rehearsal-engine-callout">
          <strong>Rehearsal result:</strong><br>
          Owner can practice the full Manual Live Level 1 safe skeleton with demo data and receipt previews.
        </div>

        <div class="ob-owner-rehearsal-engine-boundary">
          <strong>Still locked:</strong><br>
          No real market order. No broker API. No broker read. No order submit. No auto execution. No public proof. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerRehearsalEnginePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const readinessPanel = document.getElementById("obManualLiveL1ReadinessPanel");
    const finalReviewPanel = document.getElementById("obFinalReviewPerformancePanel");
    const monitorPanel = document.getElementById("obPositionMonitorExitClosePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (readinessPanel && readinessPanel.parentNode) readinessPanel.insertAdjacentElement("afterend", panel);
    else if (finalReviewPanel && finalReviewPanel.parentNode) finalReviewPanel.insertAdjacentElement("afterend", panel);
    else if (monitorPanel && monitorPanel.parentNode) monitorPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = rehearsalState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-011-owner-rehearsal-engine", "ready");
    document.body.setAttribute("data-ob-owner-rehearsal-only", "true");
    document.body.setAttribute("data-ob-fake-candidate-only", "true");
    document.body.setAttribute("data-ob-no-real-market-order", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_STATE = {
      version: VERSION,
      status: rehearsalState.status,
      fallbackActive: rehearsalState.fallbackActive,
      demoCandidateCount: payload.demo_candidate_library.length,
      rehearsalStepCount: payload.rehearsal_state_machine.length,
      ownerRehearsalOnly: true,
      fakeCandidateOnly: true,
      noRealMarketOrder: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchRehearsal();
    }, 4460);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_REHEARSAL_ENGINE_GP011_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return rehearsalState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchRehearsal,
    renderPanel,
    setFlags
  };
})();
