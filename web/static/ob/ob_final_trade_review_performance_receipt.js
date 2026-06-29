// OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT";
  const ENDPOINT = "/ob/final-trade-review-performance-receipt.json";

  // SMOKE MARKERS
  // Final Trade Review Performance Receipt
  // final trade review
  // lesson record
  // performance receipt
  // realized result summary
  // manual live trade lifecycle summary
  // rule violation review
  // discipline score placeholder
  // confidence label
  // source confidence label
  // data freshness label
  // setup quality review
  // entry quality review
  // exit quality review
  // risk management review
  // mission account impact review
  // what worked
  // what failed
  // what to repeat
  // what to avoid
  // owner final notes
  // Review Center receipt summary
  // Vault-ready final review receipt
  // no broker API
  // no broker read
  // no auto execution
  // no public proof
  // Manual Live owner-only
  // beta Survey Paper only
  // Live Auto Locked

  let finalReviewState = {
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
      source: "ob_giant_pack_009_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        private_beta_tower_lock_polish: "/ob/private-beta-tower-lock-polish.json",
        safety_preflight_gate: "/ob/manual-live-safety-preflight-gate.json",
        decision_packet: "/ob/manual-live-decision-packet.json",
        broker_checklist_fill_capture: "/ob/manual-broker-checklist-fill-capture.json",
        position_monitor_exit_close: "/ob/position-monitor-exit-close-capture.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      final_review_state: {
        review_id: "ob_ml1_final_trade_review_001",
        label: "Final Trade Review + Performance Receipt",
        status: "final_review_required",
        owner_only: true,
        requires_close_capture: true,
        requires_lesson_record: true,
        requires_performance_receipt: true,
        creates_order: false,
        reads_broker: false,
        public_proof: false
      },
      lifecycle_summary: [
        {
          stage_id: "candidate_detected",
          label: "Candidate detected",
          source: "/ob/manual-live-level-1.json",
          receipt: "candidate_reviewed",
          status: "linked"
        },
        {
          stage_id: "decision_packet",
          label: "Decision packet",
          source: "/ob/manual-live-decision-packet.json",
          receipt: "manual_live_decision_packet_receipt",
          status: "linked"
        },
        {
          stage_id: "safety_preflight",
          label: "Safety preflight",
          source: "/ob/manual-live-safety-preflight-gate.json",
          receipt: "manual_live_safety_preflight_receipt",
          status: "linked"
        },
        {
          stage_id: "manual_broker_checklist",
          label: "Manual broker checklist",
          source: "/ob/manual-broker-checklist-fill-capture.json",
          receipt: "manual_broker_checklist_detail_receipt",
          status: "linked"
        },
        {
          stage_id: "fill_or_not_placed",
          label: "Fill / not placed",
          source: "/ob/manual-broker-checklist-fill-capture.json",
          receipt: "fill_confirmed_or_order_not_placed",
          status: "linked"
        },
        {
          stage_id: "monitor_exit_close",
          label: "Monitor / exit / close",
          source: "/ob/position-monitor-exit-close-capture.json",
          receipt: "close_confirmation_receipt",
          status: "linked"
        },
        {
          stage_id: "final_review",
          label: "Final review",
          source: "/ob/final-trade-review-performance-receipt.json",
          receipt: "final_trade_review_performance_receipt",
          status: "required"
        }
      ],
      review_fields: [
        {
          field_id: "realized_result_summary",
          label: "Realized result summary",
          purpose: "Owner records realized result, outcome class, and mission account impact.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "setup_quality_review",
          label: "Setup quality review",
          purpose: "Was the original setup valid, late, weak, crowded, or high quality?",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "entry_quality_review",
          label: "Entry quality review",
          purpose: "Did the entry follow limit discipline, do-not-enter-above, and liquidity rules?",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "exit_quality_review",
          label: "Exit quality review",
          purpose: "Did the owner follow the stop/target/time/risk-reduction plan?",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "risk_management_review",
          label: "Risk management review",
          purpose: "Review sizing, protected floor, deployment capital lock, exposure, and kill-switch state.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "rule_violation_review",
          label: "Rule violation review",
          purpose: "Identify if any OB/Tower/manual-live rule was broken, skipped, or overridden.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "discipline_score_placeholder",
          label: "Discipline score placeholder",
          purpose: "Owner assigns or reviews a discipline quality label later.",
          required: false,
          sensitivity: "owner_only"
        },
        {
          field_id: "confidence_label",
          label: "Confidence label",
          purpose: "Classify source confidence and outcome confidence after review.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "data_freshness_label",
          label: "Data freshness label",
          purpose: "Mark whether data was fresh, stale, manually reviewed, or unknown.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "lesson_record",
          label: "Lesson record",
          purpose: "Capture what worked, what failed, what to repeat, and what to avoid.",
          required: true,
          sensitivity: "owner_only"
        },
        {
          field_id: "owner_final_notes",
          label: "Owner final notes",
          purpose: "Owner records final notes for Review Center and future trading discipline.",
          required: true,
          sensitivity: "owner_only"
        }
      ],
      lesson_record: {
        lesson_id: "ob_ml1_lesson_record_001",
        fields: [
          "what_worked",
          "what_failed",
          "what_to_repeat",
          "what_to_avoid",
          "missed_warning",
          "best_next_rule",
          "owner_final_notes"
        ],
        output: "review_center_lesson_card",
        future_use: "discipline review / pattern improvement",
        no_public_training_data: true
      },
      performance_receipt: {
        receipt_id: "ob_ml1_final_performance_receipt_preview",
        receipt_type: "final_trade_review_performance_receipt",
        timestamp: "placeholder_timestamp",
        source_app: "OB",
        linked_lifecycle: "manual_live_level_1",
        linked_close_capture: "/ob/position-monitor-exit-close-capture.json",
        linked_review_center: "Review Center",
        linked_mission_account: "selected OB account",
        realized_result: "owner_entered",
        result_class: "win_loss_flat_or_not_placed",
        rule_violations: "owner_reviewed",
        confidence_label: "owner_entered",
        source_confidence_label: "owner_entered",
        data_freshness_label: "owner_entered",
        vault_ready: true,
        no_direct_vault_upload: true,
        sensitivity: "owner_only",
        public_exposure: "never_public"
      },
      review_center_summary: {
        summary_id: "ob_ml1_review_center_summary_001",
        destination_section: "Review Center / Manual Live final reviews",
        visible_cards: [
          "lifecycle timeline",
          "result summary",
          "rule violations",
          "discipline score placeholder",
          "lesson record",
          "performance receipt",
          "Vault-ready placeholder"
        ],
        owner_only: true
      },
      blocked_actions: [
        "read_broker_history",
        "broker_api_order",
        "auto_score_real_money_performance",
        "auto_execute",
        "hybrid_submit",
        "automated_live",
        "create_public_proof",
        "publish_trade_result",
        "upload_direct_to_vault",
        "skip_final_review",
        "skip_rule_violation_review",
        "skip_lesson_record"
      ],
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        final_review_required: true,
        performance_receipt_owner_only: true,
        lesson_record_owner_only: true,
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
      final_review_state: { ...(fallback.final_review_state || {}), ...(safe.final_review_state || {}) },
      lifecycle_summary: Array.isArray(safe.lifecycle_summary) ? safe.lifecycle_summary : fallback.lifecycle_summary,
      review_fields: Array.isArray(safe.review_fields) ? safe.review_fields : fallback.review_fields,
      lesson_record: { ...(fallback.lesson_record || {}), ...(safe.lesson_record || {}) },
      performance_receipt: { ...(fallback.performance_receipt || {}), ...(safe.performance_receipt || {}) },
      review_center_summary: { ...(fallback.review_center_summary || {}), ...(safe.review_center_summary || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        final_review_required: true,
        performance_receipt_owner_only: true,
        lesson_record_owner_only: true,
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

    window.OB_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT_GP009 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      final_trade_review_performance_receipt_gp009: normalized,
      final_review_required: true,
      performance_receipt_owner_only: true,
      lesson_record_owner_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_auto_execution: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obFinalTradeReviewPerformanceReceiptUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchFinalReview() {
    finalReviewState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      finalReviewState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        finalReviewState.status = "ready";
        finalReviewState.source = normalized.source || "server";
        finalReviewState.payload = normalized;
        finalReviewState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        finalReviewState.status = "guarded_fallback";
        finalReviewState.source = "guarded_fallback";
        finalReviewState.payload = fallback;
        finalReviewState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      finalReviewState.status = "error_fallback";
      finalReviewState.source = "error_fallback";
      finalReviewState.payload = fallback;
      finalReviewState.fallbackActive = true;
      finalReviewState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return finalReviewState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("disabled") || text.includes("locked") || text.includes("never")) return "red";
    if (text.includes("required") || text.includes("placeholder") || text.includes("owner")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-final-review-performance-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-final-review-performance-row">
        <div class="ob-final-review-performance-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.field_id || item.stage_id, "Item")}</strong>
          <span>${safeText(item.field_id || item.stage_id || item.receipt || "record", "record")}</span>
        </div>
        <span>${safeText(item.purpose || item.source || item.receipt || item.status, "detail")}</span>
        <div class="ob-final-review-performance-status ${tone(item.status || item.required || item.sensitivity)}">${item.required ? "required" : safeText(item.status || item.sensitivity, "ready")}</div>
      </div>
    `;
  }

  function lessonFieldRow(field) {
    return `
      <div class="ob-final-review-performance-row">
        <div class="ob-final-review-performance-dot">L</div>
        <div>
          <strong>${safeText(field, "lesson")}</strong>
          <span>lesson record</span>
        </div>
        <span>Owner records this for future discipline and Review Center learning.</span>
        <div class="ob-final-review-performance-status gold">owner note</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-final-review-performance-row">
        <div class="ob-final-review-performance-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP009 boundaries.</span>
        <div class="ob-final-review-performance-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = finalReviewState.payload || buildFallbackPayload();
    const state = payload.final_review_state || {};
    const lifecycle = Array.isArray(payload.lifecycle_summary) ? payload.lifecycle_summary : [];
    const fields = Array.isArray(payload.review_fields) ? payload.review_fields : [];
    const lesson = payload.lesson_record || {};
    const receipt = payload.performance_receipt || {};
    const summary = payload.review_center_summary || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-final-review-performance-panel" id="obFinalReviewPerformancePanel" data-ob-giant-pack-009="true">
        <div class="ob-final-review-performance-head">
          <div>
            <div class="ob-label">OB Giant Pack 009 · Final Review + Performance Receipt</div>
            <div class="ob-final-review-performance-title">Final Trade Review Loop</div>
            <div class="ob-final-review-performance-subtitle">
              ${safeText(finalReviewState.status, "booting")} · ${safeText(state.status, "final_review_required")} · performance receipt is owner-only.
            </div>
          </div>
          <div class="ob-final-review-performance-chip-row">
            <span class="ob-final-review-performance-chip gold">Final review required</span>
            <span class="ob-final-review-performance-chip gold">Lesson record</span>
            <span class="ob-final-review-performance-chip gold">Vault-ready placeholder</span>
            <span class="ob-final-review-performance-chip red">No public proof</span>
          </div>
        </div>

        <div class="ob-final-review-performance-stat-grid">
          ${card("Review", safeText(state.review_id, "review"))}
          ${card("Lifecycle", String(lifecycle.length))}
          ${card("Review fields", String(fields.length))}
          ${card("Receipt", safeText(receipt.receipt_type, "performance"))}
          ${card("Broker", "not connected")}
        </div>

        <div class="ob-final-review-performance-grid">
          <div>
            <div class="ob-final-review-performance-card">
              <span>Purpose</span>
              <strong>Close the Manual Live loop with a final review, lesson, and performance receipt.</strong>
              <div class="ob-final-review-performance-callout">
                <strong>Owner review covers:</strong><br>
                Realized result, setup, entry, exit, risk management, rule violations, confidence, freshness, and lessons.
              </div>
              <div class="ob-final-review-performance-boundary">
                <strong>Boundary:</strong><br>
                This does not read broker history, publish proof, auto-score real money, or upload directly to Vault.
              </div>
            </div>

            <div class="ob-final-review-performance-card" style="margin-top: 11px;">
              <span>Lesson record</span>
              <strong>${safeText(lesson.lesson_id, "lesson record")}</strong>
              <div class="ob-final-review-performance-list">
                ${(lesson.fields || []).map(lessonFieldRow).join("")}
              </div>
            </div>

            <div class="ob-final-review-performance-card" style="margin-top: 11px;">
              <span>Performance receipt</span>
              <strong>${safeText(receipt.receipt_type, "final_trade_review_performance_receipt")}</strong>
              <div class="ob-final-review-performance-callout">
                <strong>Vault-ready:</strong> ${receipt.vault_ready ? "yes" : "no"}<br>
                <strong>Direct Vault upload:</strong> ${receipt.no_direct_vault_upload ? "disabled" : "unknown"}<br>
                <strong>Public exposure:</strong> ${safeText(receipt.public_exposure, "never_public")}
              </div>
            </div>

            <div class="ob-final-review-performance-card" style="margin-top: 11px;">
              <span>Review Center summary</span>
              <strong>${safeText(summary.destination_section, "Review Center / Manual Live final reviews")}</strong>
              <div class="ob-final-review-performance-callout">
                ${(summary.visible_cards || []).join(" · ")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-final-review-performance-section">
              <div class="ob-final-review-performance-section-title">Manual Live lifecycle summary</div>
              <div class="ob-final-review-performance-list">${lifecycle.map((item, index) => row(item, index, "T")).join("")}</div>
            </div>

            <div class="ob-final-review-performance-section">
              <div class="ob-final-review-performance-section-title">Final review fields</div>
              <div class="ob-final-review-performance-list">${fields.map((item, index) => row(item, index)).join("")}</div>
            </div>

            <div class="ob-final-review-performance-section">
              <div class="ob-final-review-performance-section-title">Blocked actions</div>
              <div class="ob-final-review-performance-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-final-review-performance-callout">
          <strong>Receipt output:</strong><br>
          Final trade review, lesson record, rule review, performance receipt, and Review Center summary are Vault-ready placeholders only.
        </div>

        <div class="ob-final-review-performance-boundary">
          <strong>Boundary:</strong><br>
          Manual Live owner-only. Beta Survey/Paper only. No broker API. No broker read. No public proof. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obFinalReviewPerformancePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const monitorPanel = document.getElementById("obPositionMonitorExitClosePanel");
    const checklistPanel = document.getElementById("obManualBrokerChecklistFillCapturePanel");
    const decisionPanel = document.getElementById("obManualLiveDecisionPacketPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (monitorPanel && monitorPanel.parentNode) monitorPanel.insertAdjacentElement("afterend", panel);
    else if (checklistPanel && checklistPanel.parentNode) checklistPanel.insertAdjacentElement("afterend", panel);
    else if (decisionPanel && decisionPanel.parentNode) decisionPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = finalReviewState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-009-final-review-performance", "ready");
    document.body.setAttribute("data-ob-final-review-required", "true");
    document.body.setAttribute("data-ob-performance-receipt-owner-only", "true");
    document.body.setAttribute("data-ob-lesson-record-owner-only", "true");
    document.body.setAttribute("data-ob-no-public-proof", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_009_FINAL_REVIEW_PERFORMANCE_STATE = {
      version: VERSION,
      status: finalReviewState.status,
      fallbackActive: finalReviewState.fallbackActive,
      lifecycleCount: payload.lifecycle_summary.length,
      reviewFieldCount: payload.review_fields.length,
      lessonFieldCount: payload.lesson_record.fields.length,
      finalReviewRequired: true,
      performanceReceiptOwnerOnly: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noPublicProof: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchFinalReview();
    }, 4140);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT_GP009_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return finalReviewState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchFinalReview,
    renderPanel,
    setFlags
  };
})();
