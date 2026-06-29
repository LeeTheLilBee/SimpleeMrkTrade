// OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE";
  const ENDPOINT = "/ob/position-monitor-exit-close-capture.json";

  // SMOKE MARKERS
  // Position Monitor Exit Close Capture
  // position monitor handoff
  // owner-entered fill monitor placeholder
  // monitored position snapshot
  // entry receipt linked
  // fill receipt linked
  // stop target plan visible
  // manual risk watch state
  // exit alert state
  // exit alert reason
  // take profit alert
  // stop warning alert
  // time based review alert
  // risk reduction alert
  // close decision capture
  // manual close confirmation
  // close price capture
  // close time capture
  // close quantity capture
  // realized result capture
  // final review required
  // close receipt preview
  // no broker API
  // no broker read
  // no auto close
  // no order submit
  // no auto execution
  // Manual Live owner-only
  // beta Survey Paper only
  // Live Auto Locked

  let monitorState = {
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
      source: "ob_giant_pack_008_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        private_beta_tower_lock_polish: "/ob/private-beta-tower-lock-polish.json",
        safety_preflight_gate: "/ob/manual-live-safety-preflight-gate.json",
        decision_packet: "/ob/manual-live-decision-packet.json",
        broker_checklist_fill_capture: "/ob/manual-broker-checklist-fill-capture.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      monitor_state: {
        monitor_id: "ob_ml1_position_monitor_placeholder_001",
        label: "Position Monitor Handoff",
        status: "owner_entered_fill_monitor_placeholder",
        owner_only: true,
        broker_api_enabled: false,
        broker_read_enabled: false,
        auto_close_enabled: false,
        creates_order: false,
        transmits_order: false,
        requires_fill_capture: true,
        requires_receipt_link: true
      },
      position_snapshot: {
        position_id: "owner_entered_manual_live_position_001",
        source: "owner-entered fill confirmation",
        mission_account: "selected OB account",
        symbol_or_contract: "owner-entered symbol/contract",
        strategy: "manual live reviewed candidate",
        entry_price: "owner-entered fill price",
        quantity: "owner-entered quantity",
        entry_time: "owner-entered fill time",
        stop_plan: "owner-entered stop",
        target_plan: "owner-entered target",
        do_not_enter_above: "owner-entered pre-entry cap",
        linked_decision_packet: "/ob/manual-live-decision-packet.json",
        linked_fill_capture: "/ob/manual-broker-checklist-fill-capture.json",
        linked_entry_receipt: "manual_live_fill_confirmation_receipt",
        linked_preflight_receipt: "manual_live_safety_preflight_receipt"
      },
      monitor_checks: [
        {
          check_id: "entry_receipt_linked",
          label: "Entry receipt linked",
          purpose: "Confirm fill confirmation receipt is connected to monitor placeholder.",
          state: "required",
          effect: "No monitor card without receipt link."
        },
        {
          check_id: "fill_receipt_linked",
          label: "Fill receipt linked",
          purpose: "Confirm owner-entered fill receipt exists.",
          state: "required",
          effect: "No performance tracking without owner-entered fill."
        },
        {
          check_id: "stop_target_plan_visible",
          label: "Stop / target plan visible",
          purpose: "Show exit plan before monitoring begins.",
          state: "required",
          effect: "Prevents unmanaged manual live position."
        },
        {
          check_id: "manual_risk_watch_state",
          label: "Manual risk watch state",
          purpose: "Owner sees if position is in normal, watch, warning, or exit-review state.",
          state: "placeholder",
          effect: "No auto close; owner must decide."
        },
        {
          check_id: "tower_kill_switch_watch",
          label: "Tower kill switch watch",
          purpose: "Surface if Tower kill switch or capital safety state would require review.",
          state: "watched",
          effect: "Triggers owner review, not broker action."
        },
        {
          check_id: "data_freshness_watch",
          label: "Data freshness watch",
          purpose: "Show stale/unknown monitor data warnings.",
          state: "watched",
          effect: "Owner must refresh/review manually."
        }
      ],
      exit_alert_states: [
        {
          alert_id: "take_profit_alert",
          label: "Take profit alert",
          trigger: "price reaches owner target zone",
          owner_action: "review manual close",
          result: "close decision capture only",
          broker_action: "owner manual at broker if chosen"
        },
        {
          alert_id: "stop_warning_alert",
          label: "Stop warning alert",
          trigger: "price approaches or breaches owner stop plan",
          owner_action: "review manual close or risk action",
          result: "close decision capture only",
          broker_action: "owner manual at broker if chosen"
        },
        {
          alert_id: "time_based_review_alert",
          label: "Time-based review alert",
          trigger: "position aging / expiration / review interval",
          owner_action: "review hold/close/watch",
          result: "review receipt only",
          broker_action: "none from OB"
        },
        {
          alert_id: "risk_reduction_alert",
          label: "Risk reduction alert",
          trigger: "Tower/capital/exposure warning",
          owner_action: "review reduce/close/watch",
          result: "risk review receipt only",
          broker_action: "owner manual at broker if chosen"
        }
      ],
      close_capture: {
        capture_id: "ob_ml1_manual_close_confirmation_capture",
        label: "Manual Close Confirmation Capture",
        required_fields: [
          "close_decision",
          "close_reason",
          "close_time",
          "close_price",
          "close_quantity",
          "symbol_or_contract",
          "manual_broker_confirmation",
          "realized_result",
          "owner_note"
        ],
        optional_fields: [
          "broker_confirmation_id_optional",
          "commission_or_fee_optional",
          "slippage_note",
          "partial_close_note",
          "screenshot_reference_later_vault_only"
        ],
        result: "owner-entered close receipt only",
        creates_order: false,
        receipt_event: "close_confirmed",
        final_review_required: true
      },
      close_decision_states: [
        {
          decision_id: "hold",
          label: "Hold",
          result: "hold receipt only",
          creates_order: false
        },
        {
          decision_id: "close_now",
          label: "Close manually",
          result: "owner closes manually at broker then captures close",
          creates_order: false
        },
        {
          decision_id: "watch",
          label: "Watch",
          result: "watch receipt only",
          creates_order: false
        },
        {
          decision_id: "risk_reduce",
          label: "Risk reduce manually",
          result: "owner reduces manually at broker then captures close/reduction",
          creates_order: false
        }
      ],
      receipt_output: {
        monitor_handoff_receipt: "manual_live_monitor_handoff_receipt",
        exit_alert_receipt: "manual_live_exit_alert_receipt",
        close_confirmation_receipt: "manual_live_close_confirmation_receipt",
        final_review_receipt: "manual_live_final_review_required_receipt",
        destination: "Review Center / Manual Live monitor and close capture",
        vault_ready: true,
        no_direct_vault_upload: true,
        sensitivity: "owner_only"
      },
      blocked_actions: [
        "read_broker_position",
        "broker_api_order",
        "submit_close_order_from_ob",
        "auto_close_position",
        "auto_execute",
        "hybrid_submit",
        "automated_live",
        "upload_direct_to_vault",
        "create_public_proof",
        "skip_fill_capture",
        "skip_close_receipt"
      ],
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        monitor_placeholder_only: true,
        owner_entered_fill_only: true,
        owner_entered_close_only: true,
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
      tower_sources: { ...(fallback.tower_sources || {}), ...(safe.tower_sources || {}) },
      monitor_state: { ...(fallback.monitor_state || {}), ...(safe.monitor_state || {}) },
      position_snapshot: { ...(fallback.position_snapshot || {}), ...(safe.position_snapshot || {}) },
      monitor_checks: Array.isArray(safe.monitor_checks) ? safe.monitor_checks : fallback.monitor_checks,
      exit_alert_states: Array.isArray(safe.exit_alert_states) ? safe.exit_alert_states : fallback.exit_alert_states,
      close_capture: { ...(fallback.close_capture || {}), ...(safe.close_capture || {}) },
      close_decision_states: Array.isArray(safe.close_decision_states) ? safe.close_decision_states : fallback.close_decision_states,
      receipt_output: { ...(fallback.receipt_output || {}), ...(safe.receipt_output || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        monitor_placeholder_only: true,
        owner_entered_fill_only: true,
        owner_entered_close_only: true,
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

    window.OB_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_GP008 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      position_monitor_exit_close_capture_gp008: normalized,
      monitor_placeholder_only: true,
      owner_entered_fill_only: true,
      owner_entered_close_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_auto_close: true,
      no_auto_execution: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obPositionMonitorExitCloseCaptureUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchMonitor() {
    monitorState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      monitorState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        monitorState.status = "ready";
        monitorState.source = normalized.source || "server";
        monitorState.payload = normalized;
        monitorState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        monitorState.status = "guarded_fallback";
        monitorState.source = "guarded_fallback";
        monitorState.payload = fallback;
        monitorState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      monitorState.status = "error_fallback";
      monitorState.source = "error_fallback";
      monitorState.payload = fallback;
      monitorState.fallbackActive = true;
      monitorState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return monitorState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("disabled") || text.includes("locked") || text.includes("breach")) return "red";
    if (text.includes("required") || text.includes("watch") || text.includes("review") || text.includes("placeholder")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-position-monitor-exit-close-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-position-monitor-exit-close-row">
        <div class="ob-position-monitor-exit-close-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.alert_id || item.decision_id, "Item")}</strong>
          <span>${safeText(item.check_id || item.alert_id || item.decision_id || "state", "state")}</span>
        </div>
        <span>${safeText(item.purpose || item.trigger || item.result || item.effect, "detail")}<br>${safeText(item.owner_action || item.broker_action || "", "")}</span>
        <div class="ob-position-monitor-exit-close-status ${tone(item.state || item.result || item.trigger)}">${safeText(item.state || item.result || "ready", "ready")}</div>
      </div>
    `;
  }

  function fieldRow(field, index) {
    return `
      <div class="ob-position-monitor-exit-close-row">
        <div class="ob-position-monitor-exit-close-dot">C</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>manual close capture</span>
        </div>
        <span>Owner enters this after manual broker close/reduction. OB does not read broker data.</span>
        <div class="ob-position-monitor-exit-close-status gold">capture</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-position-monitor-exit-close-row">
        <div class="ob-position-monitor-exit-close-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP008 boundaries.</span>
        <div class="ob-position-monitor-exit-close-status red">blocked</div>
      </div>
    `;
  }

  function snapshotRows(snapshot) {
    const pairs = [
      ["Mission account", snapshot.mission_account],
      ["Symbol/contract", snapshot.symbol_or_contract],
      ["Entry price", snapshot.entry_price],
      ["Quantity", snapshot.quantity],
      ["Entry time", snapshot.entry_time],
      ["Stop plan", snapshot.stop_plan],
      ["Target plan", snapshot.target_plan],
      ["Linked fill", snapshot.linked_fill_capture]
    ];

    return pairs.map((pair, index) => `
      <div class="ob-position-monitor-exit-close-row">
        <div class="ob-position-monitor-exit-close-dot">P</div>
        <div>
          <strong>${pair[0]}</strong>
          <span>snapshot</span>
        </div>
        <span>${safeText(pair[1], "placeholder")}</span>
        <div class="ob-position-monitor-exit-close-status gold">owner-entered</div>
      </div>
    `).join("");
  }

  function panelHtml() {
    const payload = monitorState.payload || buildFallbackPayload();
    const state = payload.monitor_state || {};
    const snapshot = payload.position_snapshot || {};
    const checks = Array.isArray(payload.monitor_checks) ? payload.monitor_checks : [];
    const alerts = Array.isArray(payload.exit_alert_states) ? payload.exit_alert_states : [];
    const close = payload.close_capture || {};
    const decisions = Array.isArray(payload.close_decision_states) ? payload.close_decision_states : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-position-monitor-exit-close-panel" id="obPositionMonitorExitClosePanel" data-ob-giant-pack-008="true">
        <div class="ob-position-monitor-exit-close-head">
          <div>
            <div class="ob-label">OB Giant Pack 008 · Position Monitor + Exit/Close Capture</div>
            <div class="ob-position-monitor-exit-close-title">Monitor Handoff + Manual Close Capture</div>
            <div class="ob-position-monitor-exit-close-subtitle">
              ${safeText(monitorState.status, "booting")} · ${safeText(state.status, "placeholder")} · no broker read, no auto close.
            </div>
          </div>
          <div class="ob-position-monitor-exit-close-chip-row">
            <span class="ob-position-monitor-exit-close-chip gold">Owner-entered fill</span>
            <span class="ob-position-monitor-exit-close-chip gold">Manual close capture</span>
            <span class="ob-position-monitor-exit-close-chip red">No broker read</span>
            <span class="ob-position-monitor-exit-close-chip red">No auto close</span>
          </div>
        </div>

        <div class="ob-position-monitor-exit-close-stat-grid">
          ${card("Monitor", safeText(state.monitor_id, "monitor"))}
          ${card("Checks", String(checks.length))}
          ${card("Exit alerts", String(alerts.length))}
          ${card("Close fields", String((close.required_fields || []).length))}
          ${card("Broker", "not connected")}
        </div>

        <div class="ob-position-monitor-exit-close-grid">
          <div>
            <div class="ob-position-monitor-exit-close-card">
              <span>Purpose</span>
              <strong>Track owner-entered fill as a monitored placeholder and capture manual close.</strong>
              <div class="ob-position-monitor-exit-close-callout">
                <strong>Allowed:</strong><br>
                OB can show monitor state, exit alert prompts, and owner-entered close confirmation fields.
              </div>
              <div class="ob-position-monitor-exit-close-boundary">
                <strong>Blocked:</strong><br>
                OB cannot read broker positions, auto-close, submit close orders, or create public proof.
              </div>
            </div>

            <div class="ob-position-monitor-exit-close-card" style="margin-top: 11px;">
              <span>Monitored position snapshot</span>
              <div class="ob-position-monitor-exit-close-list">${snapshotRows(snapshot)}</div>
            </div>

            <div class="ob-position-monitor-exit-close-card" style="margin-top: 11px;">
              <span>Manual close capture</span>
              <strong>${safeText(close.label, "Manual Close Confirmation Capture")}</strong>
              <div class="ob-position-monitor-exit-close-list">
                ${(close.required_fields || []).map(fieldRow).join("")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-position-monitor-exit-close-section">
              <div class="ob-position-monitor-exit-close-section-title">Monitor checks</div>
              <div class="ob-position-monitor-exit-close-list">${checks.map((item, index) => row(item, index)).join("")}</div>
            </div>

            <div class="ob-position-monitor-exit-close-section">
              <div class="ob-position-monitor-exit-close-section-title">Exit alert states</div>
              <div class="ob-position-monitor-exit-close-list">${alerts.map((item, index) => row(item, index, "E")).join("")}</div>
            </div>

            <div class="ob-position-monitor-exit-close-section">
              <div class="ob-position-monitor-exit-close-section-title">Close decision states</div>
              <div class="ob-position-monitor-exit-close-list">${decisions.map((item, index) => row(item, index, "D")).join("")}</div>
            </div>

            <div class="ob-position-monitor-exit-close-section">
              <div class="ob-position-monitor-exit-close-section-title">Blocked actions</div>
              <div class="ob-position-monitor-exit-close-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-position-monitor-exit-close-callout">
          <strong>Receipt output:</strong><br>
          Monitor handoff, exit alert, close confirmation, and final review receipts are Review Center / Vault-ready placeholders only.
        </div>

        <div class="ob-position-monitor-exit-close-boundary">
          <strong>Boundary:</strong><br>
          Manual Live owner-only. Beta Survey/Paper only. No broker API. No broker read. No auto close. No order submit. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPositionMonitorExitClosePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const checklistPanel = document.getElementById("obManualBrokerChecklistFillCapturePanel");
    const decisionPanel = document.getElementById("obManualLiveDecisionPacketPanel");
    const manualPanel = document.getElementById("obManualLiveLevel1Panel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (checklistPanel && checklistPanel.parentNode) checklistPanel.insertAdjacentElement("afterend", panel);
    else if (decisionPanel && decisionPanel.parentNode) decisionPanel.insertAdjacentElement("afterend", panel);
    else if (manualPanel && manualPanel.parentNode) manualPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = monitorState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-008-position-monitor-exit-close", "ready");
    document.body.setAttribute("data-ob-monitor-placeholder-only", "true");
    document.body.setAttribute("data-ob-owner-entered-fill-only", "true");
    document.body.setAttribute("data-ob-owner-entered-close-only", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-auto-close", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_STATE = {
      version: VERSION,
      status: monitorState.status,
      fallbackActive: monitorState.fallbackActive,
      monitorCheckCount: payload.monitor_checks.length,
      exitAlertCount: payload.exit_alert_states.length,
      closeFieldCount: payload.close_capture.required_fields.length,
      monitorPlaceholderOnly: true,
      ownerEnteredFillOnly: true,
      ownerEnteredCloseOnly: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noAutoClose: true,
      noOrderSubmit: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchMonitor();
    }, 3980);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_GP008_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return monitorState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchMonitor,
    renderPanel,
    setFlags
  };
})();
