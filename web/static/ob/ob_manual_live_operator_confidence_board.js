// OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_JS

(function () {
  const VERSION = "OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD";
  const ENDPOINT = "/ob/manual-live-operator-confidence-board.json";

  // SMOKE MARKERS
  // Manual Live Operator Confidence Board
  // manual live operator confidence board
  // operator confidence layer
  // confidence readiness dimensions
  // owner confidence calibration
  // manual live level one confidence
  // confidence does not unlock live trading
  // confidence scale preview
  // what feels ready
  // what needs reps
  // what stays locked
  // confidence evidence source
  // practice metrics evidence
  // practice focus evidence
  // compact snapshot evidence
  // confidence blocker
  // confidence next action
  // operator self-check
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

  let confidenceState = {
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
      source: "ob_giant_pack_031_safe_fallback",
      board_state: {
        board_id: "ob_manual_live_operator_confidence_board_001",
        label: "Manual Live Operator Confidence Board",
        status: "operator_confidence_board_ready",
        section: "OB — Manual Live Level 1 Operator Confidence Layer",
        purpose: "Calibrate owner confidence before any real Manual Live action is allowed.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        confidence_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        practice_review_source: "/ob/practice-review-polish-readiness-checkpoint.json",
        compact_snapshot_source: "/ob/practice-review-compact-snapshot.json",
        focus_queue_source: "/ob/owner-practice-focus-queue.json"
      },
      confidence_summary: {
        confidence_label: "operator_confidence_forming",
        confidence_score_preview: 68,
        confidence_threshold_preview: 85,
        ready_dimensions: 3,
        needs_reps_dimensions: 3,
        locked_dimensions: 4,
        headline: "Confidence is forming, but checklist/fill still needs reps before real Manual Live.",
        next_action: "Repeat checklist/fill path in Proof/Demo and explain the dry-run save boundary.",
        status: "watch"
      },
      confidence_dimensions: [
        {
          dimension_id: "read_signal",
          label: "Read signal",
          score_preview: 78,
          owner_feel: "mostly_clear",
          evidence: "Owner can read candidate/reasoning but should keep comparing option-style and stock fallback paths.",
          next_rep: "Compare option-style fake candidate against stock fallback rehearsal.",
          status: "watch"
        },
        {
          dimension_id: "checklist_control",
          label: "Checklist control",
          score_preview: 61,
          owner_feel: "needs_reps",
          evidence: "Checklist/fill path has the most confusion and missed-step flags.",
          next_rep: "Repeat checklist/fill path until no fields are missed.",
          status: "needs_reps"
        },
        {
          dimension_id: "fake_fill_decision",
          label: "Fake fill / not-placed decision",
          score_preview: 58,
          owner_feel: "needs_reps",
          evidence: "Owner still needs confidence choosing fake fill vs not-placed outcomes.",
          next_rep: "Run Proof/Demo fake fill and not-placed comparison.",
          status: "needs_reps"
        },
        {
          dimension_id: "dry_run_save_boundary",
          label: "Dry-run save boundary",
          score_preview: 74,
          owner_feel: "mostly_clear",
          evidence: "Owner can see dry-run save preview but must explain no database write/no save endpoint.",
          next_rep: "Explain why dry-run save is not a real save.",
          status: "watch"
        },
        {
          dimension_id: "capital_boundary",
          label: "Capital boundary",
          score_preview: 88,
          owner_feel: "clear_locked",
          evidence: "Apartment/protected reserve accounts stay protected; Proof/Demo is the practice lane.",
          next_rep: "Review protected reserve lock and redirect trade practice to Proof/Demo.",
          status: "ready_locked"
        },
        {
          dimension_id: "live_lock_respect",
          label: "Live lock respect",
          score_preview: 100,
          owner_feel: "clear_locked",
          evidence: "Real Manual Live, Hybrid, Automated, broker, bank, persistence, and Vault actions remain locked.",
          next_rep: "Confirm lock wall before every confidence review.",
          status: "locked"
        }
      ],
      confidence_evidence_sources: [
        {
          source_id: "practice_repetition_metrics",
          label: "Practice Repetition Metrics",
          route: "/ob/practice-repetition-metrics-board.json",
          evidence: "Completion up, blockers down, but repeat recommendations remain.",
          status: "ready"
        },
        {
          source_id: "owner_review_guidance",
          label: "Owner Review Polish Guidance",
          route: "/ob/owner-review-polish-guidance.json",
          evidence: "Repeat is not failure; drill until steps become automatic.",
          status: "ready"
        },
        {
          source_id: "practice_focus_queue",
          label: "Owner Practice Focus Queue",
          route: "/ob/owner-practice-focus-queue.json",
          evidence: "First focus remains checklist/fill path in Proof/Demo.",
          status: "ready"
        },
        {
          source_id: "compact_snapshot",
          label: "Practice Review Compact Snapshot",
          route: "/ob/practice-review-compact-snapshot.json",
          evidence: "Owner practice ready; real Manual Live still locked.",
          status: "ready"
        },
        {
          source_id: "pre_live_lock_wall",
          label: "Pre-Live Lock Wall",
          route: "/ob/manual-live-pre-live-lock-wall.json",
          evidence: "No real live, hybrid, automated, broker, bank, database, or Vault action is enabled.",
          status: "locked"
        }
      ],
      operator_self_checks: [
        {
          check_id: "can_explain_candidate",
          label: "Can explain candidate",
          prompt: "Can I explain why this candidate is worth reviewing without relying on hype?",
          expected_answer: "Yes, in plain language.",
          status: "watch"
        },
        {
          check_id: "can_complete_checklist",
          label: "Can complete checklist",
          prompt: "Can I complete the broker-style checklist without missing required fields?",
          expected_answer: "Not yet — repeat in Proof/Demo.",
          status: "needs_reps"
        },
        {
          check_id: "can_choose_fake_fill",
          label: "Can choose fake fill/not-placed",
          prompt: "Can I decide fake fill vs not-placed and explain why?",
          expected_answer: "Needs another repetition.",
          status: "needs_reps"
        },
        {
          check_id: "can_explain_locks",
          label: "Can explain live locks",
          prompt: "Can I explain why real Manual Live is still locked?",
          expected_answer: "Yes — no broker/bank/database/Vault actions are enabled.",
          status: "locked"
        }
      ],
      confidence_blockers: [
        {
          blocker_id: "checklist_fill_confidence_gap",
          label: "Checklist/fill confidence gap",
          reason: "Most remaining practice need is tied to checklist/fill confidence.",
          unblock_action_preview: "Complete two clean Proof/Demo checklist/fill reps.",
          status: "blocking_live"
        },
        {
          blocker_id: "fake_fill_decision_gap",
          label: "Fake fill decision gap",
          reason: "Owner still needs to compare fake fill and not-placed outcomes.",
          unblock_action_preview: "Run one fake fill and one not-placed rehearsal.",
          status: "blocking_live"
        },
        {
          blocker_id: "real_manual_live_lock",
          label: "Real Manual Live lock",
          reason: "This layer measures confidence only; it does not unlock real live trading.",
          unblock_action_preview: "Future Tower-gated readiness checkpoint only.",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_operator_confidence_database_now",
        "write_operator_confidence_file_now",
        "create_operator_confidence_save_endpoint_now",
        "persist_operator_confidence_now",
        "create_real_confidence_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_confidence_board",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_operator_confidence_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_confidence_board_only: true,
        operator_confidence_preview_only: true,
        dry_run_only: true,
        confidence_does_not_unlock_live: true,
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
      board_state: { ...(fallback.board_state || {}), ...(safe.board_state || {}) },
      confidence_summary: { ...(fallback.confidence_summary || {}), ...(safe.confidence_summary || {}) },
      confidence_dimensions: Array.isArray(safe.confidence_dimensions) ? safe.confidence_dimensions : fallback.confidence_dimensions,
      confidence_evidence_sources: Array.isArray(safe.confidence_evidence_sources) ? safe.confidence_evidence_sources : fallback.confidence_evidence_sources,
      operator_self_checks: Array.isArray(safe.operator_self_checks) ? safe.operator_self_checks : fallback.operator_self_checks,
      confidence_blockers: Array.isArray(safe.confidence_blockers) ? safe.confidence_blockers : fallback.confidence_blockers,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_operator_confidence_board_only: true,
        operator_confidence_preview_only: true,
        dry_run_only: true,
        confidence_does_not_unlock_live: true,
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
    window.OB_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_GP031 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_operator_confidence_board_gp031: normalized,
      manualLiveOperatorConfidenceBoardOnly: true,
      operatorConfidencePreviewOnly: true,
      confidenceDoesNotUnlockLive: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveOperatorConfidenceBoardUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchConfidence() {
    confidenceState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      confidenceState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        confidenceState.status = "ready";
        confidenceState.source = normalized.source || "server";
        confidenceState.payload = normalized;
        confidenceState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        confidenceState.status = "guarded_fallback";
        confidenceState.source = "guarded_fallback";
        confidenceState.payload = fallback;
        confidenceState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      confidenceState.status = "error_fallback";
      confidenceState.source = "error_fallback";
      confidenceState.payload = fallback;
      confidenceState.fallbackActive = true;
      confidenceState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return confidenceState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocking") || text.includes("needs_reps")) return "red";
    if (text.includes("ready") || text.includes("clear")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-operator-confidence-board-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-manual-live-operator-confidence-board-row">
        <div class="ob-manual-live-operator-confidence-board-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.dimension_id || item.source_id || item.check_id || item.blocker_id, "Item")}</strong>
          <span>${safeText(item.status || item.owner_feel || "confidence", "confidence")}</span>
        </div>
        <span>${safeText(item.evidence || item.prompt || item.reason || item.next_rep || "detail", "detail")}</span>
        <div class="ob-manual-live-operator-confidence-board-status ${tone(item.status || item.owner_feel)}">${safeText(item.status || item.owner_feel || "ready", "ready")}</div>
      </div>
    `;
  }

  function dimensionRow(item) {
    return `
      <div class="ob-manual-live-operator-confidence-board-row">
        <div class="ob-manual-live-operator-confidence-board-dot">${safeText(item.score_preview, "0")}</div>
        <div>
          <strong>${safeText(item.label, "Confidence dimension")}</strong>
          <span>${safeText(item.owner_feel, "owner_feel")} · ${safeText(item.status, "status")}</span>
        </div>
        <span>
          Evidence: ${safeText(item.evidence, "evidence")}<br>
          Next rep: ${safeText(item.next_rep, "next")}
        </span>
        <div class="ob-manual-live-operator-confidence-board-status ${tone(item.status)}">${safeText(item.status, "watch")}</div>
      </div>
    `;
  }

  function selfCheckRow(item) {
    return `
      <div class="ob-manual-live-operator-confidence-board-row">
        <div class="ob-manual-live-operator-confidence-board-dot">?</div>
        <div>
          <strong>${safeText(item.label, "Self check")}</strong>
          <span>${safeText(item.status, "watch")}</span>
        </div>
        <span>
          ${safeText(item.prompt, "prompt")}<br>
          Expected: ${safeText(item.expected_answer, "answer")}
        </span>
        <div class="ob-manual-live-operator-confidence-board-status ${tone(item.status)}">${safeText(item.status, "watch")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-operator-confidence-board-row">
        <div class="ob-manual-live-operator-confidence-board-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP031 operator confidence boundaries.</span>
        <div class="ob-manual-live-operator-confidence-board-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = confidenceState.payload || buildFallbackPayload();
    const state = payload.board_state || {};
    const summary = payload.confidence_summary || {};
    const dimensions = Array.isArray(payload.confidence_dimensions) ? payload.confidence_dimensions : [];
    const sources = Array.isArray(payload.confidence_evidence_sources) ? payload.confidence_evidence_sources : [];
    const checks = Array.isArray(payload.operator_self_checks) ? payload.operator_self_checks : [];
    const blockers = Array.isArray(payload.confidence_blockers) ? payload.confidence_blockers : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-manual-live-operator-confidence-board-panel" id="obManualLiveOperatorConfidenceBoardPanel" data-ob-giant-pack-031="true">
        <div class="ob-manual-live-operator-confidence-board-head">
          <div>
            <div class="ob-label">OB Giant Pack 031 · Operator Confidence</div>
            <div class="ob-manual-live-operator-confidence-board-title">Manual Live Operator Confidence Board</div>
            <div class="ob-manual-live-operator-confidence-board-subtitle">
              ${safeText(confidenceState.status, "booting")} · ${safeText(state.status, "operator_confidence_board_ready")} · confidence preview only.
            </div>
          </div>
          <div class="ob-manual-live-operator-confidence-board-chip-row">
            <span class="ob-manual-live-operator-confidence-board-chip gold">Confidence forming</span>
            <span class="ob-manual-live-operator-confidence-board-chip green">Practice evidence</span>
            <span class="ob-manual-live-operator-confidence-board-chip red">Does not unlock live</span>
            <span class="ob-manual-live-operator-confidence-board-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-manual-live-operator-confidence-board-stat-grid">
          ${card("Score", safeText(summary.confidence_score_preview, "0"))}
          ${card("Threshold", safeText(summary.confidence_threshold_preview, "85"))}
          ${card("Ready", safeText(summary.ready_dimensions, "0"))}
          ${card("Needs reps", safeText(summary.needs_reps_dimensions, "0"))}
          ${card("Locked", safeText(summary.locked_dimensions, "0"))}
        </div>

        <div class="ob-manual-live-operator-confidence-board-grid">
          <div>
            <div class="ob-manual-live-operator-confidence-board-card">
              <span>Confidence label</span>
              <strong>${safeText(summary.confidence_label, "operator_confidence_forming")}</strong>
              <div class="ob-manual-live-operator-confidence-board-callout">
                <strong>Headline:</strong><br>
                ${safeText(summary.headline, "Confidence is forming.")}
              </div>
              <div class="ob-manual-live-operator-confidence-board-callout">
                <strong>Next action:</strong><br>
                ${safeText(summary.next_action, "Repeat the next Proof/Demo practice loop.")}
              </div>
              <div class="ob-manual-live-operator-confidence-board-boundary">
                <strong>Boundary:</strong><br>
                Confidence preview does not unlock real Manual Live. No broker/bank/database/Vault action is enabled.
              </div>
            </div>

            <div class="ob-manual-live-operator-confidence-board-card" style="margin-top: 11px;">
              <span>Operator standard</span>
              <strong>Confidence means slow, boring, controlled, explainable, and lock-aware.</strong>
              <div class="ob-manual-live-operator-confidence-board-boundary">
                Any rushed, unclear, or unexplainable step stays in Proof/Demo practice.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-operator-confidence-board-section">
              <div class="ob-manual-live-operator-confidence-board-section-title">Confidence dimensions</div>
              <div class="ob-manual-live-operator-confidence-board-list">${dimensions.map(dimensionRow).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-board-section">
              <div class="ob-manual-live-operator-confidence-board-section-title">Operator self-checks</div>
              <div class="ob-manual-live-operator-confidence-board-list">${checks.map(selfCheckRow).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-board-section">
              <div class="ob-manual-live-operator-confidence-board-section-title">Confidence evidence sources</div>
              <div class="ob-manual-live-operator-confidence-board-list">${sources.map((item, index) => row(item, index, "E")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-board-section">
              <div class="ob-manual-live-operator-confidence-board-section-title">Confidence blockers</div>
              <div class="ob-manual-live-operator-confidence-board-list">${blockers.map((item, index) => row(item, index, "B")).join("")}</div>
            </div>

            <div class="ob-manual-live-operator-confidence-board-section">
              <div class="ob-manual-live-operator-confidence-board-section-title">Blocked actions</div>
              <div class="ob-manual-live-operator-confidence-board-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-operator-confidence-board-callout">
          <strong>Next handoff:</strong><br>
          GP032 can add Manual Live Operator Step Confidence Checklist.
        </div>

        <div class="ob-manual-live-operator-confidence-board-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveOperatorConfidenceBoardPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const checkpoint = document.getElementById("obPracticeReviewPolishReadinessCheckpointPanel");
    const snapshot = document.getElementById("obPracticeReviewCompactSnapshotPanel");
    const focus = document.getElementById("obOwnerPracticeFocusQueuePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else if (snapshot && snapshot.parentNode) snapshot.insertAdjacentElement("afterend", panel);
    else if (focus && focus.parentNode) focus.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = confidenceState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-031-manual-live-operator-confidence-board", "ready");
    document.body.setAttribute("data-ob-manual-live-operator-confidence-board-only", "true");
    document.body.setAttribute("data-ob-operator-confidence-preview-only", "true");
    document.body.setAttribute("data-ob-confidence-does-not-unlock-live", "true");
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

    window.OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_STATE = {
      version: VERSION,
      status: confidenceState.status,
      fallbackActive: confidenceState.fallbackActive,
      confidenceScorePreview: payload.confidence_summary.confidence_score_preview,
      confidenceLabel: payload.confidence_summary.confidence_label,
      confidenceDimensionCount: payload.confidence_dimensions.length,
      manualLiveOperatorConfidenceBoardOnly: true,
      operatorConfidencePreviewOnly: true,
      confidenceDoesNotUnlockLive: true,
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
      fetchConfidence();
    }, 7100);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_GP031_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return confidenceState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchConfidence,
    renderPanel,
    setFlags
  };
})();
