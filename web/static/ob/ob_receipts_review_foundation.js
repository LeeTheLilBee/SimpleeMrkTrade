// OB_GIANT_PACK_003_RECEIPTS_REVIEW_CENTER_FOUNDATION_JS

(function () {
  const VERSION = "OB_GIANT_PACK_003_RECEIPTS_REVIEW_CENTER_FOUNDATION";
  const ENDPOINT = "/ob/receipts-review-foundation.json";

  // SMOKE MARKERS
  // Receipts Review Center Foundation
  // Manual Live receipt timeline
  // candidate reviewed receipt
  // owner approved manual placement receipt
  // owner rejected trade receipt
  // owner watched snoozed candidate receipt
  // broker checklist receipt
  // fill confirmation receipt
  // order not placed receipt
  // exit alert receipt
  // close confirmation receipt
  // final review saved receipt
  // mission account milestone receipt
  // capital deployment trigger receipt
  // timestamp
  // mission account
  // symbol
  // strategy
  // risk state
  // Tower permission state
  // owner action
  // result
  // Vault-ready flag
  // Vault destination collection
  // Review Center timeline
  // decision history
  // approved rejected trades
  // no broker API
  // no auto execution
  // Manual Live owner-only
  // Hybrid locked
  // Automated locked
  // Live Auto Locked

  let receiptState = {
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

  function receiptEvents() {
    return [
      {
        receipt_id: "ob_ml1_receipt_candidate_reviewed",
        event_type: "candidate_reviewed",
        timestamp: "placeholder_timestamp",
        mission_account: "Personal OB Account",
        symbol: "MU",
        strategy: "options-first candidate review",
        risk_state: "manual_review_required",
        tower_permission_state: "owner_review_required",
        owner_action: "reviewed command card",
        result: "pending decision",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/decision-receipts",
        review_center_section: "Manual Live timeline"
      },
      {
        receipt_id: "ob_ml1_receipt_owner_approved_manual",
        event_type: "owner_approved_manual_placement",
        timestamp: "placeholder_timestamp",
        mission_account: "Personal OB Account",
        symbol: "MU",
        strategy: "options-first candidate review",
        risk_state: "broker_checklist_required",
        tower_permission_state: "manual_live_owner_only",
        owner_action: "approve for manual broker checklist",
        result: "checklist created only",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/approval-receipts",
        review_center_section: "Approved trades"
      },
      {
        receipt_id: "ob_ml1_receipt_owner_rejected",
        event_type: "owner_rejected_trade",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "candidate symbol",
        strategy: "candidate strategy",
        risk_state: "rejected_by_owner",
        tower_permission_state: "no execution permission created",
        owner_action: "reject",
        result: "trade blocked",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/rejection-receipts",
        review_center_section: "Rejected trades"
      },
      {
        receipt_id: "ob_ml1_receipt_owner_watched",
        event_type: "owner_watched_snoozed_candidate",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "candidate symbol",
        strategy: "candidate strategy",
        risk_state: "watch_only",
        tower_permission_state: "read_only",
        owner_action: "watch",
        result: "candidate observed only",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/watch-receipts",
        review_center_section: "Watch / snooze history"
      },
      {
        receipt_id: "ob_ml1_receipt_broker_checklist",
        event_type: "broker_checklist_created",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "candidate symbol",
        strategy: "candidate strategy",
        risk_state: "checklist_only",
        tower_permission_state: "broker_api_disabled",
        owner_action: "prepare manual broker checklist",
        result: "no order submitted",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/broker-checklist-receipts",
        review_center_section: "Broker checklist history"
      },
      {
        receipt_id: "ob_ml1_receipt_fill_confirmed",
        event_type: "fill_confirmed",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "filled symbol",
        strategy: "filled strategy",
        risk_state: "owner_entered_fill",
        tower_permission_state: "receipt_required",
        owner_action: "confirm fill after manual broker action",
        result: "position tracking placeholder",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/fill-confirmation-receipts",
        review_center_section: "Fill confirmations"
      },
      {
        receipt_id: "ob_ml1_receipt_order_not_placed",
        event_type: "order_not_placed",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "candidate symbol",
        strategy: "candidate strategy",
        risk_state: "not_placed",
        tower_permission_state: "no execution permission created",
        owner_action: "record order not placed",
        result: "missed/not-placed reason required",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/order-not-placed-receipts",
        review_center_section: "Missed / not placed"
      },
      {
        receipt_id: "ob_ml1_receipt_exit_alert",
        event_type: "exit_alert_issued",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "open position symbol",
        strategy: "open position strategy",
        risk_state: "exit_review_required",
        tower_permission_state: "manual_close_only",
        owner_action: "review exit alert",
        result: "owner close decision pending",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/exit-alert-receipts",
        review_center_section: "Exit alerts"
      },
      {
        receipt_id: "ob_ml1_receipt_close_confirmed",
        event_type: "close_confirmed",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "closed symbol",
        strategy: "closed strategy",
        risk_state: "closed_by_owner",
        tower_permission_state: "review_required",
        owner_action: "confirm manual close",
        result: "final review pending",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/close-confirmation-receipts",
        review_center_section: "Close confirmations"
      },
      {
        receipt_id: "ob_ml1_receipt_final_review_saved",
        event_type: "final_review_saved",
        timestamp: "placeholder_timestamp",
        mission_account: "selected OB account",
        symbol: "reviewed symbol",
        strategy: "reviewed strategy",
        risk_state: "lesson_recorded",
        tower_permission_state: "review_center_saved",
        owner_action: "save final review notes",
        result: "lesson added to review loop",
        vault_ready: true,
        vault_destination_collection: "ob/manual-live/final-review-receipts",
        review_center_section: "Final reviews"
      },
      {
        receipt_id: "ob_mission_receipt_milestone",
        event_type: "mission_account_milestone_reached",
        timestamp: "placeholder_timestamp",
        mission_account: "ATM OB Account",
        symbol: "account-level event",
        strategy: "mission capital progress",
        risk_state: "deployment_zone_review",
        tower_permission_state: "capital_safety_required",
        owner_action: "review milestone",
        result: "Tower deployment gate required",
        vault_ready: true,
        vault_destination_collection: "ob/mission-account/milestone-receipts",
        review_center_section: "Mission milestones"
      },
      {
        receipt_id: "ob_mission_receipt_capital_deployment_trigger",
        event_type: "capital_deployment_trigger_reached",
        timestamp: "placeholder_timestamp",
        mission_account: "ATM OB Account",
        symbol: "account-level event",
        strategy: "capital deployment trigger",
        risk_state: "risk_reduce_or_pause",
        tower_permission_state: "Tower approval required",
        owner_action: "request deployment review",
        result: "withdrawal/deployment not automatic",
        vault_ready: true,
        vault_destination_collection: "ob/mission-account/deployment-trigger-receipts",
        review_center_section: "Capital deployment triggers"
      }
    ];
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_003_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipt_standard: "Packs 396-450 Tower ecosystem foundation",
        capital_safety: "Packs 451-500 Tower capital safety controls",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      receipt_schema: {
        required_fields: [
          "receipt_id",
          "event_type",
          "timestamp",
          "mission_account",
          "symbol",
          "strategy",
          "risk_state",
          "tower_permission_state",
          "owner_action",
          "result",
          "vault_ready",
          "vault_destination_collection",
          "review_center_section"
        ],
        sensitivity: "owner_only",
        public_exposure: "never_public",
        vault_ready_default: true
      },
      receipt_events: receiptEvents(),
      review_center_sections: [
        {
          section_id: "manual_live_timeline",
          label: "Manual Live timeline",
          purpose: "Show the story from candidate review through final review.",
          readiness: "foundation_ready"
        },
        {
          section_id: "decision_history",
          label: "Decision history",
          purpose: "Track approve, reject, watch, not-placed, fill, exit, and close decisions.",
          readiness: "foundation_ready"
        },
        {
          section_id: "approved_rejected_trades",
          label: "Approved / rejected trades",
          purpose: "Separate owner-approved manual checklist actions from rejected candidates.",
          readiness: "foundation_ready"
        },
        {
          section_id: "fill_exit_close_confirmations",
          label: "Fill / exit / close confirmations",
          purpose: "Capture owner-entered manual broker confirmations.",
          readiness: "placeholder_ready"
        },
        {
          section_id: "mission_milestones",
          label: "Mission account milestones",
          purpose: "Show ATM/apartment/trust/business capital readiness events.",
          readiness: "placeholder_ready"
        },
        {
          section_id: "vault_ready_receipts",
          label: "Vault-ready receipts",
          purpose: "Prepare future Vault handoff without direct upload.",
          readiness: "vault_ready_placeholder"
        }
      ],
      boundaries: {
        private_beta_only: true,
        owner_only_receipts: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_direct_vault_upload: true,
        no_broker_api: true,
        no_auto_execution: true,
        manual_live_owner_only: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true,
        review_center_only: true,
        vault_ready_placeholder_only: true
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
      receipt_schema: { ...(fallback.receipt_schema || {}), ...(safe.receipt_schema || {}) },
      receipt_events: Array.isArray(safe.receipt_events) ? safe.receipt_events : fallback.receipt_events,
      review_center_sections: Array.isArray(safe.review_center_sections) ? safe.review_center_sections : fallback.review_center_sections,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_only_receipts: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_direct_vault_upload: true,
        no_broker_api: true,
        no_auto_execution: true,
        manual_live_owner_only: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true,
        review_center_only: true,
        vault_ready_placeholder_only: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_RECEIPTS_REVIEW_FOUNDATION_GP003 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      receipts_review_foundation_gp003: normalized,
      receipt_schema_ready: true,
      manual_live_receipts_ready: true,
      vault_ready_placeholder_only: true,
      no_direct_vault_upload: true,
      broker_api_enabled: false,
      auto_execution_enabled: false,
      hybrid_locked: true,
      automated_locked: true
    };

    window.dispatchEvent(new CustomEvent("obReceiptsReviewFoundationUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchReceiptsReviewFoundation() {
    receiptState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      receiptState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        receiptState.status = "ready";
        receiptState.source = normalized.source || "server";
        receiptState.payload = normalized;
        receiptState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        receiptState.status = "guarded_fallback";
        receiptState.source = "guarded_fallback";
        receiptState.payload = fallback;
        receiptState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      receiptState.status = "error_fallback";
      receiptState.source = "error_fallback";
      receiptState.payload = fallback;
      receiptState.fallbackActive = true;
      receiptState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return receiptState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("never") || text.includes("required")) return "red";
    if (text.includes("vault") || text.includes("placeholder") || text.includes("review")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-receipts-review-foundation-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function receiptRow(item, index) {
    return `
      <div class="ob-receipts-review-foundation-row">
        <div class="ob-receipts-review-foundation-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.event_type, "receipt_event").replaceAll("_", " ")}</strong>
          <span>${safeText(item.receipt_id, "receipt_id")}</span>
        </div>
        <span>
          ${safeText(item.mission_account, "account")} · ${safeText(item.symbol, "symbol")} · ${safeText(item.strategy, "strategy")}<br>
          Tower: ${safeText(item.tower_permission_state, "state")} · Owner: ${safeText(item.owner_action, "action")}<br>
          Vault: ${safeText(item.vault_destination_collection, "collection")}
        </span>
        <div class="ob-receipts-review-foundation-status ${item.vault_ready ? "green" : "gold"}">${item.vault_ready ? "vault ready" : "draft"}</div>
      </div>
    `;
  }

  function sectionRow(item, index) {
    return `
      <div class="ob-receipts-review-foundation-row">
        <div class="ob-receipts-review-foundation-dot">R</div>
        <div>
          <strong>${safeText(item.label, "Review section")}</strong>
          <span>${safeText(item.section_id, "section")}</span>
        </div>
        <span>${safeText(item.purpose, "Purpose pending.")}</span>
        <div class="ob-receipts-review-foundation-status ${statusClass(item.readiness)}">${safeText(item.readiness, "ready")}</div>
      </div>
    `;
  }

  function schemaRow(field, index) {
    return `
      <div class="ob-receipts-review-foundation-row">
        <div class="ob-receipts-review-foundation-dot">S</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>receipt schema</span>
        </div>
        <span>Required on serious Manual Live / mission account receipt events.</span>
        <div class="ob-receipts-review-foundation-status gold">required</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = receiptState.payload || buildFallbackPayload();
    const events = Array.isArray(payload.receipt_events) ? payload.receipt_events : [];
    const sections = Array.isArray(payload.review_center_sections) ? payload.review_center_sections : [];
    const schema = payload.receipt_schema || {};
    const fields = Array.isArray(schema.required_fields) ? schema.required_fields : [];

    const vaultReadyCount = events.filter((event) => event && event.vault_ready).length;

    return `
      <div class="ob-receipts-review-foundation-panel" id="obReceiptsReviewFoundationPanel" data-ob-giant-pack-003="true">
        <div class="ob-receipts-review-foundation-head">
          <div>
            <div class="ob-label">OB Giant Pack 003 · Receipts + Review Center</div>
            <div class="ob-receipts-review-foundation-title">Manual Live Receipts Foundation</div>
            <div class="ob-receipts-review-foundation-subtitle">
              ${safeText(receiptState.status, "booting")} · Serious Manual Live actions become reviewable, Vault-ready records.
            </div>
          </div>
          <div class="ob-receipts-review-foundation-chip-row">
            <span class="ob-receipts-review-foundation-chip green">Receipt schema ready</span>
            <span class="ob-receipts-review-foundation-chip gold">Vault-ready placeholder</span>
            <span class="ob-receipts-review-foundation-chip red">No public receipts</span>
            <span class="ob-receipts-review-foundation-chip red">No direct upload</span>
          </div>
        </div>

        <div class="ob-receipts-review-foundation-stat-grid">
          ${card("Receipt events", String(events.length))}
          ${card("Vault-ready", String(vaultReadyCount))}
          ${card("Review sections", String(sections.length))}
          ${card("Schema fields", String(fields.length))}
          ${card("Execution", "none")}
        </div>

        <div class="ob-receipts-review-foundation-grid">
          <div>
            <div class="ob-receipts-review-foundation-card">
              <span>Receipt standard</span>
              <strong>Every serious OB action gets a reviewable receipt.</strong>
              <div class="ob-receipts-review-foundation-callout">
                <strong>Review Center purpose:</strong><br>
                Explain what happened, why it happened, what the owner decided, what Tower allowed or blocked, and what Vault should store later.
              </div>
              <div class="ob-receipts-review-foundation-boundary">
                <strong>Boundary:</strong><br>
                Vault-ready does not mean direct Vault upload. Tower still controls upload/intake later.
              </div>
            </div>

            <div class="ob-receipts-review-foundation-card" style="margin-top: 11px;">
              <span>Required receipt fields</span>
              <div class="ob-receipts-review-foundation-list">${fields.map(schemaRow).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-receipts-review-foundation-section">
              <div class="ob-receipts-review-foundation-section-title">Manual Live + mission receipt events</div>
              <div class="ob-receipts-review-foundation-list">${events.map(receiptRow).join("")}</div>
            </div>

            <div class="ob-receipts-review-foundation-section">
              <div class="ob-receipts-review-foundation-section-title">Review Center sections</div>
              <div class="ob-receipts-review-foundation-list">${sections.map(sectionRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-receipts-review-foundation-callout">
          <strong>Source:</strong><br>
          Receipts use Tower ecosystem foundation standards, OB Manual Live Level 1 workflow, and Tower capital safety controls.
        </div>

        <div class="ob-receipts-review-foundation-boundary">
          <strong>Boundary:</strong><br>
          No broker API. No auto execution. No public proof. No public receipts. Hybrid locked. Automated locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obReceiptsReviewFoundationPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const manualPanel = document.getElementById("obManualLiveLevel1Panel");
    const accountPanel = document.getElementById("obAccountExperiencePanel");
    const reviewAnchor = document.querySelector("[data-ob-review-center]");
    const dashboardFocus = document.querySelector("[data-ob-dashboard-focus]");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (manualPanel && manualPanel.parentNode) manualPanel.insertAdjacentElement("afterend", panel);
    else if (accountPanel && accountPanel.parentNode) accountPanel.insertAdjacentElement("afterend", panel);
    else if (reviewAnchor && reviewAnchor.parentNode) reviewAnchor.insertAdjacentElement("afterend", panel);
    else if (dashboardFocus && dashboardFocus.parentNode) dashboardFocus.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = receiptState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-003-receipts-review", "ready");
    document.body.setAttribute("data-ob-receipt-schema-ready", "true");
    document.body.setAttribute("data-ob-vault-ready-placeholder-only", "true");
    document.body.setAttribute("data-ob-no-public-receipts", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-broker-api-enabled", "false");
    document.body.setAttribute("data-ob-auto-execution-enabled", "false");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");

    window.OB_GIANT_PACK_003_RECEIPTS_REVIEW_STATE = {
      version: VERSION,
      status: receiptState.status,
      fallbackActive: receiptState.fallbackActive,
      receiptEventCount: payload.receipt_events.length,
      reviewSectionCount: payload.review_center_sections.length,
      vaultReadyPlaceholderOnly: true,
      noPublicReceipts: true,
      noDirectVaultUpload: true,
      brokerApiEnabled: false,
      autoExecutionEnabled: false,
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
      fetchReceiptsReviewFoundation();
    }, 3180);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_RECEIPTS_REVIEW_FOUNDATION_GP003_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return receiptState; },
    receiptEvents,
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchReceiptsReviewFoundation,
    renderPanel,
    setFlags
  };
})();
