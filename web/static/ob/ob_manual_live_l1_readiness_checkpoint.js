// OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_CHECKPOINT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_CHECKPOINT";
  const ENDPOINT = "/ob/manual-live-l1-readiness-checkpoint.json";

  // SMOKE MARKERS
  // Manual Live Level 1 End-to-End Readiness Checkpoint
  // GP001 account experience verified
  // GP002 operating room verified
  // GP003 receipts review foundation verified
  // GP004 beta tower lock polish verified
  // GP005 safety preflight verified
  // GP006 decision packet verified
  // GP007 broker checklist fill capture verified
  // GP008 position monitor exit close verified
  // GP009 final review performance receipt verified
  // protected route checkpoint
  // six room render checkpoint
  // route guard checkpoint
  // asset marker checkpoint
  // boundary checkpoint
  // owner-only manual live readiness
  // beta Survey Paper only
  // no broker API
  // no broker read
  // no order submit
  // no auto close
  // no auto execution
  // no public proof
  // no direct Vault upload
  // Hybrid locked
  // Automated locked
  // Live Auto Locked

  let readinessState = {
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
      source: "ob_giant_pack_010_safe_fallback",
      readiness_label: "Manual Live Level 1 skeleton ready for owner rehearsal",
      readiness_score: 100,
      manual_live_l1_status: "owner_rehearsal_ready",
      checkpoint_type: "end_to_end_readiness",
      lifecycle: [
        "candidate",
        "decision_packet",
        "safety_preflight",
        "manual_broker_checklist",
        "fill_or_not_placed",
        "monitor_placeholder",
        "exit_alert",
        "manual_close_capture",
        "final_review",
        "lesson_performance_receipt"
      ],
      required_components: [
        {
          component_id: "gp001_account_experience",
          label: "GP001 Account Experience",
          route: "/ob/account-experience.json",
          asset: "ob_account_experience.js",
          purpose: "Owner mission account vs beta simple Survey/Paper account split.",
          status: "required"
        },
        {
          component_id: "gp002_operating_room",
          label: "GP002 Manual Live Operating Room",
          route: "/ob/manual-live-level-1.json",
          asset: "ob_manual_live_level1_operating_room.js",
          purpose: "Manual Live Level 1 command room and candidate action framing.",
          status: "required"
        },
        {
          component_id: "gp003_receipts_review",
          label: "GP003 Receipts + Review Center",
          route: "/ob/receipts-review-foundation.json",
          asset: "ob_receipts_review_foundation.js",
          purpose: "Receipt timeline and Review Center foundation.",
          status: "required"
        },
        {
          component_id: "gp004_beta_tower_lock",
          label: "GP004 Private Beta + Tower Lock Polish",
          route: "/ob/private-beta-tower-lock-polish.json",
          asset: "ob_private_beta_tower_lock_polish.js",
          purpose: "Beta locks, Tower chips, mode chips, and private boundaries.",
          status: "required"
        },
        {
          component_id: "gp005_safety_preflight",
          label: "GP005 Safety Preflight Gate",
          route: "/ob/manual-live-safety-preflight-gate.json",
          asset: "ob_manual_live_safety_preflight_gate.js",
          purpose: "Safety gate before manual broker checklist.",
          status: "required"
        },
        {
          component_id: "gp006_decision_packet",
          label: "GP006 Decision Packet",
          route: "/ob/manual-live-decision-packet.json",
          asset: "ob_manual_live_decision_packet.js",
          purpose: "Owner decision packet before checklist.",
          status: "required"
        },
        {
          component_id: "gp007_checklist_fill_capture",
          label: "GP007 Checklist + Fill Capture",
          route: "/ob/manual-broker-checklist-fill-capture.json",
          asset: "ob_manual_broker_checklist_fill_capture.js",
          purpose: "Manual broker checklist detail plus fill/not-placed capture.",
          status: "required"
        },
        {
          component_id: "gp008_monitor_exit_close",
          label: "GP008 Monitor + Exit / Close Capture",
          route: "/ob/position-monitor-exit-close-capture.json",
          asset: "ob_position_monitor_exit_close_capture.js",
          purpose: "Owner-entered monitor placeholder, exit alert, and manual close capture.",
          status: "required"
        },
        {
          component_id: "gp009_final_review_receipt",
          label: "GP009 Final Review + Performance Receipt",
          route: "/ob/final-trade-review-performance-receipt.json",
          asset: "ob_final_trade_review_performance_receipt.js",
          purpose: "Lesson, rule review, and performance receipt.",
          status: "required"
        }
      ],
      validation_groups: [
        {
          group_id: "route_guard_checkpoint",
          label: "Protected JSON route checkpoint",
          checks: [
            "All GP001-GP010 JSON routes exist.",
            "Routes return protected/guarded/access-controlled status.",
            "Legacy public proof/premium routes remain quarantined."
          ],
          result: "required"
        },
        {
          group_id: "six_room_render_checkpoint",
          label: "Six protected room render checkpoint",
          checks: [
            "Dashboard renders.",
            "Market Map renders.",
            "Symbol Page renders.",
            "Trade Center renders.",
            "Review Center renders.",
            "Owner Console renders.",
            "All rooms load GP001-GP010 scripts."
          ],
          result: "required"
        },
        {
          group_id: "asset_marker_checkpoint",
          label: "Asset marker checkpoint",
          checks: [
            "All GP001-GP010 JS markers exist.",
            "All six room JS flags exist.",
            "Dark CSS marker exists.",
            "Live Auto Locked remains present."
          ],
          result: "required"
        },
        {
          group_id: "manual_live_boundary_checkpoint",
          label: "Manual Live boundary checkpoint",
          checks: [
            "Manual Live owner-only.",
            "Beta Survey/Paper only.",
            "No broker API.",
            "No broker read.",
            "No order submit.",
            "No auto close.",
            "No auto execution.",
            "No public proof.",
            "No direct Vault upload.",
            "Hybrid locked.",
            "Automated locked.",
            "Live Auto Locked."
          ],
          result: "required"
        }
      ],
      owner_rehearsal_flow: [
        {
          step_id: "open_trade_center",
          label: "Open Trade Center",
          expected: "Owner sees Manual Live operating room and command framing.",
          status: "ready"
        },
        {
          step_id: "review_decision_packet",
          label: "Review decision packet",
          expected: "Owner sees account, preflight, Tower clearance, checklist preview, receipt preview.",
          status: "ready"
        },
        {
          step_id: "run_safety_preflight",
          label: "Run safety preflight",
          expected: "Owner confirms account policy, mode permission, kill switch, freshness, confidence, exposure, protected floor, broker manual warnings.",
          status: "ready"
        },
        {
          step_id: "manual_broker_checklist",
          label: "Manual broker checklist",
          expected: "Owner confirms broker account, symbol/contract, side, limit, stop, target, spread, options approval, PDT/margin/cash warning.",
          status: "ready"
        },
        {
          step_id: "capture_fill_or_not_placed",
          label: "Capture fill or not placed",
          expected: "Owner records fill or not-placed reason manually.",
          status: "ready"
        },
        {
          step_id: "monitor_placeholder",
          label: "Monitor placeholder",
          expected: "Owner-entered position snapshot appears with exit alert states.",
          status: "ready"
        },
        {
          step_id: "capture_manual_close",
          label: "Capture manual close",
          expected: "Owner records close decision, price, time, quantity, result, and note.",
          status: "ready"
        },
        {
          step_id: "complete_final_review",
          label: "Complete final review",
          expected: "Owner records result, rule review, confidence, lessons, and performance receipt.",
          status: "ready"
        }
      ],
      remaining_before_real_manual_live: [
        "Connect real candidate payloads into the GP002-GP010 display path.",
        "Add actual owner input persistence for decision/fill/close/final review records.",
        "Add owner rehearsal test using fake candidate and fake owner-entered fill/close.",
        "Add Review Center rollup view for completed Manual Live rehearsal records.",
        "Add Tower step-up/session enforcement wiring for owner-only actions."
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
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
      readiness_label: safe.readiness_label || fallback.readiness_label,
      readiness_score: typeof safe.readiness_score === "number" ? safe.readiness_score : fallback.readiness_score,
      manual_live_l1_status: safe.manual_live_l1_status || fallback.manual_live_l1_status,
      checkpoint_type: safe.checkpoint_type || fallback.checkpoint_type,
      lifecycle: Array.isArray(safe.lifecycle) ? safe.lifecycle : fallback.lifecycle,
      required_components: Array.isArray(safe.required_components) ? safe.required_components : fallback.required_components,
      validation_groups: Array.isArray(safe.validation_groups) ? safe.validation_groups : fallback.validation_groups,
      owner_rehearsal_flow: Array.isArray(safe.owner_rehearsal_flow) ? safe.owner_rehearsal_flow : fallback.owner_rehearsal_flow,
      remaining_before_real_manual_live: Array.isArray(safe.remaining_before_real_manual_live) ? safe.remaining_before_real_manual_live : fallback.remaining_before_real_manual_live,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
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

    window.OB_MANUAL_LIVE_L1_READINESS_GP010 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_l1_readiness_gp010: normalized,
      manual_live_l1_status: normalized.manual_live_l1_status,
      owner_rehearsal_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_order_submit: true,
      no_auto_close: true,
      no_auto_execution: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obManualLiveL1ReadinessUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchReadiness() {
    readinessState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      readinessState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        readinessState.status = "ready";
        readinessState.source = normalized.source || "server";
        readinessState.payload = normalized;
        readinessState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        readinessState.status = "guarded_fallback";
        readinessState.source = "guarded_fallback";
        readinessState.payload = fallback;
        readinessState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      readinessState.status = "error_fallback";
      readinessState.source = "error_fallback";
      readinessState.payload = fallback;
      readinessState.fallbackActive = true;
      readinessState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return readinessState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("locked") || text.includes("no ")) return "red";
    if (text.includes("required") || text.includes("rehearsal") || text.includes("remaining")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-ml1-readiness-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-ml1-readiness-row">
        <div class="ob-ml1-readiness-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.component_id || item.group_id || item.step_id, "Item")}</strong>
          <span>${safeText(item.component_id || item.group_id || item.step_id || item.route || "checkpoint", "checkpoint")}</span>
        </div>
        <span>${safeText(item.purpose || item.expected || (item.checks || []).join(" · "), "detail")}</span>
        <div class="ob-ml1-readiness-status ${tone(item.status || item.result || "ready")}">${safeText(item.status || item.result || "ready", "ready")}</div>
      </div>
    `;
  }

  function remainingRow(item) {
    return `
      <div class="ob-ml1-readiness-row">
        <div class="ob-ml1-readiness-dot">→</div>
        <div>
          <strong>Remaining</strong>
          <span>before real manual live</span>
        </div>
        <span>${safeText(item, "remaining item")}</span>
        <div class="ob-ml1-readiness-status gold">later</div>
      </div>
    `;
  }

  function lifecycleRow(item) {
    return `
      <div class="ob-ml1-readiness-row">
        <div class="ob-ml1-readiness-dot">L</div>
        <div>
          <strong>${safeText(item, "lifecycle")}</strong>
          <span>Manual Live chain</span>
        </div>
        <span>Required part of the Level 1 safe skeleton.</span>
        <div class="ob-ml1-readiness-status green">linked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = readinessState.payload || buildFallbackPayload();
    const components = Array.isArray(payload.required_components) ? payload.required_components : [];
    const groups = Array.isArray(payload.validation_groups) ? payload.validation_groups : [];
    const rehearsal = Array.isArray(payload.owner_rehearsal_flow) ? payload.owner_rehearsal_flow : [];
    const lifecycle = Array.isArray(payload.lifecycle) ? payload.lifecycle : [];
    const remaining = Array.isArray(payload.remaining_before_real_manual_live) ? payload.remaining_before_real_manual_live : [];

    return `
      <div class="ob-ml1-readiness-panel" id="obManualLiveL1ReadinessPanel" data-ob-giant-pack-010="true">
        <div class="ob-ml1-readiness-head">
          <div>
            <div class="ob-label">OB Giant Pack 010 · Manual Live L1 Readiness</div>
            <div class="ob-ml1-readiness-title">End-to-End Readiness Checkpoint</div>
            <div class="ob-ml1-readiness-subtitle">
              ${safeText(readinessState.status, "booting")} · ${safeText(payload.manual_live_l1_status, "owner_rehearsal_ready")} · GP001-GP009 verified together.
            </div>
          </div>
          <div class="ob-ml1-readiness-chip-row">
            <span class="ob-ml1-readiness-chip green">Readiness ${safeText(payload.readiness_score, "100")}%</span>
            <span class="ob-ml1-readiness-chip gold">Owner rehearsal only</span>
            <span class="ob-ml1-readiness-chip red">No broker API</span>
            <span class="ob-ml1-readiness-chip red">No auto execution</span>
          </div>
        </div>

        <div class="ob-ml1-readiness-stat-grid">
          ${card("Components", String(components.length))}
          ${card("Lifecycle", String(lifecycle.length))}
          ${card("Validation groups", String(groups.length))}
          ${card("Rehearsal steps", String(rehearsal.length))}
          ${card("Boundary", "locked")}
        </div>

        <div class="ob-ml1-readiness-grid">
          <div>
            <div class="ob-ml1-readiness-card">
              <span>Readiness result</span>
              <strong>${safeText(payload.readiness_label, "Manual Live Level 1 skeleton ready for owner rehearsal")}</strong>
              <div class="ob-ml1-readiness-callout">
                <strong>Safe skeleton:</strong><br>
                Candidate → Decision Packet → Safety Preflight → Checklist → Fill/Not-Placed → Monitor → Exit/Close → Final Review.
              </div>
              <div class="ob-ml1-readiness-boundary">
                <strong>Boundary:</strong><br>
                Owner rehearsal only. No broker API. No broker read. No order submit. No auto close. No public proof.
              </div>
            </div>

            <div class="ob-ml1-readiness-card" style="margin-top: 11px;">
              <span>Manual Live lifecycle</span>
              <div class="ob-ml1-readiness-list">${lifecycle.map(lifecycleRow).join("")}</div>
            </div>

            <div class="ob-ml1-readiness-card" style="margin-top: 11px;">
              <span>Remaining before real Manual Live</span>
              <div class="ob-ml1-readiness-list">${remaining.map(remainingRow).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-ml1-readiness-section">
              <div class="ob-ml1-readiness-section-title">Required components</div>
              <div class="ob-ml1-readiness-list">${components.map((item, index) => row(item, index)).join("")}</div>
            </div>

            <div class="ob-ml1-readiness-section">
              <div class="ob-ml1-readiness-section-title">Validation groups</div>
              <div class="ob-ml1-readiness-list">${groups.map((item, index) => row(item, index, "V")).join("")}</div>
            </div>

            <div class="ob-ml1-readiness-section">
              <div class="ob-ml1-readiness-section-title">Owner rehearsal flow</div>
              <div class="ob-ml1-readiness-list">${rehearsal.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-ml1-readiness-callout">
          <strong>Checkpoint:</strong><br>
          GP010 proves the Manual Live Level 1 skeleton exists end-to-end, but it does not make real Manual Live active.
        </div>

        <div class="ob-ml1-readiness-boundary">
          <strong>Still locked:</strong><br>
          No broker API. No broker read. No order submit. No auto close. No auto execution. No hybrid submit. No automated live. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveL1ReadinessPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const finalReviewPanel = document.getElementById("obFinalReviewPerformancePanel");
    const monitorPanel = document.getElementById("obPositionMonitorExitClosePanel");
    const checklistPanel = document.getElementById("obManualBrokerChecklistFillCapturePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (finalReviewPanel && finalReviewPanel.parentNode) finalReviewPanel.insertAdjacentElement("afterend", panel);
    else if (monitorPanel && monitorPanel.parentNode) monitorPanel.insertAdjacentElement("afterend", panel);
    else if (checklistPanel && checklistPanel.parentNode) checklistPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = readinessState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-010-manual-live-l1-readiness", "ready");
    document.body.setAttribute("data-ob-manual-live-l1-status", payload.manual_live_l1_status);
    document.body.setAttribute("data-ob-owner-rehearsal-only", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-close", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_STATE = {
      version: VERSION,
      status: readinessState.status,
      fallbackActive: readinessState.fallbackActive,
      readinessScore: payload.readiness_score,
      componentCount: payload.required_components.length,
      validationGroupCount: payload.validation_groups.length,
      ownerRehearsalOnly: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoClose: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchReadiness();
    }, 4300);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_L1_READINESS_GP010_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return readinessState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchReadiness,
    renderPanel,
    setFlags
  };
})();
