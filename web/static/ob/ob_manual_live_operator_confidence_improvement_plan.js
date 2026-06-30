// OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_JS

(function () {
  const VERSION = "OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN";
  const ENDPOINT = "/ob/manual-live-operator-confidence-improvement-plan.json";

  // SMOKE MARKERS
  // Manual Live Operator Confidence Improvement Plan
  // manual live operator confidence improvement plan
  // confidence improvement plan
  // operator improvement plan
  // ordered improvement tasks
  // checklist fill improvement task
  // fake fill not-placed improvement task
  // confusing checklist improvement task
  // emotional rush improvement task
  // scenario repetition plan
  // confidence gap plan
  // confidence unblock criteria
  // practice repetition prescription
  // proof demo improvement lane
  // operator confidence does not unlock live trading
  // improvement plan does not unlock live
  // no database write
  // no file write
  // no save endpoint
  // no real record creation
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let planState = {
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
      source: "ob_giant_pack_034_safe_fallback",
      plan_state: {
        plan_id: "ob_manual_live_operator_confidence_improvement_plan_001",
        label: "Manual Live Operator Confidence Improvement Plan",
        status: "confidence_improvement_plan_ready",
        section: "OB — Manual Live Level 1 Operator Confidence Layer",
        purpose: "Convert confidence gaps into ordered Proof/Demo improvement tasks without unlocking real Manual Live.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        improvement_plan_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        confidence_board_source: "/ob/manual-live-operator-confidence-board.json",
        step_checklist_source: "/ob/manual-live-operator-step-confidence-checklist.json",
        scenario_review_source: "/ob/manual-live-operator-scenario-confidence-review.json"
      },
      improvement_summary: {
        total_improvement_tasks: 6,
        high_priority_tasks: 4,
        locked_review_tasks: 2,
        required_clean_reps_preview: 7,
        current_clean_reps_preview: 2,
        readiness_label: "confidence_improvement_plan_ready",
        headline: "The next work is clear: checklist/fill, fake fill vs not-placed, confusing checklist response, and emotional stop rule.",
        next_action: "Run two clean checklist/fill Proof/Demo reps, then one fake fill vs not-placed comparison.",
        status: "ready"
      },
      improvement_tasks: [
        {
          task_id: "two_clean_checklist_fill_reps",
          rank: 1,
          label: "Two clean checklist/fill reps",
          priority: "high",
          gap_source: "checklist_control_step + confusing_checklist_scenario",
          assigned_lane: "Proof/Demo",
          task_reason: "Checklist/fill is the largest remaining confidence gap.",
          required_reps_preview: 2,
          done_criteria: ["No missing fields", "Owner explains every field", "No live action taken"],
          status: "active"
        },
        {
          task_id: "fake_fill_not_placed_comparison",
          rank: 2,
          label: "Fake fill vs not-placed comparison",
          priority: "high",
          gap_source: "fake_fill_not_placed_step + fake_fill_vs_not_placed_scenario",
          assigned_lane: "Proof/Demo",
          task_reason: "Owner needs confidence choosing and explaining fake fill vs not-placed.",
          required_reps_preview: 2,
          done_criteria: ["Fake fill rehearsed", "Not-placed rehearsed", "Choice explained", "Unclear defaults to repeat"],
          status: "active"
        },
        {
          task_id: "confusing_checklist_stop_rule",
          rank: 3,
          label: "Confusing checklist stop rule",
          priority: "high",
          gap_source: "confusing_checklist_scenario",
          assigned_lane: "Proof/Demo",
          task_reason: "Owner must reflexively stop/repeat when a checklist field is unclear.",
          required_reps_preview: 2,
          done_criteria: ["Confusion named", "Stop selected", "Repeat selected", "No advance"],
          status: "active"
        },
        {
          task_id: "emotional_rush_stop_rule",
          rank: 4,
          label: "Emotional rush stop rule",
          priority: "high",
          gap_source: "emotional_rush_scenario",
          assigned_lane: "Proof/Demo",
          task_reason: "Rushed, excited, scared, or pressured states must stop the operator.",
          required_reps_preview: 1,
          done_criteria: ["Emotion named", "Stop selected", "Return later selected", "No live action"],
          status: "active"
        },
        {
          task_id: "protected_capital_boundary_review",
          rank: 5,
          label: "Protected capital boundary review",
          priority: "locked_review",
          gap_source: "protected_capital_warning_scenario",
          assigned_lane: "Owner Review",
          task_reason: "Protected capital remains locked and separate from practice.",
          required_reps_preview: 1,
          done_criteria: ["Protected account named", "Proof/Demo selected", "No capital movement"],
          status: "locked_review"
        },
        {
          task_id: "live_lock_pressure_review",
          rank: 6,
          label: "Live lock pressure review",
          priority: "locked_review",
          gap_source: "live_lock_pressure_scenario",
          assigned_lane: "Owner Review",
          task_reason: "Confidence never unlocks real Manual Live in this layer.",
          required_reps_preview: 1,
          done_criteria: ["Real Manual Live locked", "Hybrid locked", "Automated locked", "Broker/bank/database/Vault blocked"],
          status: "locked_review"
        }
      ],
      improvement_rules: [
        {
          rule_id: "no_live_unlock_from_plan",
          label: "No live unlock from plan",
          requirement: "Completing this plan later still does not unlock real Manual Live.",
          status: "locked"
        },
        {
          rule_id: "clean_reps_before_checkpoint",
          label: "Clean reps before checkpoint",
          requirement: "Checklist/fill and scenario gaps need clean reps before any future readiness checkpoint.",
          status: "active"
        },
        {
          rule_id: "proof_demo_only",
          label: "Proof/Demo only",
          requirement: "All improvement tasks stay in Proof/Demo or owner review.",
          status: "active"
        },
        {
          rule_id: "stop_when_unclear",
          label: "Stop when unclear",
          requirement: "Any unclear field, emotional pressure, or missing step means stop and repeat.",
          status: "active"
        }
      ],
      improvement_evidence_sources: [
        {
          source_id: "confidence_board",
          label: "Operator Confidence Board",
          route: "/ob/manual-live-operator-confidence-board.json",
          evidence: "Confidence score preview is forming, not ready.",
          status: "watch"
        },
        {
          source_id: "step_checklist",
          label: "Step Confidence Checklist",
          route: "/ob/manual-live-operator-step-confidence-checklist.json",
          evidence: "Checklist control and fake fill/not-placed still need reps.",
          status: "needs_reps"
        },
        {
          source_id: "scenario_review",
          label: "Scenario Confidence Review",
          route: "/ob/manual-live-operator-scenario-confidence-review.json",
          evidence: "Confusing checklist, fake fill comparison, and emotional rush need reps.",
          status: "needs_reps"
        },
        {
          source_id: "practice_focus_queue",
          label: "Owner Practice Focus Queue",
          route: "/ob/owner-practice-focus-queue.json",
          evidence: "Checklist/fill path remains first practice focus.",
          status: "ready"
        }
      ],
      blocked_actions: [
        "write_confidence_improvement_plan_database_now",
        "write_confidence_improvement_plan_file_now",
        "create_confidence_improvement_plan_save_endpoint_now",
        "persist_confidence_improvement_plan_now",
        "create_real_improvement_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_improvement_plan",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_confidence_improvement_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_confidence_improvement_plan_only: true,
        confidence_improvement_plan_preview_only: true,
        dry_run_only: true,
        improvement_plan_does_not_unlock_live: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
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
      plan_state: { ...(fallback.plan_state || {}), ...(safe.plan_state || {}) },
      improvement_summary: { ...(fallback.improvement_summary || {}), ...(safe.improvement_summary || {}) },
      improvement_tasks: Array.isArray(safe.improvement_tasks) ? safe.improvement_tasks : fallback.improvement_tasks,
      improvement_rules: Array.isArray(safe.improvement_rules) ? safe.improvement_rules : fallback.improvement_rules,
      improvement_evidence_sources: Array.isArray(safe.improvement_evidence_sources) ? safe.improvement_evidence_sources : fallback.improvement_evidence_sources,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_confidence_improvement_plan_only: true,
        confidence_improvement_plan_preview_only: true,
        dry_run_only: true,
        improvement_plan_does_not_unlock_live: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_GP034 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_operator_confidence_improvement_plan_gp034: normalized,
      manualLiveOperatorConfidenceImprovementPlanOnly: true,
      confidenceImprovementPlanPreviewOnly: true,
      improvementPlanDoesNotUnlockLive: true,
      dryRunOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obManualLiveOperatorConfidenceImprovementPlanUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchImprovementPlan() {
    planState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      planState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        planState.status = "ready";
        planState.source = normalized.source || "server";
        planState.payload = normalized;
        planState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        planState.status = "guarded_fallback";
        planState.source = "guarded_fallback";
        planState.payload = fallback;
        planState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      planState.status = "error_fallback";
      planState.source = "error_fallback";
      planState.payload = fallback;
      planState.fallbackActive = true;
      planState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return planState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("needs_reps")) return "red";
    if (text.includes("active") || text.includes("ready")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-operator-confidence-improvement-plan-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function taskRow(item) {
    const criteria = Array.isArray(item.done_criteria) ? item.done_criteria.join(" · ") : "none";
    return `
      <div class="ob-manual-live-operator-confidence-improvement-plan-row">
        <div class="ob-manual-live-operator-confidence-improvement-plan-dot">${safeText(item.rank, "?")}</div>
        <div>
          <strong>${safeText(item.label, "Task")}</strong>
          <span>${safeText(item.priority, "priority")} · ${safeText(item.status, "active")}</span>
        </div>
        <span>
          Reason: ${safeText(item.task_reason, "reason")}<br>
          Lane: ${safeText(item.assigned_lane, "lane")} · Reps: ${safeText(item.required_reps_preview, "0")}<br>
          Done: ${criteria}
        </span>
        <div class="ob-manual-live-operator-confidence-improvement-plan-status ${tone(item.status || item.priority)}">${safeText(item.status, "active")}</div>
      </div>
    `;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-manual-live-operator-confidence-improvement-plan-row">
        <div class="ob-manual-live-operator-confidence-improvement-plan-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.rule_id || item.source_id, "Item")}</strong>
          <span>${safeText(item.status || "plan", "plan")}</span>
        </div>
        <span>${safeText(item.requirement || item.evidence || "detail", "detail")}</span>
        <div class="ob-manual-live-operator-confidence-improvement-plan-status ${tone(item.status)}">${safeText(item.status || "ready", "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-operator-confidence-improvement-plan-row">
        <div class="ob-manual-live-operator-confidence-improvement-plan-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP034 confidence improvement plan boundaries.</span>
        <div class="ob-manual-live-operator-confidence-improvement-plan-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = planState.payload || buildFallbackPayload();
    const state = payload.plan_state || {};
    const summary = payload.improvement_summary || {};
    const tasks = Array.isArray(payload.improvement_tasks) ? payload.improvement_tasks : [];
    const rules = Array.isArray(payload.improvement_rules) ? payload.improvement_rules : [];
    const sources = Array.isArray(payload.improvement_evidence_sources) ? payload.improvement_evidence_sources : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-manual-live-operator-confidence-improvement-plan-panel" id="obManualLiveOperatorConfidenceImprovementPlanPanel" data-ob-giant-pack-034="true">
        <div class="ob-manual-live-operator-confidence-improvement-plan-head">
          <div>
            <div class="ob-label">OB Giant Pack 034 · Confidence Improvement</div>
            <div class="ob-manual-live-operator-confidence-improvement-plan-title">Manual Live Operator Confidence Improvement Plan</div>
            <div class="ob-manual-live-operator-confidence-improvement-plan-subtitle">
              ${safeText(planState.status, "booting")} · ${safeText(state.status, "confidence_improvement_plan_ready")} · improvement plan only.
            </div>
          </div>
          <div class="ob-manual-live-operator-confidence-improvement-plan-chip-row">
            <span class="ob-manual-live-operator-confidence-improvement-plan-chip green">Ordered tasks</span>
            <span class="ob-manual-live-operator-confidence-improvement-plan-chip gold">Proof/Demo reps</span>
            <span class="ob-manual-live-operator-confidence-improvement-plan-chip red">Does not unlock live</span>
            <span class="ob-manual-live-operator-confidence-improvement-plan-chip red">No save endpoint</span>
          </div>
        </div>

        <div class="ob-manual-live-operator-confidence-improvement-plan-stat-grid">
          ${card("Tasks", safeText(summary.total_improvement_tasks, "0"))}
          ${card("High", safeText(summary.high_priority_tasks, "0"))}
          ${card("Locked", safeText(summary.locked_review_tasks, "0"))}
          ${card("Required reps", safeText(summary.required_clean_reps_preview, "0"))}
          ${card("Current reps", safeText(summary.current_clean_reps_preview, "0"))}
        </div>

        <div class="ob-manual-live-operator-confidence-improvement-plan-grid">
          <div>
            <div class="ob-manual-live-operator-confidence-improvement-plan-card">
              <span>Readiness label</span>
              <strong>${safeText(summary.readiness_label, "confidence_improvement_plan_ready")}</strong>
              <div class="ob-manual-live-operator-confidence-improvement-plan-callout">
                <strong>Headline:</strong><br>
                ${safeText(summary.headline, "Improvement plan ready.")}
              </div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-callout">
                <strong>Next action:</strong><br>
                ${safeText(summary.next_action, "Run Proof/Demo reps.")}
              </div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-boundary">
                <strong>Boundary:</strong><br>
                This improvement plan does not unlock real Manual Live. It creates no persisted record and performs no broker/bank/Vault action.
              </div>
            </div>

            <div class="ob-manual-live-operator-confidence-improvement-plan-card" style="margin-top: 11px;">
              <span>Operator standard</span>
              <strong>Improve the weak reps first. Clean, boring, explainable practice beats rushing.</strong>
              <div class="ob-manual-live-operator-confidence-improvement-plan-boundary">
                Real Manual Live, Hybrid, Automated, broker, bank, database, save endpoint, and direct Vault actions remain locked.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-operator-confidence-improvement-plan-section">
              <div class="ob-manual-live-operator-confidence-improvement-plan-section-title">Ordered improvement tasks</div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-list">${tasks.map(taskRow).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-improvement-plan-section">
              <div class="ob-manual-live-operator-confidence-improvement-plan-section-title">Improvement rules</div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-list">${rules.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-improvement-plan-section">
              <div class="ob-manual-live-operator-confidence-improvement-plan-section-title">Evidence sources</div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-list">${sources.map((item, index) => row(item, index, "E")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-improvement-plan-section">
              <div class="ob-manual-live-operator-confidence-improvement-plan-section-title">Blocked actions</div>
              <div class="ob-manual-live-operator-confidence-improvement-plan-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-operator-confidence-improvement-plan-callout">
          <strong>Next handoff:</strong><br>
          GP035 can close this mini-section with Manual Live Operator Confidence Readiness Checkpoint.
        </div>

        <div class="ob-manual-live-operator-confidence-improvement-plan-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveOperatorConfidenceImprovementPlanPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const scenario = document.getElementById("obManualLiveOperatorScenarioConfidenceReviewPanel");
    const checklist = document.getElementById("obManualLiveOperatorStepConfidenceChecklistPanel");
    const confidence = document.getElementById("obManualLiveOperatorConfidenceBoardPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (scenario && scenario.parentNode) scenario.insertAdjacentElement("afterend", panel);
    else if (checklist && checklist.parentNode) checklist.insertAdjacentElement("afterend", panel);
    else if (confidence && confidence.parentNode) confidence.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = planState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-034-manual-live-operator-confidence-improvement-plan", "ready");
    document.body.setAttribute("data-ob-manual-live-operator-confidence-improvement-plan-only", "true");
    document.body.setAttribute("data-ob-confidence-improvement-plan-preview-only", "true");
    document.body.setAttribute("data-ob-improvement-plan-does-not-unlock-live", "true");
    document.body.setAttribute("data-ob-dry-run-only", "true");
    document.body.setAttribute("data-ob-no-database-write", "true");
    document.body.setAttribute("data-ob-no-file-write", "true");
    document.body.setAttribute("data-ob-no-save-endpoint", "true");
    document.body.setAttribute("data-ob-no-real-record-creation", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_STATE = {
      version: VERSION,
      status: planState.status,
      fallbackActive: planState.fallbackActive,
      readinessLabel: payload.improvement_summary.readiness_label,
      totalImprovementTasks: payload.improvement_summary.total_improvement_tasks,
      requiredCleanRepsPreview: payload.improvement_summary.required_clean_reps_preview,
      manualLiveOperatorConfidenceImprovementPlanOnly: true,
      confidenceImprovementPlanPreviewOnly: true,
      improvementPlanDoesNotUnlockLive: true,
      dryRunOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
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
      fetchImprovementPlan();
    }, 7580);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_GP034_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return planState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchImprovementPlan,
    renderPanel,
    setFlags
  };
})();
