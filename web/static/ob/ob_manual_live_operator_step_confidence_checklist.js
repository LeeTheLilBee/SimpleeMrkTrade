// OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_JS

(function () {
  const VERSION = "OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST";
  const ENDPOINT = "/ob/manual-live-operator-step-confidence-checklist.json";

  // SMOKE MARKERS
  // Manual Live Operator Step Confidence Checklist
  // manual live operator step confidence checklist
  // step confidence checklist
  // pre-live confidence checklist
  // signal read step check
  // checklist control step check
  // fake fill not-placed step check
  // dry-run save boundary step check
  // capital boundary step check
  // live lock respect step check
  // confidence pass criteria
  // confidence fail safe
  // operator step prompt
  // operator step evidence
  // operator step done criteria
  // confidence checklist does not unlock live trading
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

  let checklistState = {
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
      source: "ob_giant_pack_032_safe_fallback",
      checklist_state: {
        checklist_id: "ob_manual_live_operator_step_confidence_checklist_001",
        label: "Manual Live Operator Step Confidence Checklist",
        status: "step_confidence_checklist_ready",
        section: "OB — Manual Live Level 1 Operator Confidence Layer",
        purpose: "Break operator confidence into step-by-step pre-live checks without unlocking real Manual Live.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        checklist_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        confidence_board_source: "/ob/manual-live-operator-confidence-board.json",
        practice_review_source: "/ob/practice-review-polish-readiness-checkpoint.json"
      },
      checklist_summary: {
        total_steps: 8,
        pass_ready_steps: 3,
        needs_reps_steps: 3,
        locked_steps: 2,
        minimum_required_preview: 7,
        current_pass_preview: 3,
        readiness_label: "step_confidence_needs_reps",
        headline: "Step confidence is not ready for real Manual Live. Keep rehearsing checklist/fill and fake fill/not-placed decisions.",
        next_action: "Complete two clean Proof/Demo checklist/fill reps before another confidence review.",
        status: "needs_reps"
      },
      confidence_steps: [
        {
          step_id: "signal_read_step",
          rank: 1,
          label: "Signal read step",
          prompt: "Can I explain the signal, setup, risk, and reason in plain language?",
          evidence_needed: "Candidate reason is explainable without hype.",
          done_criteria: ["Signal reason stated", "Risk named", "Option vs stock path understood"],
          owner_answer_preview: "mostly_clear",
          status: "watch"
        },
        {
          step_id: "checklist_control_step",
          rank: 2,
          label: "Checklist control step",
          prompt: "Can I complete every checklist field without missing anything?",
          evidence_needed: "No missing checklist fields in a Proof/Demo rehearsal.",
          done_criteria: ["All fields completed", "No skipped required item", "Owner can explain each field"],
          owner_answer_preview: "needs_reps",
          status: "needs_reps"
        },
        {
          step_id: "fake_fill_not_placed_step",
          rank: 3,
          label: "Fake fill / not-placed step",
          prompt: "Can I choose fake fill or not-placed and explain why?",
          evidence_needed: "Owner can compare both outcomes and explain the chosen one.",
          done_criteria: ["Fake fill outcome rehearsed", "Not-placed outcome rehearsed", "Choice explained"],
          owner_answer_preview: "needs_reps",
          status: "needs_reps"
        },
        {
          step_id: "dry_run_save_boundary_step",
          rank: 4,
          label: "Dry-run save boundary step",
          prompt: "Can I explain why the dry-run save preview is not a real save?",
          evidence_needed: "Owner names no DB write, no file write, no save endpoint, no direct Vault upload.",
          done_criteria: ["No database write explained", "No save endpoint explained", "No direct Vault upload explained"],
          owner_answer_preview: "mostly_clear",
          status: "watch"
        },
        {
          step_id: "capital_boundary_step",
          rank: 5,
          label: "Capital boundary step",
          prompt: "Can I keep protected/trust/apartment capital separated from trade practice?",
          evidence_needed: "Owner redirects trade practice to Proof/Demo.",
          done_criteria: ["Protected account named", "Proof/Demo selected for practice", "Capital lock respected"],
          owner_answer_preview: "clear_locked",
          status: "ready_locked"
        },
        {
          step_id: "manual_broker_translation_step",
          rank: 6,
          label: "Manual broker translation step",
          prompt: "Can I translate the rehearsal checklist into what I would manually review at the broker?",
          evidence_needed: "Owner can name broker-style fields without connecting to broker.",
          done_criteria: ["Symbol checked", "Contract/stock path checked", "Quantity/risk reviewed", "No order submitted"],
          owner_answer_preview: "watch",
          status: "watch"
        },
        {
          step_id: "live_lock_respect_step",
          rank: 7,
          label: "Live lock respect step",
          prompt: "Can I confirm Real Manual Live, Hybrid, Automated, broker, bank, database, and Vault actions are locked?",
          evidence_needed: "Owner repeats lock wall before practice.",
          done_criteria: ["Real Manual Live locked", "Hybrid locked", "Automated locked", "Broker/bank/database/Vault blocked"],
          owner_answer_preview: "clear_locked",
          status: "locked"
        },
        {
          step_id: "stop_if_unclear_step",
          rank: 8,
          label: "Stop if unclear step",
          prompt: "Will I stop and repeat practice if any step feels rushed, unclear, or emotional?",
          evidence_needed: "Owner chooses repeat practice over rushing.",
          done_criteria: ["Stop condition named", "Repeat practice selected", "No live action taken"],
          owner_answer_preview: "required",
          status: "locked"
        }
      ],
      pass_criteria: [
        {
          criteria_id: "minimum_step_count",
          label: "Minimum passing step count",
          requirement: "At least 7 of 8 steps must be clear before future readiness review.",
          current_state: "3 of 8 pass/locked-clear equivalent",
          status: "not_met"
        },
        {
          criteria_id: "no_needs_reps_steps",
          label: "No needs-reps steps",
          requirement: "Checklist control and fake fill/not-placed must no longer be needs_reps.",
          current_state: "2 needs_reps steps remain",
          status: "not_met"
        },
        {
          criteria_id: "lock_wall_confirmed",
          label: "Lock wall confirmed",
          requirement: "Owner must confirm live locks before each confidence review.",
          current_state: "confirmed as locked",
          status: "met_locked"
        },
        {
          criteria_id: "confidence_does_not_unlock",
          label: "Confidence does not unlock",
          requirement: "Passing confidence checklist still does not unlock real Manual Live without future Tower-gated readiness.",
          current_state: "locked",
          status: "locked"
        }
      ],
      fail_safe_rules: [
        {
          rule_id: "unclear_means_repeat",
          label: "Unclear means repeat",
          trigger: "Any unclear step",
          response: "Repeat Proof/Demo practice. Do not advance.",
          status: "active"
        },
        {
          rule_id: "missing_field_means_repeat",
          label: "Missing field means repeat",
          trigger: "Any missing checklist field",
          response: "Repeat checklist/fill practice until clean.",
          status: "active"
        },
        {
          rule_id: "emotion_means_stop",
          label: "Emotion means stop",
          trigger: "Rushed, emotional, or pressured feeling",
          response: "Stop practice and return later.",
          status: "active"
        },
        {
          rule_id: "live_locked_even_if_confident",
          label: "Live locked even if confident",
          trigger: "Owner confidence improves",
          response: "Keep real Manual Live locked until future Tower-gated readiness.",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_step_confidence_checklist_database_now",
        "write_step_confidence_checklist_file_now",
        "create_step_confidence_save_endpoint_now",
        "persist_step_confidence_checklist_now",
        "create_real_step_confidence_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_step_confidence_checklist",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_step_confidence_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_step_confidence_checklist_only: true,
        step_confidence_checklist_preview_only: true,
        dry_run_only: true,
        confidence_checklist_does_not_unlock_live: true,
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
      checklist_state: { ...(fallback.checklist_state || {}), ...(safe.checklist_state || {}) },
      checklist_summary: { ...(fallback.checklist_summary || {}), ...(safe.checklist_summary || {}) },
      confidence_steps: Array.isArray(safe.confidence_steps) ? safe.confidence_steps : fallback.confidence_steps,
      pass_criteria: Array.isArray(safe.pass_criteria) ? safe.pass_criteria : fallback.pass_criteria,
      fail_safe_rules: Array.isArray(safe.fail_safe_rules) ? safe.fail_safe_rules : fallback.fail_safe_rules,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_step_confidence_checklist_only: true,
        step_confidence_checklist_preview_only: true,
        dry_run_only: true,
        confidence_checklist_does_not_unlock_live: true,
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
    window.OB_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_GP032 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_operator_step_confidence_checklist_gp032: normalized,
      manualLiveOperatorStepConfidenceChecklistOnly: true,
      stepConfidenceChecklistPreviewOnly: true,
      confidenceChecklistDoesNotUnlockLive: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveOperatorStepConfidenceChecklistUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchChecklist() {
    checklistState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      checklistState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        checklistState.status = "ready";
        checklistState.source = normalized.source || "server";
        checklistState.payload = normalized;
        checklistState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        checklistState.status = "guarded_fallback";
        checklistState.source = "guarded_fallback";
        checklistState.payload = fallback;
        checklistState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      checklistState.status = "error_fallback";
      checklistState.source = "error_fallback";
      checklistState.payload = fallback;
      checklistState.fallbackActive = true;
      checklistState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return checklistState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("not_met") || text.includes("needs_reps") || text.includes("blocked")) return "red";
    if (text.includes("ready") || text.includes("met") || text.includes("active")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-operator-step-confidence-checklist-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-manual-live-operator-step-confidence-checklist-row">
        <div class="ob-manual-live-operator-step-confidence-checklist-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.criteria_id || item.rule_id, "Item")}</strong>
          <span>${safeText(item.status || item.current_state || "check", "check")}</span>
        </div>
        <span>${safeText(item.requirement || item.response || item.trigger || item.evidence_needed || "detail", "detail")}</span>
        <div class="ob-manual-live-operator-step-confidence-checklist-status ${tone(item.status || item.current_state)}">${safeText(item.status || item.current_state || "watch", "watch")}</div>
      </div>
    `;
  }

  function stepRow(item) {
    const criteria = Array.isArray(item.done_criteria) ? item.done_criteria.join(" · ") : "none";
    return `
      <div class="ob-manual-live-operator-step-confidence-checklist-row">
        <div class="ob-manual-live-operator-step-confidence-checklist-dot">${safeText(item.rank, "?")}</div>
        <div>
          <strong>${safeText(item.label, "Step")}</strong>
          <span>${safeText(item.owner_answer_preview, "answer")} · ${safeText(item.status, "watch")}</span>
        </div>
        <span>
          Prompt: ${safeText(item.prompt, "prompt")}<br>
          Evidence: ${safeText(item.evidence_needed, "evidence")}<br>
          Done: ${criteria}
        </span>
        <div class="ob-manual-live-operator-step-confidence-checklist-status ${tone(item.status)}">${safeText(item.status, "watch")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-operator-step-confidence-checklist-row">
        <div class="ob-manual-live-operator-step-confidence-checklist-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP032 step-confidence checklist boundaries.</span>
        <div class="ob-manual-live-operator-step-confidence-checklist-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = checklistState.payload || buildFallbackPayload();
    const state = payload.checklist_state || {};
    const summary = payload.checklist_summary || {};
    const steps = Array.isArray(payload.confidence_steps) ? payload.confidence_steps : [];
    const criteria = Array.isArray(payload.pass_criteria) ? payload.pass_criteria : [];
    const failSafe = Array.isArray(payload.fail_safe_rules) ? payload.fail_safe_rules : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-manual-live-operator-step-confidence-checklist-panel" id="obManualLiveOperatorStepConfidenceChecklistPanel" data-ob-giant-pack-032="true">
        <div class="ob-manual-live-operator-step-confidence-checklist-head">
          <div>
            <div class="ob-label">OB Giant Pack 032 · Step Confidence Checklist</div>
            <div class="ob-manual-live-operator-step-confidence-checklist-title">Manual Live Operator Step Confidence Checklist</div>
            <div class="ob-manual-live-operator-step-confidence-checklist-subtitle">
              ${safeText(checklistState.status, "booting")} · ${safeText(state.status, "step_confidence_checklist_ready")} · pre-live checks only.
            </div>
          </div>
          <div class="ob-manual-live-operator-step-confidence-checklist-chip-row">
            <span class="ob-manual-live-operator-step-confidence-checklist-chip gold">Step checks</span>
            <span class="ob-manual-live-operator-step-confidence-checklist-chip green">Fail-safes active</span>
            <span class="ob-manual-live-operator-step-confidence-checklist-chip red">Does not unlock live</span>
            <span class="ob-manual-live-operator-step-confidence-checklist-chip red">No save endpoint</span>
          </div>
        </div>

        <div class="ob-manual-live-operator-step-confidence-checklist-stat-grid">
          ${card("Steps", safeText(summary.total_steps, "0"))}
          ${card("Pass", safeText(summary.pass_ready_steps, "0"))}
          ${card("Needs reps", safeText(summary.needs_reps_steps, "0"))}
          ${card("Locked", safeText(summary.locked_steps, "0"))}
          ${card("Required", safeText(summary.minimum_required_preview, "0"))}
        </div>

        <div class="ob-manual-live-operator-step-confidence-checklist-grid">
          <div>
            <div class="ob-manual-live-operator-step-confidence-checklist-card">
              <span>Readiness label</span>
              <strong>${safeText(summary.readiness_label, "step_confidence_needs_reps")}</strong>
              <div class="ob-manual-live-operator-step-confidence-checklist-callout">
                <strong>Headline:</strong><br>
                ${safeText(summary.headline, "Step confidence needs reps.")}
              </div>
              <div class="ob-manual-live-operator-step-confidence-checklist-callout">
                <strong>Next action:</strong><br>
                ${safeText(summary.next_action, "Repeat practice.")}
              </div>
              <div class="ob-manual-live-operator-step-confidence-checklist-boundary">
                <strong>Boundary:</strong><br>
                Passing this checklist later still does not unlock real Manual Live without a future Tower-gated readiness checkpoint.
              </div>
            </div>

            <div class="ob-manual-live-operator-step-confidence-checklist-card" style="margin-top: 11px;">
              <span>Operator rule</span>
              <strong>Unclear means repeat. Missing field means repeat. Emotion means stop.</strong>
              <div class="ob-manual-live-operator-step-confidence-checklist-boundary">
                No broker, bank, database, save endpoint, order, execution, or direct Vault action exists here.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-operator-step-confidence-checklist-section">
              <div class="ob-manual-live-operator-step-confidence-checklist-section-title">Step confidence checklist</div>
              <div class="ob-manual-live-operator-step-confidence-checklist-list">${steps.map(stepRow).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-step-confidence-checklist-section">
              <div class="ob-manual-live-operator-step-confidence-checklist-section-title">Pass criteria preview</div>
              <div class="ob-manual-live-operator-step-confidence-checklist-list">${criteria.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-step-confidence-checklist-section">
              <div class="ob-manual-live-operator-step-confidence-checklist-section-title">Fail-safe rules</div>
              <div class="ob-manual-live-operator-step-confidence-checklist-list">${failSafe.map((item, index) => row(item, index, "F")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-step-confidence-checklist-section">
              <div class="ob-manual-live-operator-step-confidence-checklist-section-title">Blocked actions</div>
              <div class="ob-manual-live-operator-step-confidence-checklist-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-operator-step-confidence-checklist-callout">
          <strong>Next handoff:</strong><br>
          GP033 can add Manual Live Operator Scenario Confidence Review.
        </div>

        <div class="ob-manual-live-operator-step-confidence-checklist-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveOperatorStepConfidenceChecklistPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const confidence = document.getElementById("obManualLiveOperatorConfidenceBoardPanel");
    const checkpoint = document.getElementById("obPracticeReviewPolishReadinessCheckpointPanel");
    const snapshot = document.getElementById("obPracticeReviewCompactSnapshotPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (confidence && confidence.parentNode) confidence.insertAdjacentElement("afterend", panel);
    else if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else if (snapshot && snapshot.parentNode) snapshot.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = checklistState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-032-manual-live-operator-step-confidence-checklist", "ready");
    document.body.setAttribute("data-ob-manual-live-operator-step-confidence-checklist-only", "true");
    document.body.setAttribute("data-ob-step-confidence-checklist-preview-only", "true");
    document.body.setAttribute("data-ob-confidence-checklist-does-not-unlock-live", "true");
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

    window.OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_STATE = {
      version: VERSION,
      status: checklistState.status,
      fallbackActive: checklistState.fallbackActive,
      checklistReadinessLabel: payload.checklist_summary.readiness_label,
      totalSteps: payload.checklist_summary.total_steps,
      currentPassPreview: payload.checklist_summary.current_pass_preview,
      manualLiveOperatorStepConfidenceChecklistOnly: true,
      stepConfidenceChecklistPreviewOnly: true,
      confidenceChecklistDoesNotUnlockLive: true,
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
      fetchChecklist();
    }, 7260);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_GP032_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return checklistState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchChecklist,
    renderPanel,
    setFlags
  };
})();
