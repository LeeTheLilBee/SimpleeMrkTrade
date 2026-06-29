// OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET_JS

(function () {
  const VERSION = "OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET";
  const ENDPOINT = "/ob/manual-live-decision-packet.json";

  // SMOKE MARKERS
  // Manual Live Decision Packet
  // command card packet
  // account experience packet
  // safety preflight packet
  // Tower clearance packet
  // broker checklist preview packet
  // receipt preview packet
  // owner decision packet
  // approve reject watch packet
  // approve creates checklist receipt only
  // reject creates rejection receipt only
  // watch creates watch receipt only
  // no order submit
  // no broker API
  // no auto execution
  // no hybrid submit
  // no automated live
  // Manual Live owner-only
  // beta Survey Paper only
  // Live Auto Locked

  let packetState = {
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
      source: "ob_giant_pack_006_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        private_beta_tower_lock_polish: "/ob/private-beta-tower-lock-polish.json",
        safety_preflight_gate: "/ob/manual-live-safety-preflight-gate.json",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        mode_permission_controller: "/tower/tower-mode-permission-controller-index-v461.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      packet_state: {
        packet_id: "ob_ml1_decision_packet_001",
        label: "Manual Live Decision Packet",
        packet_status: "owner_review_required",
        current_result: "no decision submitted",
        owner_only: true,
        creates_order: false,
        creates_broker_action: false,
        creates_receipt_preview: true,
        requires_safety_preflight: true,
        requires_tower_clearance: true,
        requires_owner_step_up: true
      },
      packet_sections: [
        {
          section_id: "command_card",
          label: "Command Card",
          purpose: "Shows symbol, strategy, mission fit, risk summary, and action choices.",
          source: "/ob/manual-live-level-1.json",
          required: true,
          status: "ready"
        },
        {
          section_id: "account_experience",
          label: "Account Experience",
          purpose: "Confirms owner mission account versus beta Survey/Paper account.",
          source: "/ob/account-experience.json",
          required: true,
          status: "ready"
        },
        {
          section_id: "safety_preflight",
          label: "Safety Preflight",
          purpose: "Confirms account policy, mode, kill switch, freshness, confidence, exposure, and protected-floor checks.",
          source: "/ob/manual-live-safety-preflight-gate.json",
          required: true,
          status: "required"
        },
        {
          section_id: "tower_clearance",
          label: "Tower Clearance",
          purpose: "Confirms Tower clearance and owner step-up requirement.",
          source: "Tower capital safety controls",
          required: true,
          status: "required"
        },
        {
          section_id: "broker_checklist_preview",
          label: "Broker Checklist Preview",
          purpose: "Shows manual checklist only; OB does not place or transmit orders.",
          source: "/ob/manual-live-level-1.json",
          required: true,
          status: "checklist_only"
        },
        {
          section_id: "receipt_preview",
          label: "Receipt Preview",
          purpose: "Previews decision receipt before Review Center saves it.",
          source: "/ob/receipts-review-foundation.json",
          required: true,
          status: "vault_ready_placeholder"
        },
        {
          section_id: "owner_decision",
          label: "Owner Decision",
          purpose: "Approve / Reject / Watch only.",
          source: "Owner action",
          required: true,
          status: "waiting_owner"
        }
      ],
      decision_actions: {
        approve: {
          label: "Approve",
          allowed_result: "manual broker checklist receipt only",
          packet_result: "preflight-approved checklist packet",
          creates_real_order: false,
          creates_broker_api_call: false,
          creates_receipt_type: "owner_approved_manual_checklist_packet",
          requires_all_preflight_checks: true
        },
        reject: {
          label: "Reject",
          allowed_result: "rejection receipt only",
          packet_result: "owner rejected candidate packet",
          creates_real_order: false,
          creates_broker_api_call: false,
          creates_receipt_type: "owner_rejected_candidate_packet",
          requires_all_preflight_checks: false
        },
        watch: {
          label: "Watch",
          allowed_result: "watch/snooze receipt only",
          packet_result: "owner watch candidate packet",
          creates_real_order: false,
          creates_broker_api_call: false,
          creates_receipt_type: "owner_watched_candidate_packet",
          requires_all_preflight_checks: false
        }
      },
      packet_receipt_preview: {
        receipt_id: "ob_ml1_decision_packet_receipt_preview",
        receipt_type: "manual_live_decision_packet_receipt",
        timestamp: "placeholder_timestamp",
        source_app: "OB",
        linked_packet: "ob_ml1_decision_packet_001",
        linked_account_experience: "/ob/account-experience.json",
        linked_command_card: "/ob/manual-live-level-1.json",
        linked_preflight_gate: "/ob/manual-live-safety-preflight-gate.json",
        linked_review_foundation: "/ob/receipts-review-foundation.json",
        tower_permission_state: "required",
        owner_action: "pending",
        result: "pending",
        vault_ready: true,
        no_direct_vault_upload: true,
        sensitivity: "owner_only",
        public_exposure: "never_public"
      },
      blocked_actions: [
        "submit_order_from_ob",
        "broker_api_order",
        "auto_execute",
        "hybrid_submit",
        "automated_live",
        "skip_preflight",
        "skip_tower_clearance",
        "skip_owner_step_up",
        "create_public_proof",
        "upload_direct_to_vault"
      ],
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        decision_packet_required: true,
        safety_preflight_required: true,
        checklist_only_no_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
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
      packet_state: { ...(fallback.packet_state || {}), ...(safe.packet_state || {}) },
      packet_sections: Array.isArray(safe.packet_sections) ? safe.packet_sections : fallback.packet_sections,
      decision_actions: { ...(fallback.decision_actions || {}), ...(safe.decision_actions || {}) },
      packet_receipt_preview: { ...(fallback.packet_receipt_preview || {}), ...(safe.packet_receipt_preview || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        decision_packet_required: true,
        safety_preflight_required: true,
        checklist_only_no_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
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

    window.OB_MANUAL_LIVE_DECISION_PACKET_GP006 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_decision_packet_gp006: normalized,
      decision_packet_required: true,
      safety_preflight_required: true,
      checklist_only_no_order: true,
      no_broker_api: true,
      no_auto_execution: true,
      hybrid_locked: true,
      automated_locked: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obManualLiveDecisionPacketUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchPacket() {
    packetState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      packetState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        packetState.status = "ready";
        packetState.source = normalized.source || "server";
        packetState.payload = normalized;
        packetState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        packetState.status = "guarded_fallback";
        packetState.source = "guarded_fallback";
        packetState.payload = fallback;
        packetState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      packetState.status = "error_fallback";
      packetState.source = "error_fallback";
      packetState.payload = fallback;
      packetState.fallbackActive = true;
      packetState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return packetState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("disabled") || text.includes("locked") || text.includes("never")) return "red";
    if (text.includes("required") || text.includes("waiting") || text.includes("checklist") || text.includes("placeholder")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-decision-packet-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function sectionRow(item, index) {
    return `
      <div class="ob-manual-live-decision-packet-row">
        <div class="ob-manual-live-decision-packet-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Packet section")}</strong>
          <span>${safeText(item.section_id, "section")}</span>
        </div>
        <span>${safeText(item.purpose, "purpose")}<br>Source: ${safeText(item.source, "source")}</span>
        <div class="ob-manual-live-decision-packet-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function actionRow(key, item) {
    return `
      <div class="ob-manual-live-decision-packet-row">
        <div class="ob-manual-live-decision-packet-dot">A</div>
        <div>
          <strong>${safeText(item.label, key)}</strong>
          <span>${key}</span>
        </div>
        <span>${safeText(item.allowed_result, "allowed")}<br>Receipt: ${safeText(item.creates_receipt_type, "receipt")}</span>
        <div class="ob-manual-live-decision-packet-status ${item.requires_all_preflight_checks ? "gold" : "green"}">${item.requires_all_preflight_checks ? "preflight required" : "receipt only"}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-decision-packet-row">
        <div class="ob-manual-live-decision-packet-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is not allowed from the Manual Live Decision Packet.</span>
        <div class="ob-manual-live-decision-packet-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = packetState.payload || buildFallbackPayload();
    const state = payload.packet_state || {};
    const sections = Array.isArray(payload.packet_sections) ? payload.packet_sections : [];
    const actions = payload.decision_actions || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];
    const receipt = payload.packet_receipt_preview || {};

    return `
      <div class="ob-manual-live-decision-packet-panel" id="obManualLiveDecisionPacketPanel" data-ob-giant-pack-006="true">
        <div class="ob-manual-live-decision-packet-head">
          <div>
            <div class="ob-label">OB Giant Pack 006 · Manual Live Decision Packet</div>
            <div class="ob-manual-live-decision-packet-title">Owner Decision Packet</div>
            <div class="ob-manual-live-decision-packet-subtitle">
              ${safeText(packetState.status, "booting")} · ${safeText(state.packet_status, "owner_review_required")} · packet creates no broker action.
            </div>
          </div>
          <div class="ob-manual-live-decision-packet-chip-row">
            <span class="ob-manual-live-decision-packet-chip gold">Owner decision required</span>
            <span class="ob-manual-live-decision-packet-chip gold">Preflight required</span>
            <span class="ob-manual-live-decision-packet-chip red">No broker API</span>
            <span class="ob-manual-live-decision-packet-chip red">No auto execution</span>
          </div>
        </div>

        <div class="ob-manual-live-decision-packet-stat-grid">
          ${card("Packet", safeText(state.packet_id, "packet"))}
          ${card("Sections", String(sections.length))}
          ${card("Decision", safeText(state.current_result, "pending"))}
          ${card("Receipt", receipt.vault_ready ? "vault-ready placeholder" : "draft")}
          ${card("Order", "none")}
        </div>

        <div class="ob-manual-live-decision-packet-grid">
          <div>
            <div class="ob-manual-live-decision-packet-card">
              <span>Packet purpose</span>
              <strong>One owner-review packet before any manual broker checklist.</strong>
              <div class="ob-manual-live-decision-packet-callout">
                <strong>Includes:</strong><br>
                Command card, account experience, safety preflight, Tower clearance, broker checklist preview, receipt preview, and owner decision.
              </div>
              <div class="ob-manual-live-decision-packet-boundary">
                <strong>Boundary:</strong><br>
                The packet does not create an order, broker call, hybrid submit, automation, or public proof.
              </div>
            </div>

            <div class="ob-manual-live-decision-packet-card" style="margin-top: 11px;">
              <span>Owner decisions</span>
              <div class="ob-manual-live-decision-packet-action-row">
                <span class="ob-manual-live-decision-packet-action">Approve checklist</span>
                <span class="ob-manual-live-decision-packet-action">Reject</span>
                <span class="ob-manual-live-decision-packet-action">Watch</span>
                <span class="ob-manual-live-decision-packet-action">Submit disabled</span>
              </div>
              <div class="ob-manual-live-decision-packet-list" style="margin-top: 10px;">
                ${Object.keys(actions).map((key) => actionRow(key, actions[key])).join("")}
              </div>
            </div>

            <div class="ob-manual-live-decision-packet-card" style="margin-top: 11px;">
              <span>Receipt preview</span>
              <strong>${safeText(receipt.receipt_type, "manual_live_decision_packet_receipt")}</strong>
              <div class="ob-manual-live-decision-packet-callout">
                <strong>Vault-ready:</strong> ${receipt.vault_ready ? "yes" : "no"}<br>
                <strong>Direct Vault upload:</strong> ${receipt.no_direct_vault_upload ? "disabled" : "unknown"}<br>
                <strong>Public exposure:</strong> ${safeText(receipt.public_exposure, "never_public")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-decision-packet-section">
              <div class="ob-manual-live-decision-packet-section-title">Packet sections</div>
              <div class="ob-manual-live-decision-packet-list">${sections.map(sectionRow).join("")}</div>
            </div>

            <div class="ob-manual-live-decision-packet-section">
              <div class="ob-manual-live-decision-packet-section-title">Blocked actions</div>
              <div class="ob-manual-live-decision-packet-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-decision-packet-callout">
          <strong>Source:</strong><br>
          GP006 ties GP001 account experience, GP002 operating room, GP003 receipts, GP004 lock polish, and GP005 safety preflight into one owner-review packet.
        </div>

        <div class="ob-manual-live-decision-packet-boundary">
          <strong>Boundary:</strong><br>
          Manual Live owner-only. Beta Survey/Paper only. No broker API. No auto execution. No hybrid submit. No automated live. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveDecisionPacketPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const preflightPanel = document.getElementById("obManualLiveSafetyPreflightPanel");
    const polishPanel = document.getElementById("obPrivateBetaTowerLockPolishPanel");
    const receiptsPanel = document.getElementById("obReceiptsReviewFoundationPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (preflightPanel && preflightPanel.parentNode) preflightPanel.insertAdjacentElement("afterend", panel);
    else if (polishPanel && polishPanel.parentNode) polishPanel.insertAdjacentElement("afterend", panel);
    else if (receiptsPanel && receiptsPanel.parentNode) receiptsPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = packetState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-006-manual-live-decision-packet", "ready");
    document.body.setAttribute("data-ob-decision-packet-required", "true");
    document.body.setAttribute("data-ob-safety-preflight-required", "true");
    document.body.setAttribute("data-ob-checklist-only-no-order", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_006_DECISION_PACKET_STATE = {
      version: VERSION,
      status: packetState.status,
      fallbackActive: packetState.fallbackActive,
      sectionCount: payload.packet_sections.length,
      decisionPacketRequired: true,
      checklistOnlyNoOrder: true,
      noBrokerApi: true,
      noAutoExecution: true,
      hybridLocked: true,
      automatedLocked: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchPacket();
    }, 3660);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_DECISION_PACKET_GP006_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return packetState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchPacket,
    renderPanel,
    setFlags
  };
})();
