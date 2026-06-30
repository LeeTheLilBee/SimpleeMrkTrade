// OB_GIANT_PACK_012_REHEARSAL_RECORD_PERSISTENCE_CONTRACT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_012_REHEARSAL_RECORD_PERSISTENCE_CONTRACT";
  const ENDPOINT = "/ob/rehearsal-record-contracts.json";

  // SMOKE MARKERS
  // Rehearsal Record Persistence Contract
  // rehearsal session record
  // rehearsal candidate record
  // rehearsal decision record
  // rehearsal preflight record
  // rehearsal checklist record
  // rehearsal fill record
  // rehearsal not placed record
  // rehearsal monitor record
  // rehearsal close record
  // rehearsal final review record
  // rehearsal receipt record
  // session id required
  // linked receipts required
  // linked packet required
  // blocked reason field
  // confidence label field
  // freshness label field
  // sensitivity field
  // vault ready field
  // owner-only persistence contract
  // contract only no database write
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let contractState = {
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
    const sharedFields = [
      "record_id",
      "session_id",
      "source_app",
      "mission_account",
      "mode",
      "owner_action",
      "timestamp",
      "status",
      "linked_receipts",
      "linked_packet",
      "blocked_reason",
      "confidence_label",
      "freshness_label",
      "sensitivity",
      "vault_ready"
    ];

    return {
      version: VERSION,
      source: "ob_giant_pack_012_safe_fallback",
      contract_state: {
        contract_id: "ob_rehearsal_record_persistence_contract_001",
        label: "Rehearsal Record Persistence Contract",
        status: "contract_ready",
        purpose: "Define future-persistent record shapes for every owner rehearsal step.",
        owner_only: true,
        contract_only_no_database_write: true,
        no_broker_data: true,
        no_order_data_from_broker: true
      },
      shared_record_fields: sharedFields,
      record_contracts: [
        {
          contract_id: "rehearsal_session_record",
          label: "Rehearsal Session Record",
          purpose: "Top-level session for one owner Manual Live L1 rehearsal.",
          required_fields: sharedFields.concat([
            "session_type",
            "selected_candidate_id",
            "selected_mission_account",
            "started_at",
            "completed_at",
            "completion_status",
            "current_step",
            "owner_readiness_label"
          ]),
          linked_gp: "GP011",
          status: "ready"
        },
        {
          contract_id: "rehearsal_candidate_record",
          label: "Rehearsal Candidate Record",
          purpose: "Stores fake/demo candidate selected for rehearsal.",
          required_fields: sharedFields.concat([
            "candidate_id",
            "symbol",
            "asset_type",
            "strategy",
            "side",
            "risk_label",
            "demo_static",
            "candidate_source"
          ]),
          linked_gp: "GP011",
          status: "ready"
        },
        {
          contract_id: "rehearsal_decision_record",
          label: "Rehearsal Decision Record",
          purpose: "Stores approve/reject/watch rehearsal decision.",
          required_fields: sharedFields.concat([
            "decision",
            "decision_reason",
            "decision_packet_id",
            "tower_clearance_state",
            "creates_checklist_receipt_only"
          ]),
          linked_gp: "GP006",
          status: "ready"
        },
        {
          contract_id: "rehearsal_preflight_record",
          label: "Rehearsal Preflight Record",
          purpose: "Stores safety preflight checklist results.",
          required_fields: sharedFields.concat([
            "account_policy_state",
            "mode_permission_state",
            "kill_switch_state",
            "data_freshness_state",
            "source_confidence_state",
            "exposure_state",
            "protected_floor_state",
            "owner_step_up_state"
          ]),
          linked_gp: "GP005",
          status: "ready"
        },
        {
          contract_id: "rehearsal_checklist_record",
          label: "Rehearsal Checklist Record",
          purpose: "Stores manual broker checklist rehearsal answers.",
          required_fields: sharedFields.concat([
            "broker_account_confirmed",
            "symbol_contract_confirmed",
            "action_side_confirmed",
            "limit_order_confirmed",
            "entry_limit",
            "do_not_enter_above",
            "stop_plan",
            "target_plan",
            "spread_liquidity_confirmed",
            "options_approval_confirmed",
            "pdt_margin_cash_acknowledged"
          ]),
          linked_gp: "GP007",
          status: "ready"
        },
        {
          contract_id: "rehearsal_fill_record",
          label: "Rehearsal Fill Record",
          purpose: "Stores fake owner-entered fill details.",
          required_fields: sharedFields.concat([
            "fill_time",
            "fill_price",
            "quantity",
            "symbol_or_contract",
            "order_type",
            "manual_broker_confirmation",
            "commission_or_fee_optional",
            "owner_note"
          ]),
          linked_gp: "GP007",
          status: "ready"
        },
        {
          contract_id: "rehearsal_not_placed_record",
          label: "Rehearsal Not-Placed Record",
          purpose: "Stores fake not-placed reason and blocker.",
          required_fields: sharedFields.concat([
            "not_placed_reason",
            "price_moved",
            "spread_too_wide",
            "broker_restriction",
            "owner_changed_mind",
            "tower_gate_blocked",
            "data_stale",
            "liquidity_failed",
            "manual_note"
          ]),
          linked_gp: "GP007",
          status: "ready"
        },
        {
          contract_id: "rehearsal_monitor_record",
          label: "Rehearsal Monitor Record",
          purpose: "Stores fake position monitor state and exit alert state.",
          required_fields: sharedFields.concat([
            "position_id",
            "entry_receipt_linked",
            "fill_receipt_linked",
            "stop_target_plan_visible",
            "manual_risk_watch_state",
            "exit_alert_state",
            "exit_alert_reason",
            "tower_kill_switch_watch",
            "data_freshness_watch"
          ]),
          linked_gp: "GP008",
          status: "ready"
        },
        {
          contract_id: "rehearsal_close_record",
          label: "Rehearsal Close Record",
          purpose: "Stores fake manual close confirmation.",
          required_fields: sharedFields.concat([
            "close_decision",
            "close_reason",
            "close_time",
            "close_price",
            "close_quantity",
            "symbol_or_contract",
            "manual_broker_confirmation",
            "realized_result",
            "owner_note"
          ]),
          linked_gp: "GP008",
          status: "ready"
        },
        {
          contract_id: "rehearsal_final_review_record",
          label: "Rehearsal Final Review Record",
          purpose: "Stores final review, rule review, discipline, and lesson fields.",
          required_fields: sharedFields.concat([
            "realized_result_summary",
            "setup_quality_review",
            "entry_quality_review",
            "exit_quality_review",
            "risk_management_review",
            "rule_violation_review",
            "discipline_score_placeholder",
            "lesson_record",
            "owner_final_notes"
          ]),
          linked_gp: "GP009",
          status: "ready"
        },
        {
          contract_id: "rehearsal_receipt_record",
          label: "Rehearsal Receipt Record",
          purpose: "Stores final rehearsal receipt preview and Review Center handoff.",
          required_fields: sharedFields.concat([
            "receipt_id",
            "receipt_type",
            "rehearsal_result",
            "review_center_destination",
            "vault_destination_placeholder",
            "public_exposure",
            "no_direct_vault_upload"
          ]),
          linked_gp: "GP003_GP009_GP011",
          status: "ready"
        }
      ],
      record_relationships: [
        {
          relationship_id: "session_links_all_records",
          label: "Session links all records",
          from: "rehearsal_session_record",
          to: "all_rehearsal_step_records",
          key: "session_id",
          status: "required"
        },
        {
          relationship_id: "candidate_links_decision",
          label: "Candidate links decision",
          from: "rehearsal_candidate_record",
          to: "rehearsal_decision_record",
          key: "candidate_id",
          status: "required"
        },
        {
          relationship_id: "decision_links_preflight",
          label: "Decision links preflight",
          from: "rehearsal_decision_record",
          to: "rehearsal_preflight_record",
          key: "linked_packet",
          status: "required"
        },
        {
          relationship_id: "fill_links_monitor",
          label: "Fill links monitor",
          from: "rehearsal_fill_record",
          to: "rehearsal_monitor_record",
          key: "linked_receipts",
          status: "required"
        },
        {
          relationship_id: "close_links_final_review",
          label: "Close links final review",
          from: "rehearsal_close_record",
          to: "rehearsal_final_review_record",
          key: "linked_receipts",
          status: "required"
        },
        {
          relationship_id: "final_review_links_receipt",
          label: "Final review links receipt",
          from: "rehearsal_final_review_record",
          to: "rehearsal_receipt_record",
          key: "receipt_id",
          status: "required"
        }
      ],
      persistence_rules: [
        {
          rule_id: "contract_only_no_database_write",
          label: "Contract only",
          rule: "GP012 defines record shapes only; it does not write to database or disk.",
          status: "locked"
        },
        {
          rule_id: "owner_only_records",
          label: "Owner-only records",
          rule: "Rehearsal records are owner-only and not visible to beta users.",
          status: "locked"
        },
        {
          rule_id: "fake_demo_data_only",
          label: "Fake/demo data only",
          rule: "Rehearsal records must not imply real broker execution.",
          status: "locked"
        },
        {
          rule_id: "vault_ready_no_direct_upload",
          label: "Vault-ready, no direct upload",
          rule: "Records may be Vault-ready placeholders, but OB does not upload directly to Vault.",
          status: "locked"
        },
        {
          rule_id: "review_center_destination",
          label: "Review Center destination",
          rule: "Records are shaped for Review Center rollup in the next pack.",
          status: "ready"
        }
      ],
      blocked_actions: [
        "write_rehearsal_database_now",
        "store_real_broker_data",
        "read_broker_account",
        "submit_order_from_ob",
        "auto_execute",
        "publish_rehearsal",
        "create_public_proof",
        "upload_direct_to_vault",
        "show_rehearsal_records_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        contract_only_no_database_write: true,
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
      contract_state: { ...(fallback.contract_state || {}), ...(safe.contract_state || {}) },
      shared_record_fields: Array.isArray(safe.shared_record_fields) ? safe.shared_record_fields : fallback.shared_record_fields,
      record_contracts: Array.isArray(safe.record_contracts) ? safe.record_contracts : fallback.record_contracts,
      record_relationships: Array.isArray(safe.record_relationships) ? safe.record_relationships : fallback.record_relationships,
      persistence_rules: Array.isArray(safe.persistence_rules) ? safe.persistence_rules : fallback.persistence_rules,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        contract_only_no_database_write: true,
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
    window.OB_REHEARSAL_RECORD_CONTRACTS_GP012 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      rehearsal_record_contracts_gp012: normalized,
      owner_rehearsal_only: true,
      contract_only_no_database_write: true,
      fake_candidate_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_order_submit: true,
      no_auto_execution: true,
      no_direct_vault_upload: true,
      live_auto_locked: true
    };
    window.dispatchEvent(new CustomEvent("obRehearsalRecordContractsUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchContracts() {
    contractState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      contractState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        contractState.status = "ready";
        contractState.source = normalized.source || "server";
        contractState.payload = normalized;
        contractState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        contractState.status = "guarded_fallback";
        contractState.source = "guarded_fallback";
        contractState.payload = fallback;
        contractState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      contractState.status = "error_fallback";
      contractState.source = "error_fallback";
      contractState.payload = fallback;
      contractState.fallbackActive = true;
      contractState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return contractState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("no ") || text.includes("contract only")) return "red";
    if (text.includes("ready")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-rehearsal-record-contracts-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-rehearsal-record-contracts-row">
        <div class="ob-rehearsal-record-contracts-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.contract_id || item.relationship_id || item.rule_id, "Item")}</strong>
          <span>${safeText(item.contract_id || item.relationship_id || item.rule_id || item.linked_gp || "record", "record")}</span>
        </div>
        <span>${safeText(item.purpose || item.rule || item.key || "detail", "detail")}</span>
        <div class="ob-rehearsal-record-contracts-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function fieldRows(fields) {
    return (fields || []).map((field) => `
      <div class="ob-rehearsal-record-contracts-row">
        <div class="ob-rehearsal-record-contracts-dot">F</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>shared field</span>
        </div>
        <span>Required across rehearsal persistence records.</span>
        <div class="ob-rehearsal-record-contracts-status gold">required</div>
      </div>
    `).join("");
  }

  function blockedRow(item) {
    return `
      <div class="ob-rehearsal-record-contracts-row">
        <div class="ob-rehearsal-record-contracts-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP012 persistence-contract boundaries.</span>
        <div class="ob-rehearsal-record-contracts-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = contractState.payload || buildFallbackPayload();
    const state = payload.contract_state || {};
    const shared = Array.isArray(payload.shared_record_fields) ? payload.shared_record_fields : [];
    const contracts = Array.isArray(payload.record_contracts) ? payload.record_contracts : [];
    const relationships = Array.isArray(payload.record_relationships) ? payload.record_relationships : [];
    const rules = Array.isArray(payload.persistence_rules) ? payload.persistence_rules : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-rehearsal-record-contracts-panel" id="obRehearsalRecordContractsPanel" data-ob-giant-pack-012="true">
        <div class="ob-rehearsal-record-contracts-head">
          <div>
            <div class="ob-label">OB Giant Pack 012 · Rehearsal Record Contracts</div>
            <div class="ob-rehearsal-record-contracts-title">Persistence Contract Layer</div>
            <div class="ob-rehearsal-record-contracts-subtitle">
              ${safeText(contractState.status, "booting")} · ${safeText(state.status, "contract_ready")} · defines record shapes, no database write.
            </div>
          </div>
          <div class="ob-rehearsal-record-contracts-chip-row">
            <span class="ob-rehearsal-record-contracts-chip green">Record contracts</span>
            <span class="ob-rehearsal-record-contracts-chip gold">Owner-only</span>
            <span class="ob-rehearsal-record-contracts-chip red">No DB write</span>
            <span class="ob-rehearsal-record-contracts-chip red">No broker data</span>
          </div>
        </div>

        <div class="ob-rehearsal-record-contracts-stat-grid">
          ${card("Contracts", String(contracts.length))}
          ${card("Shared fields", String(shared.length))}
          ${card("Relationships", String(relationships.length))}
          ${card("Rules", String(rules.length))}
          ${card("Write", "disabled")}
        </div>

        <div class="ob-rehearsal-record-contracts-grid">
          <div>
            <div class="ob-rehearsal-record-contracts-card">
              <span>Purpose</span>
              <strong>Give every owner rehearsal step a future-persistent record shape.</strong>
              <div class="ob-rehearsal-record-contracts-callout">
                <strong>Contract covers:</strong><br>
                Session, candidate, decision, preflight, checklist, fill, not-placed, monitor, close, final review, and receipt records.
              </div>
              <div class="ob-rehearsal-record-contracts-boundary">
                <strong>Boundary:</strong><br>
                GP012 does not write a database, store real broker data, submit orders, or upload to Vault.
              </div>
            </div>

            <div class="ob-rehearsal-record-contracts-card" style="margin-top: 11px;">
              <span>Shared fields</span>
              <div class="ob-rehearsal-record-contracts-list">${fieldRows(shared)}</div>
            </div>
          </div>

          <div>
            <div class="ob-rehearsal-record-contracts-section">
              <div class="ob-rehearsal-record-contracts-section-title">Record contracts</div>
              <div class="ob-rehearsal-record-contracts-list">${contracts.map((item, index) => row(item, index)).join("")}</div>
            </div>

            <div class="ob-rehearsal-record-contracts-section">
              <div class="ob-rehearsal-record-contracts-section-title">Record relationships</div>
              <div class="ob-rehearsal-record-contracts-list">${relationships.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-rehearsal-record-contracts-section">
              <div class="ob-rehearsal-record-contracts-section-title">Persistence rules</div>
              <div class="ob-rehearsal-record-contracts-list">${rules.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-rehearsal-record-contracts-section">
              <div class="ob-rehearsal-record-contracts-section-title">Blocked actions</div>
              <div class="ob-rehearsal-record-contracts-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-rehearsal-record-contracts-callout">
          <strong>Next handoff:</strong><br>
          GP013 can now build the Review Center rehearsal command board using these record contracts.
        </div>

        <div class="ob-rehearsal-record-contracts-boundary">
          <strong>Still locked:</strong><br>
          Contract only. No database write. No real broker data. No broker API. No order submit. No public proof. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obRehearsalRecordContractsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const rehearsalPanel = document.getElementById("obOwnerRehearsalEnginePanel");
    const readinessPanel = document.getElementById("obManualLiveL1ReadinessPanel");
    const finalReviewPanel = document.getElementById("obFinalReviewPerformancePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (rehearsalPanel && rehearsalPanel.parentNode) rehearsalPanel.insertAdjacentElement("afterend", panel);
    else if (readinessPanel && readinessPanel.parentNode) readinessPanel.insertAdjacentElement("afterend", panel);
    else if (finalReviewPanel && finalReviewPanel.parentNode) finalReviewPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = contractState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-012-rehearsal-record-contracts", "ready");
    document.body.setAttribute("data-ob-contract-only-no-database-write", "true");
    document.body.setAttribute("data-ob-owner-rehearsal-only", "true");
    document.body.setAttribute("data-ob-fake-candidate-only", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_012_REHEARSAL_RECORD_CONTRACTS_STATE = {
      version: VERSION,
      status: contractState.status,
      fallbackActive: contractState.fallbackActive,
      recordContractCount: payload.record_contracts.length,
      sharedFieldCount: payload.shared_record_fields.length,
      relationshipCount: payload.record_relationships.length,
      contractOnlyNoDatabaseWrite: true,
      ownerRehearsalOnly: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchContracts();
    }, 4620);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_REHEARSAL_RECORD_CONTRACTS_GP012_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return contractState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchContracts,
    renderPanel,
    setFlags
  };
})();
