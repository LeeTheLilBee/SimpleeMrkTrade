// OBSERVATORY_V25_SAFE_ENGINE_FEED_ADAPTER_JS

(function () {
  const ADAPTER_VERSION = "OB_V25_SAFE_ENGINE_FEED_ADAPTER";
  const ENDPOINT = "/ob/engine-feed-snapshot.json";

  let adapterState = {
    status: "booting",
    source: "unknown",
    httpStatus: null,
    payload: null,
    error: null,
    fallbackActive: true,
    loadedAt: null
  };

  function count(value) {
    return Array.isArray(value) ? value.length : 0;
  }

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function fallbackSnapshot() {
    const contracts = window.OB_DATA_CONTRACTS_V22;

    if (!contracts) {
      return {
        source: "fallback_no_contracts",
        market_health: { label: "Fallback waiting", breadth: "0 symbols" },
        positions_preview: [],
        candidates_preview: [],
        manual_live_queue: [],
        review_summary: { receipts: 0 },
        tower_boundaries: {
          no_broker_api: true,
          no_auto_execution: true,
          live_auto_locked: true
        }
      };
    }

    const trade = contracts.tradeCenterContract ? contracts.tradeCenterContract() : {};
    const review = contracts.reviewCenterContract ? contracts.reviewCenterContract() : {};
    const health = contracts.marketHealth ? contracts.marketHealth() : { label: "Preview fallback", breadth: "Preview" };

    return {
      source: "v22_preview_contract_fallback",
      market_health: health,
      positions_preview: trade.open_positions || [],
      candidates_preview: trade.candidates || [],
      manual_live_queue: trade.manual_live_queue || [],
      review_summary: {
        receipts: count(review.journal_receipts)
      },
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      }
    };
  }

  function normalizePayload(payload) {
    const fallback = fallbackSnapshot();
    const safe = payload && typeof payload === "object" ? payload : {};

    return {
      version: safe.version || ADAPTER_VERSION,
      source: safe.source || fallback.source,
      adapter_status: safe.adapter_status || "normalized",
      market_health: safe.market_health || fallback.market_health,
      positions_preview: Array.isArray(safe.positions_preview) ? safe.positions_preview : fallback.positions_preview,
      candidates_preview: Array.isArray(safe.candidates_preview) ? safe.candidates_preview : fallback.candidates_preview,
      manual_live_queue: Array.isArray(safe.manual_live_queue) ? safe.manual_live_queue : fallback.manual_live_queue,
      review_summary: safe.review_summary || fallback.review_summary,
      data_files: safe.data_files || {},
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : ["Using safe normalized adapter payload."],
      room_contract_hint: safe.room_contract_hint || {},
      raw_meta: safe.raw_meta || {}
    };
  }

  function exposeServerData(payload) {
    const normalized = normalizePayload(payload);

    window.OB_ENGINE_FEED_SNAPSHOT_V25 = normalized;

    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      engine_feed_v25: normalized,
      market_health: normalized.market_health,
      positions_preview: normalized.positions_preview,
      candidates_preview: normalized.candidates_preview,
      manual_live_queue: normalized.manual_live_queue,
      review_summary: normalized.review_summary
    };

    window.dispatchEvent(new CustomEvent("obEngineFeedAdapterUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchEngineSnapshot() {
    adapterState.status = "loading";
    adapterState.loadedAt = new Date().toISOString();

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: {
          "Accept": "application/json"
        }
      });

      adapterState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = exposeServerData(payload);

        adapterState.status = "ready";
        adapterState.source = normalized.source || "guarded_snapshot";
        adapterState.payload = normalized;
        adapterState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = exposeServerData(fallbackSnapshot());

        adapterState.status = "guarded_fallback";
        adapterState.source = "guarded_route_preview_fallback";
        adapterState.payload = fallback;
        adapterState.fallbackActive = true;
        adapterState.error = "Engine feed route is protected or redirected. Preview fallback is active.";
      } else {
        const fallback = exposeServerData(fallbackSnapshot());

        adapterState.status = "http_fallback";
        adapterState.source = "http_" + response.status + "_fallback";
        adapterState.payload = fallback;
        adapterState.fallbackActive = true;
        adapterState.error = "Engine feed returned HTTP " + response.status + ". Preview fallback is active.";
      }
    } catch (error) {
      const fallback = exposeServerData(fallbackSnapshot());

      adapterState.status = "error_fallback";
      adapterState.source = "fetch_error_fallback";
      adapterState.payload = fallback;
      adapterState.fallbackActive = true;
      adapterState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    updateEngineBar();
    return adapterState;
  }

  function closeDrawer() {
    const existing = document.getElementById("obEngineFeedBackdrop");
    if (existing) existing.remove();
  }

  function boundaryValue(value) {
    return value ? "Yes" : "No";
  }

  function row(title, detail, index) {
    return `
      <div class="ob-engine-feed-row">
        <div class="ob-engine-feed-dot">${index + 1}</div>
        <div class="ob-engine-feed-copy">
          <strong>${title}</strong>
          <span>${detail}</span>
        </div>
      </div>
    `;
  }

  function openEngineDrawer() {
    closeDrawer();

    const payload = adapterState.payload || fallbackSnapshot();
    const boundaries = payload.tower_boundaries || {};

    const backdrop = document.createElement("div");
    backdrop.id = "obEngineFeedBackdrop";
    backdrop.className = "ob-engine-feed-backdrop open";

    const drawer = document.createElement("div");
    drawer.className = "ob-engine-feed-drawer";

    drawer.innerHTML = `
      <div class="ob-engine-feed-head">
        <div>
          <strong>Safe Engine Feed Adapter</strong>
          <span>V25 read-only bridge. It can read protected snapshot data when allowed and falls back safely when blocked.</span>
        </div>
        <button class="ob-engine-feed-close" id="obEngineFeedClose">×</button>
      </div>

      <div class="ob-engine-feed-grid">
        <div class="ob-engine-feed-card"><span>Status</span><strong>${safeText(adapterState.status, "unknown")}</strong></div>
        <div class="ob-engine-feed-card"><span>HTTP</span><strong>${safeText(adapterState.httpStatus, "not requested")}</strong></div>
        <div class="ob-engine-feed-card"><span>Source</span><strong>${safeText(payload.source, adapterState.source)}</strong></div>
        <div class="ob-engine-feed-card"><span>Positions</span><strong>${count(payload.positions_preview)}</strong></div>
        <div class="ob-engine-feed-card"><span>Candidates</span><strong>${count(payload.candidates_preview)}</strong></div>
        <div class="ob-engine-feed-card"><span>Manual queue</span><strong>${count(payload.manual_live_queue)}</strong></div>
      </div>

      <div class="ob-engine-feed-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        This is a bridge, not permission. Real data can make OB smarter, but it cannot bypass Tower locks, mission account rules, or Manual Live Level 1.
      </div>

      <div class="ob-engine-feed-warning">
        <strong>Read-only boundary:</strong><br>
        Broker API: ${boundaryValue(!boundaries.no_broker_api)} ·
        Auto execution: ${boundaryValue(!boundaries.no_auto_execution)} ·
        Live Auto Locked: ${boundaryValue(boundaries.live_auto_locked)}
      </div>

      <div class="ob-engine-feed-list">
        ${row("Market health", `${safeText(payload.market_health && payload.market_health.label, "Unknown")} · ${safeText(payload.market_health && payload.market_health.breadth, "No breadth")}`, 0)}
        ${row("Data files", `market_universe: ${safeText(payload.data_files && payload.data_files.market_universe, "unknown")} · pipeline_status: ${safeText(payload.data_files && payload.data_files.pipeline_status, "unknown")}`, 1)}
        ${row("Fallback", adapterState.fallbackActive ? "Preview fallback is active." : "Protected snapshot data loaded.", 2)}
        ${row("Warnings", (payload.warnings || []).join(" · ") || "No warnings.", 3)}
      </div>

      <div class="ob-engine-feed-actions-row">
        <button class="ob-engine-feed-button" id="obEngineFeedRefresh">Refresh adapter</button>
        <button class="ob-engine-feed-button gold" id="obEngineFeedContracts">Open data contracts</button>
        <button class="ob-engine-feed-button red" id="obEngineFeedCloseFooter">Close</button>
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obEngineFeedClose").addEventListener("click", closeDrawer);
    document.getElementById("obEngineFeedCloseFooter").addEventListener("click", closeDrawer);

    const refresh = document.getElementById("obEngineFeedRefresh");
    if (refresh) {
      refresh.addEventListener("click", async function () {
        await fetchEngineSnapshot();
        openEngineDrawer();
      });
    }

    const contracts = document.getElementById("obEngineFeedContracts");
    if (contracts) {
      contracts.addEventListener("click", function () {
        if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.openDataDrawer) {
          window.OB_DATA_CONTRACTS_V22.openDataDrawer();
        }
      });
    }

    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });
  }

  function updateEngineBar() {
    const bar = document.getElementById("obEngineFeedBar");
    if (!bar) return;

    const payload = adapterState.payload || fallbackSnapshot();
    const isReady = adapterState.status === "ready";
    const chipClass = isReady ? "green" : adapterState.status && adapterState.status.includes("fallback") ? "gold" : "red";

    bar.querySelector(".ob-engine-feed-title").textContent = "Engine Feed Adapter · " + safeText(adapterState.status, "unknown");
    bar.querySelector(".ob-engine-feed-subtitle").textContent =
      `${safeText(payload.market_health && payload.market_health.label, "Unknown")} · ${safeText(payload.market_health && payload.market_health.breadth, "No breadth")} · ${adapterState.fallbackActive ? "safe fallback active" : "snapshot active"}`;

    const sourceChip = bar.querySelector("[data-engine-feed-source-chip]");
    if (sourceChip) {
      sourceChip.className = "ob-engine-feed-chip " + chipClass;
      sourceChip.textContent = adapterState.fallbackActive ? "fallback" : "snapshot";
    }
  }

  function buildEngineBar() {
    if (document.getElementById("obEngineFeedBar")) return;

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const bar = document.createElement("div");
    bar.className = "ob-engine-feed-bar";
    bar.id = "obEngineFeedBar";

    bar.innerHTML = `
      <div class="ob-engine-feed-main">
        <div class="ob-engine-feed-title">Engine Feed Adapter · booting</div>
        <div class="ob-engine-feed-subtitle">Read-only snapshot bridge preparing safe fallback.</div>
      </div>

      <div class="ob-engine-feed-actions">
        <span class="ob-engine-feed-chip gold" data-engine-feed-source-chip>loading</span>
        <span class="ob-engine-feed-chip red">No broker API</span>
        <span class="ob-engine-feed-chip red">No auto execution</span>
        <button class="ob-engine-feed-chip clickable" id="obEngineFeedOpen">Engine Feed</button>
      </div>
    `;

    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    if (dataBar && dataBar.parentNode) {
      dataBar.insertAdjacentElement("afterend", bar);
    } else if (missionBar && missionBar.parentNode) {
      missionBar.insertAdjacentElement("afterend", bar);
    } else if (routeBar && routeBar.parentNode) {
      routeBar.insertAdjacentElement("afterend", bar);
    } else {
      layer.prepend(bar);
    }

    document.getElementById("obEngineFeedOpen").addEventListener("click", openEngineDrawer);
  }

  function boot() {
    exposeServerData(fallbackSnapshot());

    setTimeout(function () {
      buildEngineBar();
      updateEngineBar();
      fetchEngineSnapshot();
    }, 230);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_ENGINE_FEED_ADAPTER_V25 = {
    version: ADAPTER_VERSION,
    endpoint: ENDPOINT,
    getState: function () {
      return adapterState;
    },
    fallbackSnapshot,
    normalizePayload,
    exposeServerData,
    fetchEngineSnapshot,
    openEngineDrawer
  };
})();
