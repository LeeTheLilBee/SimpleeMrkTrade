// OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE";
  const ENDPOINT = "/ob/manual-broker-checklist-fill-capture.json";

  // SMOKE MARKERS
  // Manual Broker Checklist Fill Capture
  // broker checklist detail
  // selected mission account
  // broker account manual confirmation
  // symbol contract manual confirmation
  // action side manual confirmation
  // limit order discipline
  // entry limit capture
  // do not enter above capture
  // stop target capture
  // spread liquidity confirmation
  // options approval manual confirmation
  // PDT margin cash warning acknowledgement
  // order not placed capture
  // order not placed reason
  // fill confirmation capture
  // manual fill price
  // manual fill time
  // manual quantity
  // broker confirmation id optional
  // monitor handoff placeholder
  // receipt preview
  // no broker API
  // no auto execution
  // no order submit
  // no hybrid submit
  // no automated live
  // Manual Live owner-only
  // beta Survey Paper only
  // Live Auto Locked

  let captureState = {
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
      source: "ob_giant_pack_007_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        private_beta_tower_lock_polish: "/ob/private-beta-tower-lock-polish.json",
        safety_preflight_gate: "/ob/manual-live-safety-preflight-gate.json",
        decision_packet: "/ob/manual-live-decision-packet.json",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      checklist_state: {
        checklist_id: "ob_ml1_manual_broker_checklist_001",
        label: "Manual Broker Checklist + Fill Capture",
        status: "manual_owner_capture_only",
        owner_only: true,
        broker_api_enabled: false,
        creates_order: false,
        transmits_order: false,
        stores_owner_entered_capture: true,
        requires_decision_packet: true,
        requires_safety_preflight: true,
        requires_tower_clearance: true
      },
      checklist_items: [
        {
          item_id: "selected_mission_account",
          label: "Selected mission account",
          required_input: "Owner confirms correct OB mission account.",
          expected_value: "Personal / Trust / ATM / Apartment / Business / Proof-Demo as allowed",
          gate_effect: "Blocks checklist if account does not match decision packet.",
          status: "required"
        },
        {
          item_id: "broker_account_manual_confirmation",
          label: "Broker account manual confirmation",
          required_input: "Owner confirms correct brokerage account manually.",
          expected_value: "Manual broker account confirmation",
          gate_effect: "OB does not verify broker account directly.",
          status: "manual_required"
        },
        {
          item_id: "symbol_contract_manual_confirmation",
          label: "Symbol / contract manual confirmation",
          required_input: "Owner confirms symbol, contract, expiration, strike, and option type if applicable.",
          expected_value: "Symbol/contract matches command card.",
          gate_effect: "Blocks fill capture if owner cannot confirm match.",
          status: "manual_required"
        },
        {
          item_id: "action_side_manual_confirmation",
          label: "Action side manual confirmation",
          required_input: "Owner confirms buy/sell/open/close intent manually.",
          expected_value: "Action side matches decision packet.",
          gate_effect: "Prevents wrong-side manual order mistakes.",
          status: "manual_required"
        },
        {
          item_id: "limit_order_discipline",
          label: "Limit order discipline",
          required_input: "Owner confirms limit-order discipline before manual placement.",
          expected_value: "Limit order, not market order, unless owner explicitly records exception.",
          gate_effect: "Protects against bad fills.",
          status: "required"
        },
        {
          item_id: "entry_limit_capture",
          label: "Entry limit capture",
          required_input: "Owner records intended limit price before manual broker action.",
          expected_value: "Owner-entered limit price.",
          gate_effect: "Required before fill/not-placed capture.",
          status: "required"
        },
        {
          item_id: "do_not_enter_above_capture",
          label: "Do-not-enter-above capture",
          required_input: "Owner records max acceptable entry.",
          expected_value: "Owner-entered do-not-enter-above value.",
          gate_effect: "Prevents chasing price after signal.",
          status: "required"
        },
        {
          item_id: "stop_target_capture",
          label: "Stop / target capture",
          required_input: "Owner records stop and target plan.",
          expected_value: "Owner-entered stop/target.",
          gate_effect: "Requires exit thinking before entry.",
          status: "required"
        },
        {
          item_id: "spread_liquidity_confirmation",
          label: "Spread / liquidity confirmation",
          required_input: "Owner confirms spread/liquidity manually before action.",
          expected_value: "Acceptable spread/liquidity.",
          gate_effect: "Blocks wide-spread or illiquid manual placement.",
          status: "required"
        },
        {
          item_id: "options_approval_manual_confirmation",
          label: "Options approval manual confirmation",
          required_input: "Owner confirms options permission manually at broker if option trade.",
          expected_value: "Options approval confirmed or not applicable.",
          gate_effect: "Prevents assuming broker permission.",
          status: "manual_required"
        },
        {
          item_id: "pdt_margin_cash_warning_acknowledgement",
          label: "PDT / margin / cash warning acknowledgement",
          required_input: "Owner acknowledges broker account rule implications.",
          expected_value: "Acknowledged manually.",
          gate_effect: "Records owner awareness; OB does not provide compliance determination.",
          status: "manual_warning"
        }
      ],
      not_placed_capture: {
        capture_id: "ob_ml1_order_not_placed_capture",
        label: "Order Not Placed Capture",
        required_fields: [
          "not_placed_reason",
          "price_moved",
          "spread_too_wide",
          "broker_restriction",
          "owner_changed_mind",
          "Tower_gate_blocked",
          "data_stale",
          "liquidity_failed",
          "manual_note"
        ],
        result: "not placed receipt only",
        creates_order: false,
        receipt_event: "order_not_placed"
      },
      fill_capture: {
        capture_id: "ob_ml1_fill_confirmation_capture",
        label: "Fill Confirmation Capture",
        required_fields: [
          "fill_time",
          "fill_price",
          "quantity",
          "symbol_or_contract",
          "order_type",
          "manual_broker_confirmation",
          "commission_or_fee_optional",
          "owner_note"
        ],
        optional_fields: [
          "broker_confirmation_id_optional",
          "screenshot_reference_later_vault_only",
          "slippage_note",
          "partial_fill_note"
        ],
        result: "owner-entered fill receipt only",
        creates_order: false,
        receipt_event: "fill_confirmed",
        monitor_handoff: "position_monitor_placeholder"
      },
      monitor_handoff_placeholder: {
        handoff_id: "ob_ml1_monitor_handoff_placeholder",
        label: "Monitor handoff placeholder",
        trigger: "after owner-entered fill confirmation",
        destination: "Trade Center / Open Positions preview",
        receipt_required: true,
        no_broker_sync: true
      },
      blocked_actions: [
        "submit_order_from_ob",
        "broker_api_order",
        "auto_execute",
        "hybrid_submit",
        "automated_live",
        "read_broker_account",
        "upload_direct_to_vault",
        "create_public_proof",
        "skip_decision_packet",
        "skip_safety_preflight"
      ],
      receipt_output: {
        not_placed_receipt: "manual_live_order_not_placed_receipt",
        fill_receipt: "manual_live_fill_confirmation_receipt",
        checklist_receipt: "manual_broker_checklist_detail_receipt",
        destination: "Review Center / Manual Live checklist capture",
        vault_ready: true,
        no_direct_vault_upload: true,
        sensitivity: "owner_only"
      },
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        decision_packet_required: true,
        safety_preflight_required: true,
        checklist_capture_only: true,
        fill_capture_owner_entered_only: true,
        not_placed_capture_owner_entered_only: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
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
      checklist_state: { ...(fallback.checklist_state || {}), ...(safe.checklist_state || {}) },
      checklist_items: Array.isArray(safe.checklist_items) ? safe.checklist_items : fallback.checklist_items,
      not_placed_capture: { ...(fallback.not_placed_capture || {}), ...(safe.not_placed_capture || {}) },
      fill_capture: { ...(fallback.fill_capture || {}), ...(safe.fill_capture || {}) },
      monitor_handoff_placeholder: { ...(fallback.monitor_handoff_placeholder || {}), ...(safe.monitor_handoff_placeholder || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      receipt_output: { ...(fallback.receipt_output || {}), ...(safe.receipt_output || {}) },
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        decision_packet_required: true,
        safety_preflight_required: true,
        checklist_capture_only: true,
        fill_capture_owner_entered_only: true,
        not_placed_capture_owner_entered_only: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
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

    window.OB_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_GP007 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_broker_checklist_fill_capture_gp007: normalized,
      checklist_capture_only: true,
      fill_capture_owner_entered_only: true,
      not_placed_capture_owner_entered_only: true,
      no_broker_api: true,
      no_order_submit: true,
      no_auto_execution: true,
      hybrid_locked: true,
      automated_locked: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obManualBrokerChecklistFillCaptureUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchCapture() {
    captureState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      captureState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        captureState.status = "ready";
        captureState.source = normalized.source || "server";
        captureState.payload = normalized;
        captureState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        captureState.status = "guarded_fallback";
        captureState.source = "guarded_fallback";
        captureState.payload = fallback;
        captureState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      captureState.status = "error_fallback";
      captureState.source = "error_fallback";
      captureState.payload = fallback;
      captureState.fallbackActive = true;
      captureState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return captureState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("disabled") || text.includes("locked")) return "red";
    if (text.includes("required") || text.includes("manual") || text.includes("warning") || text.includes("capture")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-broker-checklist-capture-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function checklistRow(item, index) {
    return `
      <div class="ob-broker-checklist-capture-row">
        <div class="ob-broker-checklist-capture-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Checklist item")}</strong>
          <span>${safeText(item.item_id, "item")}</span>
        </div>
        <span>${safeText(item.required_input, "required input")}<br>${safeText(item.gate_effect, "gate effect")}</span>
        <div class="ob-broker-checklist-capture-status ${tone(item.status)}">${safeText(item.status, "required")}</div>
      </div>
    `;
  }

  function fieldRow(field, index, kind) {
    return `
      <div class="ob-broker-checklist-capture-row">
        <div class="ob-broker-checklist-capture-dot">${kind}</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>owner-entered</span>
        </div>
        <span>This is captured manually by owner; OB does not read broker data.</span>
        <div class="ob-broker-checklist-capture-status gold">capture</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-broker-checklist-capture-row">
        <div class="ob-broker-checklist-capture-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP007 boundaries.</span>
        <div class="ob-broker-checklist-capture-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = captureState.payload || buildFallbackPayload();
    const state = payload.checklist_state || {};
    const items = Array.isArray(payload.checklist_items) ? payload.checklist_items : [];
    const notPlaced = payload.not_placed_capture || {};
    const fill = payload.fill_capture || {};
    const monitor = payload.monitor_handoff_placeholder || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-broker-checklist-capture-panel" id="obManualBrokerChecklistFillCapturePanel" data-ob-giant-pack-007="true">
        <div class="ob-broker-checklist-capture-head">
          <div>
            <div class="ob-label">OB Giant Pack 007 · Manual Broker Checklist + Capture</div>
            <div class="ob-broker-checklist-capture-title">Checklist Detail + Fill / Not-Placed Capture</div>
            <div class="ob-broker-checklist-capture-subtitle">
              ${safeText(captureState.status, "booting")} · ${safeText(state.status, "manual_owner_capture_only")} · owner-entered only.
            </div>
          </div>
          <div class="ob-broker-checklist-capture-chip-row">
            <span class="ob-broker-checklist-capture-chip gold">Manual capture only</span>
            <span class="ob-broker-checklist-capture-chip gold">Owner-entered fill</span>
            <span class="ob-broker-checklist-capture-chip red">No broker read</span>
            <span class="ob-broker-checklist-capture-chip red">No order submit</span>
          </div>
        </div>

        <div class="ob-broker-checklist-capture-stat-grid">
          ${card("Checklist", safeText(state.checklist_id, "checklist"))}
          ${card("Items", String(items.length))}
          ${card("Not placed", "capture")}
          ${card("Fill", "owner-entered")}
          ${card("Broker API", "disabled")}
        </div>

        <div class="ob-broker-checklist-capture-grid">
          <div>
            <div class="ob-broker-checklist-capture-card">
              <span>Purpose</span>
              <strong>Make the manual broker step clear without touching the broker.</strong>
              <div class="ob-broker-checklist-capture-callout">
                <strong>Allowed:</strong><br>
                Owner manually confirms broker/account details, then records either fill confirmation or order-not-placed reason.
              </div>
              <div class="ob-broker-checklist-capture-boundary">
                <strong>Boundary:</strong><br>
                OB does not read broker data, submit orders, upload proof, or create public records.
              </div>
            </div>

            <div class="ob-broker-checklist-capture-card" style="margin-top: 11px;">
              <span>Not placed capture</span>
              <strong>${safeText(notPlaced.label, "Order Not Placed Capture")}</strong>
              <div class="ob-broker-checklist-capture-list">
                ${(notPlaced.required_fields || []).map((field, index) => fieldRow(field, index, "N")).join("")}
              </div>
            </div>

            <div class="ob-broker-checklist-capture-card" style="margin-top: 11px;">
              <span>Fill capture</span>
              <strong>${safeText(fill.label, "Fill Confirmation Capture")}</strong>
              <div class="ob-broker-checklist-capture-list">
                ${(fill.required_fields || []).map((field, index) => fieldRow(field, index, "F")).join("")}
              </div>
            </div>

            <div class="ob-broker-checklist-capture-card" style="margin-top: 11px;">
              <span>Monitor handoff</span>
              <strong>${safeText(monitor.label, "Monitor handoff placeholder")}</strong>
              <div class="ob-broker-checklist-capture-callout">
                ${safeText(monitor.trigger, "after fill")} → ${safeText(monitor.destination, "Trade Center")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-broker-checklist-capture-section">
              <div class="ob-broker-checklist-capture-section-title">Manual broker checklist details</div>
              <div class="ob-broker-checklist-capture-list">${items.map(checklistRow).join("")}</div>
            </div>

            <div class="ob-broker-checklist-capture-section">
              <div class="ob-broker-checklist-capture-section-title">Blocked actions</div>
              <div class="ob-broker-checklist-capture-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-broker-checklist-capture-callout">
          <strong>Receipt output:</strong><br>
          Checklist detail, not-placed, and fill confirmation receipts are Review Center / Vault-ready placeholders only.
        </div>

        <div class="ob-broker-checklist-capture-boundary">
          <strong>Boundary:</strong><br>
          Manual Live owner-only. Beta Survey/Paper only. No broker API. No broker read. No order submit. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualBrokerChecklistFillCapturePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const decisionPanel = document.getElementById("obManualLiveDecisionPacketPanel");
    const preflightPanel = document.getElementById("obManualLiveSafetyPreflightPanel");
    const manualPanel = document.getElementById("obManualLiveLevel1Panel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (decisionPanel && decisionPanel.parentNode) decisionPanel.insertAdjacentElement("afterend", panel);
    else if (preflightPanel && preflightPanel.parentNode) preflightPanel.insertAdjacentElement("afterend", panel);
    else if (manualPanel && manualPanel.parentNode) manualPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = captureState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-007-manual-broker-checklist-fill-capture", "ready");
    document.body.setAttribute("data-ob-checklist-capture-only", "true");
    document.body.setAttribute("data-ob-fill-capture-owner-entered-only", "true");
    document.body.setAttribute("data-ob-not-placed-capture-owner-entered-only", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_007_BROKER_CHECKLIST_FILL_CAPTURE_STATE = {
      version: VERSION,
      status: captureState.status,
      fallbackActive: captureState.fallbackActive,
      checklistItemCount: payload.checklist_items.length,
      checklistCaptureOnly: true,
      fillCaptureOwnerEnteredOnly: true,
      notPlacedCaptureOwnerEnteredOnly: true,
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
      fetchCapture();
    }, 3820);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_GP007_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return captureState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchCapture,
    renderPanel,
    setFlags
  };
})();
