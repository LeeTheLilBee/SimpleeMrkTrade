// OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS_JS
(function () {
  const VERSION = "OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS";
  const ENDPOINT = "/ob/manual-live-owner-rehearsal-final-readiness.json";

  // Manual Live Owner Rehearsal Final Readiness
  // owner rehearsal final readiness
  // full rehearsal stack checklist
  // GP011 through GP017 readiness
  // owner practice ready
  // missing rehearsal blockers
  // manual live readiness label
  // real manual live remains locked
  // hybrid remains locked
  // automated remains locked
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
      status: "owner_rehearsal_final_readiness_ready",
      source: "ob_giant_pack_018_safe_fallback",
      metrics: { mode: "owner_practice_ready_check" },
      primary_items: [
        { item_id: "gp011_ready", label: "GP011 rehearsal engine", purpose: "Owner rehearsal engine and fake candidate walkthrough exist.", status: "ready" },
        { item_id: "gp012_ready", label: "GP012 record contracts", purpose: "Rehearsal record contracts exist.", status: "ready" },
        { item_id: "gp013_ready", label: "GP013 command board", purpose: "Review Center command board exists.", status: "ready" },
        { item_id: "gp014_ready", label: "GP014 owner input prep", purpose: "Drafts, validation, autosave placeholder, and submit gate placeholder exist.", status: "ready" },
        { item_id: "gp015_ready", label: "GP015 capital rules", purpose: "Mission account capital rule rehearsal overlay exists.", status: "ready" },
        { item_id: "gp016_ready", label: "GP016 Tower step-up prep", purpose: "Tower step-up request/approval placeholders exist.", status: "ready" },
        { item_id: "gp017_ready", label: "GP017 candidate adapter", purpose: "Real candidate to rehearsal adapter exists.", status: "ready" }
      ],
      secondary_items: [
        { item_id: "owner_practice_ready", label: "Owner practice ready", purpose: "Safe to rehearse repeatedly using demo/fake data.", status: "ready" },
        { item_id: "real_manual_live_locked", label: "Real Manual Live locked", purpose: "Readiness is for rehearsal only; real Manual Live remains locked.", status: "locked" },
        { item_id: "missing_blockers", label: "Missing blockers", purpose: "No rehearsal blockers remain for owner practice path.", status: "complete" }
      ],
      tertiary_items: [
        { item_id: "manual_live_readiness_label", label: "Manual Live readiness label", purpose: "manual_live_owner_rehearsal_ready, not real_manual_live_ready.", status: "ready" },
        { item_id: "hybrid_automated_locked", label: "Hybrid/Automated locked", purpose: "Hybrid and automated remain locked behind Tower policy.", status: "locked" }
      ],
      blocked_actions: ["start_real_manual_live", "enable_hybrid", "enable_automated", "submit_order_from_ob", "read_broker_account"],
      boundaries: { owner_practice_ready: true, real_manual_live_locked: true, hybrid_locked: true, automated_locked: true, no_broker_api: true, no_order_submit: true, live_auto_locked: true }
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
    window.OB_GP018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      ob_gp018_manual_live_owner_rehearsal_final_readiness: normalized,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obManualLiveOwnerRehearsalFinalReadinessUpdated", { detail: normalized }));
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
      <div class="ob-gp18-final-readiness-panel" id="obManualLiveOwnerRehearsalFinalReadinessPanel" data-version="${VERSION}">
        <div class="ob-gp-batch-head">
          <div>
            <div class="ob-label">OB Giant Pack 018 · Owner Rehearsal Final Readiness</div>
            <div class="ob-gp-batch-title">Owner Rehearsal Final Readiness</div>
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
              <strong>Summarize the full owner rehearsal stack and decide whether the rehearsal layer is ready for repeated owner practice.</strong>
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
    const existing = document.getElementById("obManualLiveOwnerRehearsalFinalReadinessPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const anchors = ['obRealCandidateRehearsalAdapterPanel','obTowerStepUpEnforcementPrepPanel'];
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
