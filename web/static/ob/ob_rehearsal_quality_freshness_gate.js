// OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE_JS
(function () {
  const VERSION = "OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE";
  const ENDPOINT = "/ob/rehearsal-quality-freshness-gate.json";

  // Rehearsal Quality Freshness Gate
  // quality freshness gate
  // data freshness check
  // source confidence check
  // stale candidate block
  // missing field block
  // incomplete rehearsal block
  // low confidence warning
  // owner note required
  // Review Center quality warning
  // no broker API
  // no order submit
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
      status: "quality_freshness_gate_ready",
      source: "ob_giant_pack_019_safe_fallback",
      metrics: { mode: "quality_freshness_gate" },
      primary_items: [
        { rule_id: "data_freshness_check", label: "Data freshness check", purpose: "Rehearsal candidate must show fresh/aging/stale/unknown status.", status: "ready" },
        { rule_id: "source_confidence_check", label: "Source confidence check", purpose: "Owner sees whether candidate is system-generated, owner-entered, verified, or needs verification.", status: "ready" },
        { rule_id: "stale_candidate_block", label: "Stale candidate block", purpose: "Stale or unknown candidate cannot be promoted as practice-ready without warning.", status: "ready" },
        { rule_id: "missing_field_block", label: "Missing field block", purpose: "Missing required rehearsal fields block final readiness.", status: "ready" }
      ],
      secondary_items: [
        { rule_id: "incomplete_rehearsal_block", label: "Incomplete rehearsal block", purpose: "Incomplete rehearsal cannot count as owner-ready.", status: "ready" },
        { rule_id: "low_confidence_warning", label: "Low confidence warning", purpose: "Low confidence data requires owner note.", status: "ready" },
        { rule_id: "owner_note_required", label: "Owner note required", purpose: "Owner note required when confidence/freshness fails.", status: "ready" }
      ],
      tertiary_items: [
        { rule_id: "review_center_quality_warning", label: "Review Center quality warning", purpose: "Review Center shows quality warnings before final readiness.", status: "ready" },
        { rule_id: "source_of_truth_label", label: "Source-of-truth label", purpose: "Each rehearsal record keeps source/freshness/confidence labels.", status: "ready" }
      ],
      blocked_actions: ["mark_stale_candidate_ready", "complete_without_required_fields", "hide_quality_warning", "claim_verified_without_source"],
      boundaries: { quality_gate_only: true, no_database_write: true, no_broker_api: true, no_order_submit: true, live_auto_locked: true }
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
    window.OB_GP019_REHEARSAL_QUALITY_FRESHNESS_GATE = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      ob_gp019_rehearsal_quality_freshness_gate: normalized,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obRehearsalQualityFreshnessGateUpdated", { detail: normalized }));
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
      <div class="ob-gp19-quality-freshness-panel" id="obRehearsalQualityFreshnessGatePanel" data-version="${VERSION}">
        <div class="ob-gp-batch-head">
          <div>
            <div class="ob-label">OB Giant Pack 019 · Quality + Freshness Gate</div>
            <div class="ob-gp-batch-title">Rehearsal Quality & Freshness Gate</div>
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
              <strong>Add a quality and freshness gate so rehearsal inputs, candidates, and lessons cannot look reliable when stale, unverified, incomplete, or low-confidence.</strong>
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
    const existing = document.getElementById("obRehearsalQualityFreshnessGatePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const anchors = ['obManualLiveOwnerRehearsalFinalReadinessPanel','obRealCandidateRehearsalAdapterPanel'];
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
