// OBSERVATORY_V26_REAL_SNAPSHOT_DISPLAY_WIRING_JS

(function () {
  const VERSION = "OB_V26_REAL_SNAPSHOT_DISPLAY_WIRING";

  function currentRoomKey() {
    const path = window.location.pathname.toLowerCase();

    if (path.includes("/symbol/")) return "symbol_page";
    if (path.includes("market-map")) return "market_map";
    if (path.includes("trade-center")) return "trade_center";
    if (path.includes("review-center")) return "review_center";
    if (path.includes("owner-console")) return "owner_console";
    return "dashboard";
  }

  function roomLabel(key) {
    return {
      dashboard: "Dashboard",
      market_map: "Market Map",
      symbol_page: "Symbol Page",
      trade_center: "Trade Center",
      review_center: "Review Center",
      owner_console: "Owner Console"
    }[key] || "OB Room";
  }

  function count(value) {
    return Array.isArray(value) ? value.length : 0;
  }

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function adapterState() {
    if (window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.getState) {
      return window.OB_ENGINE_FEED_ADAPTER_V25.getState();
    }

    return {
      status: "adapter unavailable",
      source: "fallback",
      fallbackActive: true,
      payload: null,
      httpStatus: null
    };
  }

  function snapshotPayload() {
    const state = adapterState();

    if (state && state.payload) {
      return state.payload;
    }

    if (window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot) {
      return window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot();
    }

    return {
      source: "local_display_fallback",
      market_health: { label: "Fallback waiting", breadth: "0 symbols" },
      positions_preview: [],
      candidates_preview: [],
      manual_live_queue: [],
      review_summary: { receipts: 0 },
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      },
      warnings: ["Snapshot display is waiting for the V25 adapter."]
    };
  }

  function chipClass(state) {
    if (state.status === "ready") return "green";
    if (state.fallbackActive || String(state.status || "").includes("fallback")) return "gold";
    return "red";
  }

  function sourceLabel(state, payload) {
    if (state.status === "ready") return "Snapshot active";
    if (state.fallbackActive) return "Preview fallback";
    return safeText(payload.source, "Unknown source");
  }

  function card(label, value) {
    return `
      <div class="ob-snapshot-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function symbolRows(items, emptyText) {
    const list = Array.isArray(items) ? items.slice(0, 5) : [];

    if (!list.length) {
      return `
        <div class="ob-snapshot-list-row">
          <strong>No rows yet</strong>
          <span>${emptyText}</span>
          <button class="ob-snapshot-button" type="button">Fallback</button>
        </div>
      `;
    }

    return list.map(item => `
      <div class="ob-snapshot-list-row">
        <strong>${safeText(item.symbol, "UNKNOWN")}</strong>
        <span>${safeText(item.company, safeText(item.position, "Snapshot row"))}</span>
        <button class="ob-snapshot-button" type="button" onclick="window.location.href='/ob/symbol/${safeText(item.symbol, "MU")}'">
          Open star
        </button>
      </div>
    `).join("");
  }

  function roomNote(room, payload, state) {
    if (room === "dashboard") {
      return "Dashboard now shows whether the account room is reading protected snapshot data or the V22 preview fallback.";
    }

    if (room === "market_map") {
      return "Market Map uses the adapter source to show whether the sky is powered by snapshot data or safe preview constellation data.";
    }

    if (room === "symbol_page") {
      return "Symbol Page stays one-star focused. Snapshot state is context only; it does not create permission.";
    }

    if (room === "trade_center") {
      return "Trade Center can see candidate and Manual Live queue counts from the safe adapter. Owner review is still required.";
    }

    if (room === "review_center") {
      return "Review Center can see receipt/review snapshot status while Proof/Demo remains private.";
    }

    if (room === "owner_console") {
      return "Owner Console can diagnose feed status, guard behavior, fallback state, and data file availability.";
    }

    return "Snapshot status is visible for this protected OB room.";
  }

  function roomSpecificList(room, payload) {
    if (room === "dashboard") {
      return `
        <div class="ob-snapshot-list">
          ${symbolRows(payload.positions_preview, "No open position preview from adapter yet.")}
        </div>
      `;
    }

    if (room === "market_map") {
      return `
        <div class="ob-snapshot-list">
          ${symbolRows(payload.candidates_preview, "No hot candidates from adapter yet.")}
        </div>
      `;
    }

    if (room === "symbol_page") {
      const symbol = window.location.pathname.split("/").filter(Boolean).pop() || "MU";
      return `
        <div class="ob-snapshot-list">
          <div class="ob-snapshot-list-row">
            <strong>${symbol.toUpperCase()}</strong>
            <span>Snapshot context active for this symbol room. Check Data Contracts for full star state.</span>
            <button class="ob-snapshot-button" type="button" onclick="window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.openDataDrawer && window.OB_DATA_CONTRACTS_V22.openDataDrawer()">Contracts</button>
          </div>
        </div>
      `;
    }

    if (room === "trade_center") {
      return `
        <div class="ob-snapshot-list">
          ${symbolRows(payload.manual_live_queue, "Manual Live queue is waiting for candidate data.")}
        </div>
      `;
    }

    if (room === "review_center") {
      return `
        <div class="ob-snapshot-list">
          <div class="ob-snapshot-list-row">
            <strong>Receipts</strong>
            <span>${safeText(payload.review_summary && payload.review_summary.receipts, "0")} Manual Live / review receipts detected by adapter.</span>
            <button class="ob-snapshot-button" type="button">Private</button>
          </div>
          <div class="ob-snapshot-list-row">
            <strong>Proof/Demo</strong>
            <span>Proof/Demo remains private and Tower export-gated.</span>
            <button class="ob-snapshot-button" type="button">Locked</button>
          </div>
        </div>
      `;
    }

    if (room === "owner_console") {
      return `
        <div class="ob-snapshot-list">
          <div class="ob-snapshot-list-row">
            <strong>market_universe</strong>
            <span>${safeText(payload.data_files && payload.data_files.market_universe, "unknown")}</span>
            <button class="ob-snapshot-button" type="button">Data</button>
          </div>
          <div class="ob-snapshot-list-row">
            <strong>pipeline_status</strong>
            <span>${safeText(payload.data_files && payload.data_files.pipeline_status, "unknown")}</span>
            <button class="ob-snapshot-button" type="button">Data</button>
          </div>
          <div class="ob-snapshot-list-row">
            <strong>Guard status</strong>
            <span>Engine route status: ${safeText(adapterState().httpStatus, "not requested")}</span>
            <button class="ob-snapshot-button" type="button">Guarded</button>
          </div>
        </div>
      `;
    }

    return "";
  }

  function snapshotPanelHtml() {
    const room = currentRoomKey();
    const state = adapterState();
    const payload = snapshotPayload();
    const health = payload.market_health || {};
    const boundaries = payload.tower_boundaries || {};

    return `
      <div class="ob-snapshot-panel" id="obSnapshotDisplayPanel" data-ob-v26-snapshot-display="true">
        <div class="ob-snapshot-head">
          <div>
            <div class="ob-label">Snapshot Display · V26</div>
            <div class="ob-snapshot-title">${roomLabel(room)} snapshot status</div>
            <div class="ob-snapshot-subtitle">
              ${safeText(health.label, "Snapshot waiting")} · ${safeText(health.breadth, "No breadth yet")} · ${sourceLabel(state, payload)}
            </div>
          </div>

          <div class="ob-snapshot-chip-row">
            <span class="ob-snapshot-chip ${chipClass(state)}">${safeText(state.status, "waiting")}</span>
            <span class="ob-snapshot-chip gold">${safeText(payload.source, "fallback")}</span>
            <span class="ob-snapshot-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-snapshot-grid">
          ${card("Data source", sourceLabel(state, payload))}
          ${card("HTTP / Guard", safeText(state.httpStatus, "not requested"))}
          ${card("Positions", count(payload.positions_preview))}
          ${card("Candidates", count(payload.candidates_preview))}
          ${card("Manual queue", count(payload.manual_live_queue))}
        </div>

        ${roomSpecificList(room, payload)}

        <div class="ob-snapshot-room-note">
          <strong>Room note:</strong><br>
          ${roomNote(room, payload, state)}
          <br><br>
          No broker API: ${boundaries.no_broker_api ? "true" : "unknown"} ·
          No auto execution: ${boundaries.no_auto_execution ? "true" : "unknown"} ·
          Live Auto Locked: ${boundaries.live_auto_locked ? "true" : "unknown"}
        </div>
      </div>
    `;
  }

  function insertPanel() {
    const existing = document.getElementById("obSnapshotDisplayPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const engineBar = document.getElementById("obEngineFeedBar");
    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = snapshotPanelHtml();
    const panel = wrapper.firstElementChild;

    if (engineBar && engineBar.parentNode) {
      engineBar.insertAdjacentElement("afterend", panel);
    } else if (dataBar && dataBar.parentNode) {
      dataBar.insertAdjacentElement("afterend", panel);
    } else if (missionBar && missionBar.parentNode) {
      missionBar.insertAdjacentElement("afterend", panel);
    } else if (routeBar && routeBar.parentNode) {
      routeBar.insertAdjacentElement("afterend", panel);
    } else {
      layer.prepend(panel);
    }
  }

  function addInlineFlags() {
    document.body.setAttribute("data-ob-v26-snapshot-display", "ready");
    window.OB_V26_SNAPSHOT_DISPLAY_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      adapterSeen: !!window.OB_ENGINE_FEED_ADAPTER_V25,
      contractsSeen: !!window.OB_DATA_CONTRACTS_V22,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    setTimeout(function () {
      insertPanel();
      addInlineFlags();
    }, 360);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    insertPanel();
    addInlineFlags();
  });

  window.OB_SNAPSHOT_DISPLAY_V26 = {
    version: VERSION,
    currentRoomKey,
    snapshotPayload,
    insertPanel,
    addInlineFlags
  };
})();

// OBSERVATORY_V26_REAL_SNAPSHOT_DISPLAY_WIRING_SMOKE_MARKERS
// Dashboard snapshot status
// Market Map snapshot status
// Symbol Page snapshot status
// Trade Center snapshot status
// Review Center snapshot status
// Owner Console snapshot status
// Preview fallback
// No broker API
// No auto execution
// Live Auto Locked

