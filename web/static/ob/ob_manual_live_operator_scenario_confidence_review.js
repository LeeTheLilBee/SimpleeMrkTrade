// OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_JS

(function () {
  const VERSION = "OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW";
  const ENDPOINT = "/ob/manual-live-operator-scenario-confidence-review.json";

  // SMOKE MARKERS
  // Manual Live Operator Scenario Confidence Review
  // manual live operator scenario confidence review
  // operator scenario confidence
  // scenario confidence review
  // clean candidate scenario
  // confusing checklist scenario
  // fake fill vs not-placed scenario
  // protected capital warning scenario
  // live lock pressure scenario
  // emotional rush scenario
  // scenario prompt
  // scenario expected response
  // scenario pass criteria
  // scenario confidence blocker
  // scenario fail safe
  // scenario review does not unlock live trading
  // pre-live scenario drill
  // operator scenario evidence
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

  let scenarioState = {
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
      source: "ob_giant_pack_033_safe_fallback",
      scenario_state: {
        scenario_review_id: "ob_manual_live_operator_scenario_confidence_review_001",
        label: "Manual Live Operator Scenario Confidence Review",
        status: "scenario_confidence_review_ready",
        section: "OB — Manual Live Level 1 Operator Confidence Layer",
        purpose: "Pressure-test owner confidence with pre-live scenario cards without unlocking real Manual Live.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        scenario_review_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        confidence_board_source: "/ob/manual-live-operator-confidence-board.json",
        step_checklist_source: "/ob/manual-live-operator-step-confidence-checklist.json"
      },
      scenario_summary: {
        total_scenarios: 6,
        pass_ready_scenarios: 2,
        needs_reps_scenarios: 3,
        locked_scenarios: 1,
        minimum_required_preview: 5,
        current_pass_preview: 2,
        readiness_label: "scenario_confidence_needs_reps",
        headline: "Scenario confidence is not ready for real Manual Live. The owner still needs reps under confusion and pressure.",
        next_action: "Run the confusing checklist scenario and fake fill vs not-placed scenario again in Proof/Demo.",
        status: "needs_reps"
      },
      scenario_cards: [
        {
          scenario_id: "clean_candidate_scenario",
          rank: 1,
          label: "Clean candidate scenario",
          scenario_type: "clean_candidate",
          prompt: "The candidate looks clean and the checklist is complete. What do you do next?",
          expected_response: "Explain the signal, confirm risk, complete fake/manual review, and keep real live locked.",
          pass_criteria: ["Signal explained", "Risk named", "Checklist complete", "No real order submitted"],
          confidence_result_preview: "pass_ready",
          status: "ready"
        },
        {
          scenario_id: "confusing_checklist_scenario",
          rank: 2,
          label: "Confusing checklist scenario",
          scenario_type: "confusion",
          prompt: "A checklist field feels unclear or missing. What do you do?",
          expected_response: "Stop, mark confusion, repeat Proof/Demo practice, and do not advance.",
          pass_criteria: ["Unclear field identified", "Stop condition named", "Repeat practice selected", "No live action taken"],
          confidence_result_preview: "needs_reps",
          status: "needs_reps"
        },
        {
          scenario_id: "fake_fill_vs_not_placed_scenario",
          rank: 3,
          label: "Fake fill vs not-placed scenario",
          scenario_type: "outcome_choice",
          prompt: "The rehearsal reaches the fill outcome decision. Do you mark fake fill or not-placed?",
          expected_response: "Choose the scenario outcome and explain why; if unclear, mark not-placed and repeat.",
          pass_criteria: ["Fake fill understood", "Not-placed understood", "Choice explained", "Unclear defaults to repeat"],
          confidence_result_preview: "needs_reps",
          status: "needs_reps"
        },
        {
          scenario_id: "protected_capital_warning_scenario",
          rank: 4,
          label: "Protected capital warning scenario",
          scenario_type: "capital_boundary",
          prompt: "The candidate looks attractive but the selected account is Trust/Apartment/protected reserve. What do you do?",
          expected_response: "Keep protected capital locked and redirect practice to Proof/Demo.",
          pass_criteria: ["Protected account named", "Practice redirected to Proof/Demo", "No capital movement", "Boundary explained"],
          confidence_result_preview: "pass_ready_locked",
          status: "ready_locked"
        },
        {
          scenario_id: "live_lock_pressure_scenario",
          rank: 5,
          label: "Live lock pressure scenario",
          scenario_type: "live_lock_pressure",
          prompt: "The owner feels confident and wants to move toward real live action. What happens?",
          expected_response: "Confidence does not unlock real Manual Live. Future Tower-gated readiness is required.",
          pass_criteria: ["Real Manual Live locked", "Hybrid locked", "Automated locked", "Broker/bank/database/Vault blocked"],
          confidence_result_preview: "locked",
          status: "locked"
        },
        {
          scenario_id: "emotional_rush_scenario",
          rank: 6,
          label: "Emotional rush scenario",
          scenario_type: "operator_pressure",
          prompt: "The owner feels rushed, excited, scared, or pressured. What is the operator response?",
          expected_response: "Stop. Do not continue. Return later or repeat practice when calm.",
          pass_criteria: ["Emotion named", "Stop selected", "No live action", "Practice repeated later"],
          confidence_result_preview: "needs_reps",
          status: "needs_reps"
        }
      ],
      scenario_evidence_sources: [
        {
          source_id: "operator_confidence_board",
          label: "Manual Live Operator Confidence Board",
          route: "/ob/manual-live-operator-confidence-board.json",
          evidence: "Confidence score preview is forming but below threshold.",
          status: "ready"
        },
        {
          source_id: "step_confidence_checklist",
          label: "Manual Live Operator Step Confidence Checklist",
          route: "/ob/manual-live-operator-step-confidence-checklist.json",
          evidence: "Checklist/fill and fake fill/not-placed still need reps.",
          status: "needs_reps"
        },
        {
          source_id: "practice_focus_queue",
          label: "Owner Practice Focus Queue",
          route: "/ob/owner-practice-focus-queue.json",
          evidence: "Repeat checklist/fill path remains first practice focus.",
          status: "ready"
        },
        {
          source_id: "pre_live_lock_wall",
          label: "Pre-Live Lock Wall",
          route: "/ob/manual-live-pre-live-lock-wall.json",
          evidence: "Real Manual Live, Hybrid, Automated, broker, bank, database, and Vault actions remain locked.",
          status: "locked"
        }
      ],
      scenario_pass_rules: [
        {
          rule_id: "must_stop_when_unclear",
          label: "Must stop when unclear",
          requirement: "Any confusing or missing step must produce stop/repeat response.",
          current_state: "needs reps",
          status: "not_met"
        },
        {
          rule_id: "must_default_to_proof_demo",
          label: "Must default to Proof/Demo",
          requirement: "All practice and unclear outcomes must stay in Proof/Demo.",
          current_state: "mostly clear",
          status: "watch"
        },
        {
          rule_id: "must_protect_capital",
          label: "Must protect capital",
          requirement: "Protected capital accounts cannot be used for casual practice.",
          current_state: "met locked",
          status: "met_locked"
        },
        {
          rule_id: "must_respect_live_lock",
          label: "Must respect live lock",
          requirement: "Confidence never unlocks real live action in this layer.",
          current_state: "locked",
          status: "locked"
        },
        {
          rule_id: "must_stop_under_emotion",
          label: "Must stop under emotion",
          requirement: "Rushed, emotional, or pressured states must stop the operator.",
          current_state: "needs reps",
          status: "not_met"
        }
      ],
      scenario_blockers: [
        {
          blocker_id: "confusing_checklist_response_gap",
          label: "Confusing checklist response gap",
          reason: "Owner must reflexively stop/repeat when checklist is unclear.",
          unblock_action_preview: "Repeat confusing checklist scenario twice cleanly.",
          status: "blocking_live"
        },
        {
          blocker_id: "fake_fill_choice_gap",
          label: "Fake fill choice gap",
          reason: "Owner must confidently explain fake fill vs not-placed.",
          unblock_action_preview: "Run fake fill and not-placed scenario comparison.",
          status: "blocking_live"
        },
        {
          blocker_id: "emotion_stop_rule_gap",
          label: "Emotion stop rule gap",
          reason: "Owner must stop if rushed, excited, scared, or pressured.",
          unblock_action_preview: "Practice emotional rush scenario until stop is automatic.",
          status: "blocking_live"
        },
        {
          blocker_id: "real_manual_live_lock",
          label: "Real Manual Live lock",
          reason: "Scenario review measures confidence only; it does not unlock live.",
          unblock_action_preview: "Future Tower-gated readiness checkpoint only.",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_scenario_confidence_database_now",
        "write_scenario_confidence_file_now",
        "create_scenario_confidence_save_endpoint_now",
        "persist_scenario_confidence_review_now",
        "create_real_scenario_confidence_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_scenario_review",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_scenario_confidence_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_scenario_confidence_review_only: true,
        scenario_confidence_review_preview_only: true,
        dry_run_only: true,
        scenario_review_does_not_unlock_live: true,
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
      scenario_state: { ...(fallback.scenario_state || {}), ...(safe.scenario_state || {}) },
      scenario_summary: { ...(fallback.scenario_summary || {}), ...(safe.scenario_summary || {}) },
      scenario_cards: Array.isArray(safe.scenario_cards) ? safe.scenario_cards : fallback.scenario_cards,
      scenario_evidence_sources: Array.isArray(safe.scenario_evidence_sources) ? safe.scenario_evidence_sources : fallback.scenario_evidence_sources,
      scenario_pass_rules: Array.isArray(safe.scenario_pass_rules) ? safe.scenario_pass_rules : fallback.scenario_pass_rules,
      scenario_blockers: Array.isArray(safe.scenario_blockers) ? safe.scenario_blockers : fallback.scenario_blockers,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_scenario_confidence_review_only: true,
        scenario_confidence_review_preview_only: true,
        dry_run_only: true,
        scenario_review_does_not_unlock_live: true,
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
    window.OB_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_GP033 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_operator_scenario_confidence_review_gp033: normalized,
      manualLiveOperatorScenarioConfidenceReviewOnly: true,
      scenarioConfidenceReviewPreviewOnly: true,
      scenarioReviewDoesNotUnlockLive: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveOperatorScenarioConfidenceReviewUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchScenarioReview() {
    scenarioState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      scenarioState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        scenarioState.status = "ready";
        scenarioState.source = normalized.source || "server";
        scenarioState.payload = normalized;
        scenarioState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        scenarioState.status = "guarded_fallback";
        scenarioState.source = "guarded_fallback";
        scenarioState.payload = fallback;
        scenarioState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      scenarioState.status = "error_fallback";
      scenarioState.source = "error_fallback";
      scenarioState.payload = fallback;
      scenarioState.fallbackActive = true;
      scenarioState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return scenarioState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("not_met") || text.includes("needs_reps") || text.includes("blocking")) return "red";
    if (text.includes("ready") || text.includes("met") || text.includes("pass")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-operator-scenario-confidence-review-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function scenarioRow(item) {
    const criteria = Array.isArray(item.pass_criteria) ? item.pass_criteria.join(" · ") : "none";
    return `
      <div class="ob-manual-live-operator-scenario-confidence-review-row">
        <div class="ob-manual-live-operator-scenario-confidence-review-dot">${safeText(item.rank, "?")}</div>
        <div>
          <strong>${safeText(item.label, "Scenario")}</strong>
          <span>${safeText(item.scenario_type, "scenario")} · ${safeText(item.status, "watch")}</span>
        </div>
        <span>
          Prompt: ${safeText(item.prompt, "prompt")}<br>
          Expected: ${safeText(item.expected_response, "response")}<br>
          Pass: ${criteria}
        </span>
        <div class="ob-manual-live-operator-scenario-confidence-review-status ${tone(item.status || item.confidence_result_preview)}">${safeText(item.status, "watch")}</div>
      </div>
    `;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-manual-live-operator-scenario-confidence-review-row">
        <div class="ob-manual-live-operator-scenario-confidence-review-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.source_id || item.rule_id || item.blocker_id, "Item")}</strong>
          <span>${safeText(item.status || item.current_state || "review", "review")}</span>
        </div>
        <span>${safeText(item.evidence || item.requirement || item.reason || item.unblock_action_preview || "detail", "detail")}</span>
        <div class="ob-manual-live-operator-scenario-confidence-review-status ${tone(item.status || item.current_state)}">${safeText(item.status || item.current_state || "watch", "watch")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-operator-scenario-confidence-review-row">
        <div class="ob-manual-live-operator-scenario-confidence-review-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP033 scenario confidence review boundaries.</span>
        <div class="ob-manual-live-operator-scenario-confidence-review-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = scenarioState.payload || buildFallbackPayload();
    const state = payload.scenario_state || {};
    const summary = payload.scenario_summary || {};
    const scenarios = Array.isArray(payload.scenario_cards) ? payload.scenario_cards : [];
    const sources = Array.isArray(payload.scenario_evidence_sources) ? payload.scenario_evidence_sources : [];
    const rules = Array.isArray(payload.scenario_pass_rules) ? payload.scenario_pass_rules : [];
    const blockers = Array.isArray(payload.scenario_blockers) ? payload.scenario_blockers : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-manual-live-operator-scenario-confidence-review-panel" id="obManualLiveOperatorScenarioConfidenceReviewPanel" data-ob-giant-pack-033="true">
        <div class="ob-manual-live-operator-scenario-confidence-review-head">
          <div>
            <div class="ob-label">OB Giant Pack 033 · Scenario Confidence</div>
            <div class="ob-manual-live-operator-scenario-confidence-review-title">Manual Live Operator Scenario Confidence Review</div>
            <div class="ob-manual-live-operator-scenario-confidence-review-subtitle">
              ${safeText(scenarioState.status, "booting")} · ${safeText(state.status, "scenario_confidence_review_ready")} · scenario review only.
            </div>
          </div>
          <div class="ob-manual-live-operator-scenario-confidence-review-chip-row">
            <span class="ob-manual-live-operator-scenario-confidence-review-chip green">Scenario cards</span>
            <span class="ob-manual-live-operator-scenario-confidence-review-chip gold">Pressure checks</span>
            <span class="ob-manual-live-operator-scenario-confidence-review-chip red">Does not unlock live</span>
            <span class="ob-manual-live-operator-scenario-confidence-review-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-manual-live-operator-scenario-confidence-review-stat-grid">
          ${card("Scenarios", safeText(summary.total_scenarios, "0"))}
          ${card("Pass", safeText(summary.pass_ready_scenarios, "0"))}
          ${card("Needs reps", safeText(summary.needs_reps_scenarios, "0"))}
          ${card("Locked", safeText(summary.locked_scenarios, "0"))}
          ${card("Required", safeText(summary.minimum_required_preview, "0"))}
        </div>

        <div class="ob-manual-live-operator-scenario-confidence-review-grid">
          <div>
            <div class="ob-manual-live-operator-scenario-confidence-review-card">
              <span>Readiness label</span>
              <strong>${safeText(summary.readiness_label, "scenario_confidence_needs_reps")}</strong>
              <div class="ob-manual-live-operator-scenario-confidence-review-callout">
                <strong>Headline:</strong><br>
                ${safeText(summary.headline, "Scenario confidence needs reps.")}
              </div>
              <div class="ob-manual-live-operator-scenario-confidence-review-callout">
                <strong>Next action:</strong><br>
                ${safeText(summary.next_action, "Repeat scenario review.")}
              </div>
              <div class="ob-manual-live-operator-scenario-confidence-review-boundary">
                <strong>Boundary:</strong><br>
                Scenario confidence review does not unlock real Manual Live. No order, broker, bank, database, or Vault action exists here.
              </div>
            </div>

            <div class="ob-manual-live-operator-scenario-confidence-review-card" style="margin-top: 11px;">
              <span>Operator scenario rule</span>
              <strong>Pressure is the test. If pressure makes the step unclear, stop and repeat practice.</strong>
              <div class="ob-manual-live-operator-scenario-confidence-review-boundary">
                Confidence under scenarios is still rehearsal-only and private-owner-only.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-operator-scenario-confidence-review-section">
              <div class="ob-manual-live-operator-scenario-confidence-review-section-title">Scenario cards</div>
              <div class="ob-manual-live-operator-scenario-confidence-review-list">${scenarios.map(scenarioRow).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-scenario-confidence-review-section">
              <div class="ob-manual-live-operator-scenario-confidence-review-section-title">Scenario evidence sources</div>
              <div class="ob-manual-live-operator-scenario-confidence-review-list">${sources.map((item, index) => row(item, index, "E")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-scenario-confidence-review-section">
              <div class="ob-manual-live-operator-scenario-confidence-review-section-title">Scenario pass rules</div>
              <div class="ob-manual-live-operator-scenario-confidence-review-list">${rules.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-scenario-confidence-review-section">
              <div class="ob-manual-live-operator-scenario-confidence-review-section-title">Scenario blockers</div>
              <div class="ob-manual-live-operator-scenario-confidence-review-list">${blockers.map((item, index) => row(item, index, "B")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-scenario-confidence-review-section">
              <div class="ob-manual-live-operator-scenario-confidence-review-section-title">Blocked actions</div>
              <div class="ob-manual-live-operator-scenario-confidence-review-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-operator-scenario-confidence-review-callout">
          <strong>Next handoff:</strong><br>
          GP034 can add Manual Live Operator Confidence Improvement Plan.
        </div>

        <div class="ob-manual-live-operator-scenario-confidence-review-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveOperatorScenarioConfidenceReviewPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const checklist = document.getElementById("obManualLiveOperatorStepConfidenceChecklistPanel");
    const confidence = document.getElementById("obManualLiveOperatorConfidenceBoardPanel");
    const checkpoint = document.getElementById("obPracticeReviewPolishReadinessCheckpointPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (checklist && checklist.parentNode) checklist.insertAdjacentElement("afterend", panel);
    else if (confidence && confidence.parentNode) confidence.insertAdjacentElement("afterend", panel);
    else if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = scenarioState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-033-manual-live-operator-scenario-confidence-review", "ready");
    document.body.setAttribute("data-ob-manual-live-operator-scenario-confidence-review-only", "true");
    document.body.setAttribute("data-ob-scenario-confidence-review-preview-only", "true");
    document.body.setAttribute("data-ob-scenario-review-does-not-unlock-live", "true");
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

    window.OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_STATE = {
      version: VERSION,
      status: scenarioState.status,
      fallbackActive: scenarioState.fallbackActive,
      scenarioReadinessLabel: payload.scenario_summary.readiness_label,
      totalScenarios: payload.scenario_summary.total_scenarios,
      currentPassPreview: payload.scenario_summary.current_pass_preview,
      manualLiveOperatorScenarioConfidenceReviewOnly: true,
      scenarioConfidenceReviewPreviewOnly: true,
      scenarioReviewDoesNotUnlockLive: true,
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
      fetchScenarioReview();
    }, 7420);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_GP033_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return scenarioState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchScenarioReview,
    renderPanel,
    setFlags
  };
})();
