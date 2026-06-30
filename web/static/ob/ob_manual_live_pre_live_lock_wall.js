// OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL_JS
(function () {
  const VERSION = "OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL";
  const ENDPOINT = "/ob/manual-live-pre-live-lock-wall.json";

  // Manual Live Pre-Live Lock Wall
  // pre-live lock wall
  // real Manual Live remains locked
  // owner rehearsal allowed
  // broker action blocked
  // bank action blocked
  // database write blocked
  // Vault direct upload blocked
  // Hybrid locked
  // Automated locked
  // Live Auto Locked
  // batch close readiness
  // GP017 through GP020 closeout
  // no broker API
  // no order submit

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
      status: "pre_live_lock_wall_ready",
      source: "ob_giant_pack_020_safe_fallback",
      metrics: { mode: "pre_live_lock_wall" },
      primary_items: [
        { lock_id: "owner_rehearsal_allowed", label: "Owner rehearsal allowed", purpose: "Owner may continue safe fake/demo rehearsal.", status: "ready" },
        { lock_id: "real_manual_live_locked", label: "Real Manual Live locked", purpose: "Real Manual Live remains blocked until future Tower clearance.", status: "locked" },
        { lock_id: "broker_action_blocked", label: "Broker action blocked", purpose: "OB cannot read broker, select live contract, submit order, or close order.", status: "locked" },
        { lock_id: "bank_action_blocked", label: "Bank action blocked", purpose: "OB cannot read bank or move capital.", status: "locked" },
        { lock_id: "database_write_blocked", label: "Database write blocked", purpose: "Rehearsal persistence remains contract/prep only.", status: "locked" }
      ],
      secondary_items: [
        { lock_id: "vault_direct_upload_blocked", label: "Vault direct upload blocked", purpose: "Vault-ready placeholders only; no OB direct upload.", status: "locked" },
        { lock_id: "hybrid_locked", label: "Hybrid locked", purpose: "Hybrid remains locked behind future Tower policy.", status: "locked" },
        { lock_id: "automated_locked", label: "Automated locked", purpose: "Automated remains locked behind future Tower policy.", status: "locked" },
        { lock_id: "live_auto_locked", label: "Live Auto Locked", purpose: "Live Auto Locked stays visible across rooms.", status: "locked" }
      ],
      tertiary_items: [
        { item_id: "batch_close_readiness", label: "Batch close readiness", purpose: "GP017-GP020 can be saved together after passing.", status: "ready" },
        { item_id: "next_batch_ready", label: "Next batch ready", purpose: "Next batch can move toward persistence adapter or beta rehearsal polish.", status: "ready" }
      ],
      blocked_actions: ["enable_real_manual_live", "connect_broker_api", "read_bank_account", "write_database", "upload_direct_to_vault", "enable_hybrid", "enable_automated"],
      boundaries: { pre_live_lock_wall: true, owner_rehearsal_allowed: true, real_manual_live_locked: true, hybrid_locked: true, automated_locked: true, no_broker_api: true, no_order_submit: true, live_auto_locked: true }
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
    window.OB_GP020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      ob_gp020_manual_live_pre_live_lock_wall: normalized,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obManualLivePreLiveLockWallUpdated", { detail: normalized }));
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
      <div class="ob-gp20-pre-live-lock-wall-panel" id="obManualLivePreLiveLockWallPanel" data-version="${VERSION}">
        <div class="ob-gp-batch-head">
          <div>
            <div class="ob-label">OB Giant Pack 020 · Pre-Live Lock Wall</div>
            <div class="ob-gp-batch-title">Manual Live Pre-Live Lock Wall</div>
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
              <strong>Close the rehearsal batch with a hard pre-live lock wall: owner practice can continue, but real Manual Live, Hybrid, Automated, broker actions, bank actions, and database writes remain blocked.</strong>
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
    const existing = document.getElementById("obManualLivePreLiveLockWallPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const anchors = ['obRehearsalQualityFreshnessGatePanel','obManualLiveOwnerRehearsalFinalReadinessPanel'];
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
