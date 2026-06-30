// OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER_JS
(function () {
  const VERSION = "OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER";
  const ENDPOINT = "/ob/real-candidate-rehearsal-adapter.json";

  // Real Candidate Rehearsal Adapter
  // real candidate adapter
  // engine candidate read-only handoff
  // candidate normalization
  // candidate to rehearsal mapping
  // symbol strategy score mapping
  // option candidate rehearsal mapping
  // stock fallback rehearsal mapping
  // observed-only candidate support
  // candidate source confidence
  // candidate freshness label
  // no order intent
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // Live Auto Locked

  let state = {
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
      status: "real_candidate_rehearsal_adapter_ready",
      source: "ob_giant_pack_017_safe_fallback",
      metrics: { mode: "read_only_adapter" },
      primary_items: [
        { item_id: "candidate_normalization", label: "Candidate normalization", purpose: "Normalize real engine candidates into rehearsal-safe shape.", status: "ready" },
        { item_id: "candidate_to_rehearsal_mapping", label: "Candidate to rehearsal mapping", purpose: "Map symbol, strategy, score, account fit, confidence, and freshness into rehearsal.", status: "ready" },
        { item_id: "option_candidate_rehearsal_mapping", label: "Option candidate rehearsal mapping", purpose: "Option candidates can be rehearsed without selecting or submitting real broker orders.", status: "ready" },
        { item_id: "stock_fallback_rehearsal_mapping", label: "Stock fallback rehearsal mapping", purpose: "Stock fallback can be rehearsed as an owner-only fake candidate path.", status: "ready" }
      ],
      secondary_items: [
        { item_id: "observed_only_support", label: "Observed-only candidate support", purpose: "Observed-only candidates can be rehearsed as watch/reject scenarios.", status: "ready" },
        { item_id: "source_confidence", label: "Candidate source confidence", purpose: "Candidate source confidence is visible before rehearsal starts.", status: "ready" },
        { item_id: "freshness_label", label: "Candidate freshness label", purpose: "Freshness label is carried into rehearsal gates.", status: "ready" }
      ],
      tertiary_items: [
        { item_id: "no_order_intent", label: "No order intent", purpose: "Adapter strips any execution meaning and produces rehearsal-only input.", status: "locked" },
        { item_id: "review_center_handoff", label: "Review Center handoff", purpose: "Adapted candidate can be shown in Review Center rehearsal command board.", status: "ready" }
      ],
      blocked_actions: ["submit_order_from_candidate", "read_broker_chain", "create_real_contract_selection", "auto_execute_candidate", "publish_candidate_proof"],
      boundaries: { real_candidate_adapter_only: true, read_only_candidate_handoff: true, no_order_intent: true, no_broker_api: true, no_broker_read: true, no_order_submit: true, no_auto_execution: true, live_auto_locked: true }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};
    return {
      ...fallback,
      ...safe,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        no_database_write: true,
        no_file_write: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_GP017_REAL_CANDIDATE_REHEARSAL_ADAPTER = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      ob_gp017_real_candidate_rehearsal_adapter: normalized,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obRealCandidateRehearsalAdapterUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchPayload() {
    state.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      state.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        state.status = "ready";
        state.source = normalized.source || "server";
        state.payload = normalized;
        state.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        state.status = "guarded_fallback";
        state.source = "guarded_fallback";
        state.payload = fallback;
        state.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      state.status = "error_fallback";
      state.source = "error_fallback";
      state.payload = fallback;
      state.fallbackActive = true;
      state.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return state;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("locked") || text.includes("failed") || text.includes("disabled") || text.includes("stale")) return "red";
    if (text.includes("ready") || text.includes("pass") || text.includes("allowed") || text.includes("complete")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-gp-batch-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-gp-batch-row">
        <div class="ob-gp-batch-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.name || item.rule_id || item.item_id || item.step_id || item.gate_id || item.lock_id, "Item")}</strong>
          <span>${safeText(item.status || item.severity || item.mode || item.source || "ready", "ready")}</span>
        </div>
        <span>${safeText(item.purpose || item.description || item.reason || item.next_action || item.required_action || "detail", "detail")}</span>
        <div class="ob-gp-batch-status ${tone(item.status || item.severity || item.mode)}">${safeText(item.status || item.severity || item.mode || "ready", "ready")}</div>
      </div>
    `;
  }

  function listRows(items, kind) {
    return (Array.isArray(items) ? items : []).map((item, index) => row(item, index, kind)).join("");
  }

  function panelHtml() {
    const payload = state.payload || buildFallbackPayload();
    const primary = payload.primary_items || [];
    const secondary = payload.secondary_items || [];
    const tertiary = payload.tertiary_items || [];
    const blocked = payload.blocked_actions || [];
    const metrics = payload.metrics || {};

    return `
      <div class="ob-gp17-real-candidate-adapter-panel" id="obRealCandidateRehearsalAdapterPanel" data-version="${VERSION}">
        <div class="ob-gp-batch-head">
          <div>
            <div class="ob-label">OB Giant Pack 017 · Real Candidate Adapter</div>
            <div class="ob-gp-batch-title">Real Candidate → Rehearsal Adapter</div>
            <div class="ob-gp-batch-subtitle">${safeText(state.status, "booting")} · ${safeText(payload.status, "ready")} · protected rehearsal layer.</div>
          </div>
          <div class="ob-gp-batch-chip-row">
            <span class="ob-gp-batch-chip green">Owner rehearsal</span>
            <span class="ob-gp-batch-chip gold">Read-only prep</span>
            <span class="ob-gp-batch-chip red">No broker/order</span>
            <span class="ob-gp-batch-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-gp-batch-stat-grid">
          ${card("Primary", String(primary.length))}
          ${card("Secondary", String(secondary.length))}
          ${card("Tertiary", String(tertiary.length))}
          ${card("Blocked", String(blocked.length))}
          ${card("Mode", safeText(metrics.mode || "rehearsal", "rehearsal"))}
        </div>

        <div class="ob-gp-batch-grid">
          <div>
            <div class="ob-gp-batch-card">
              <span>Purpose</span>
              <strong>Prepare real engine candidates to enter the rehearsal path as read-only rehearsal candidates, without order intent or broker action.</strong>
              <div class="ob-gp-batch-callout">
                <strong>Readiness note:</strong><br>
                This pack adds structure only. It does not write database records, read broker/bank data, submit orders, or upload to Vault.
              </div>
              <div class="ob-gp-batch-boundary">
                <strong>Boundary:</strong><br>
                No broker API. No broker read. No order submit. No auto execution. No direct Vault upload. Live Auto Locked.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-gp-batch-section">
              <div class="ob-gp-batch-section-title">Primary items</div>
              <div class="ob-gp-batch-list">${listRows(primary, "P")}</div>
            </div>
            <div class="ob-gp-batch-section">
              <div class="ob-gp-batch-section-title">Secondary items</div>
              <div class="ob-gp-batch-list">${listRows(secondary, "S")}</div>
            </div>
            <div class="ob-gp-batch-section">
              <div class="ob-gp-batch-section-title">Tertiary items</div>
              <div class="ob-gp-batch-list">${listRows(tertiary, "T")}</div>
            </div>
            <div class="ob-gp-batch-section">
              <div class="ob-gp-batch-section-title">Blocked actions</div>
              <div class="ob-gp-batch-list">${listRows(blocked.map((x) => ({ label: x, status: "blocked", purpose: "Blocked by protected rehearsal boundaries." })), "×")}</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obRealCandidateRehearsalAdapterPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const anchors = ['obTowerStepUpEnforcementPrepPanel','obMissionAccountCapitalRuleRehearsalOverlayPanel'];
    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    for (const id of anchors) {
      const anchor = document.getElementById(id);
      if (anchor && anchor.parentNode) {
        anchor.insertAdjacentElement("afterend", panel);
        return;
      }
    }

    layer.prepend(panel);
  }

  function setFlags() {
    document.body.setAttribute("data-" + VERSION.toLowerCase().replace(/_/g, "-"), "ready");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window[VERSION + "_STATE"] = {
      version: VERSION,
      status: state.status,
      fallbackActive: state.fallbackActive,
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
      fetchPayload();
    }, 5400);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window[VERSION + "_API"] = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return state; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchPayload,
    renderPanel,
    setFlags
  };
})();
