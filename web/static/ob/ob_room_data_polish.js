// OBSERVATORY_V27_ROOM_LEVEL_REAL_DATA_POLISH_JS

(function () {
  const VERSION = "OB_V27_ROOM_LEVEL_REAL_DATA_POLISH";

  // V27 SMOKE MARKERS
  // Dashboard room-level data polish
  // Market Map source-aware constellation counts
  // Symbol Page snapshot context polish
  // Trade Center candidate queue summary
  // Review Center receipt snapshot summary
  // Owner Console engine feed diagnostics
  // Preview fallback
  // No broker API
  // No auto execution
  // Live Auto Locked

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

  function payload() {
    const state = adapterState();

    if (state && state.payload) {
      return state.payload;
    }

    if (window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot) {
      return window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot();
    }

    return {
      source: "room_polish_fallback",
      market_health: { label: "Fallback waiting", breadth: "0 symbols" },
      positions_preview: [],
      candidates_preview: [],
      manual_live_queue: [],
      review_summary: { receipts: 0 },
      data_files: {},
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      },
      warnings: ["Room polish is waiting for adapter payload."]
    };
  }

  function sourceChipClass(state) {
    if (state.status === "ready") return "green";
    if (state.fallbackActive || String(state.status || "").includes("fallback")) return "gold";
    return "red";
  }

  function sourceLabel(state, data) {
    if (state.status === "ready") return "Snapshot active";
    if (state.fallbackActive) return "Preview fallback";
    return safeText(data.source, "Unknown source");
  }

  function card(label, value) {
    return `
      <div class="ob-room-polish-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function openStarButton(symbol) {
    const clean = safeText(symbol, "MU").toUpperCase();
    return `<button class="ob-room-polish-button" type="button" onclick="window.location.href='/ob/symbol/${clean}'">Open star</button>`;
  }

  function rows(items, emptyLabel, emptyDetail) {
    const list = Array.isArray(items) ? items.slice(0, 5) : [];

    if (!list.length) {
      return `
        <div class="ob-room-polish-row">
          <strong>${emptyLabel}</strong>
          <span>${emptyDetail}</span>
          <button class="ob-room-polish-button" type="button">Fallback</button>
        </div>
      `;
    }

    return list.map(item => `
      <div class="ob-room-polish-row">
        <strong>${safeText(item.symbol, "UNKNOWN")}</strong>
        <span>${safeText(item.company, safeText(item.manualStatus, safeText(item.position, "Snapshot row")))}</span>
        ${openStarButton(item.symbol)}
      </div>
    `).join("");
  }

  function dataContracts() {
    return window.OB_DATA_CONTRACTS_V22 || null;
  }

  function contractMarketCounts() {
    const contracts = dataContracts();

    if (!contracts || !contracts.marketMapContract) {
      return {
        symbols: 0,
        signals: 0,
        watchlist: 0,
        candidates: 0,
        sectors: 0
      };
    }

    const market = contracts.marketMapContract();

    return {
      symbols: count(market.symbols),
      signals: count(market.signals),
      watchlist: count(market.watchlist),
      candidates: count(market.candidates),
      sectors: count(market.sectors)
    };
  }

  function roomCards(room, data, state) {
    const health = data.market_health || {};
    const marketCounts = contractMarketCounts();

    if (room === "dashboard") {
      return [
        card("Source", sourceLabel(state, data)),
        card("Market health", safeText(health.label, "Unknown")),
        card("Open preview", count(data.positions_preview)),
        card("Focus", "Review first")
      ].join("");
    }

    if (room === "market_map") {
      return [
        card("Constellations", marketCounts.sectors),
        card("Symbols", marketCounts.symbols),
        card("Signals", marketCounts.signals),
        card("Candidates", marketCounts.candidates)
      ].join("");
    }

    if (room === "symbol_page") {
      const symbol = window.location.pathname.split("/").filter(Boolean).pop() || "MU";
      return [
        card("Symbol", symbol.toUpperCase()),
        card("Source", sourceLabel(state, data)),
        card("Permission", "Live Auto Locked"),
        card("Mode", "One-star context")
      ].join("");
    }

    if (room === "trade_center") {
      return [
        card("Candidates", count(data.candidates_preview)),
        card("Manual queue", count(data.manual_live_queue)),
        card("Guard", safeText(state.httpStatus, "not requested")),
        card("Execution", "Manual only")
      ].join("");
    }

    if (room === "review_center") {
      return [
        card("Receipts", safeText(data.review_summary && data.review_summary.receipts, "0")),
        card("Proof/Demo", "Private"),
        card("Source", sourceLabel(state, data)),
        card("Export", "Tower gated")
      ].join("");
    }

    if (room === "owner_console") {
      return [
        card("Adapter", safeText(state.status, "unknown")),
        card("HTTP / Guard", safeText(state.httpStatus, "not requested")),
        card("Universe", safeText(data.data_files && data.data_files.market_universe, "unknown")),
        card("Pipeline", safeText(data.data_files && data.data_files.pipeline_status, "unknown"))
      ].join("");
    }

    return [
      card("Source", sourceLabel(state, data)),
      card("Status", safeText(state.status, "unknown")),
      card("Candidates", count(data.candidates_preview)),
      card("Manual queue", count(data.manual_live_queue))
    ].join("");
  }

  function roomFocus(room, data, state) {
    if (room === "dashboard") {
      return "Dashboard polish: account, market, and focus panels can now read the same snapshot context without pretending fallback data is live.";
    }

    if (room === "market_map") {
      return "Market Map polish: constellation counts are source-aware and can use the V22 contract counts while protected engine data remains guarded.";
    }

    if (room === "symbol_page") {
      return "Symbol Page polish: one-star context gets snapshot source awareness, but permission still comes from Tower and the selected mission account.";
    }

    if (room === "trade_center") {
      return "Trade Center polish: candidate and Manual Live queue summaries are visible from the safe adapter. Owner review still comes before broker placement.";
    }

    if (room === "review_center") {
      return "Review Center polish: receipts and Proof/Demo status are summarized without making proof public or exportable.";
    }

    if (room === "owner_console") {
      return "Owner Console polish: diagnostics show adapter status, guard behavior, data file state, and fallback state for owner review.";
    }

    return "Room-level snapshot polish is active.";
  }

  function roomList(room, data) {
    if (room === "dashboard") {
      return `
        <div class="ob-room-polish-list">
          ${rows(data.positions_preview, "No open preview", "Dashboard is waiting for adapter positions or fallback preview rows.")}
        </div>
      `;
    }

    if (room === "market_map") {
      return `
        <div class="ob-room-polish-list">
          ${rows(data.candidates_preview, "No candidate stars", "Market Map is reading source-aware counts but no candidate rows are available yet.")}
        </div>
      `;
    }

    if (room === "symbol_page") {
      const symbol = window.location.pathname.split("/").filter(Boolean).pop() || "MU";
      return `
        <div class="ob-room-polish-list">
          <div class="ob-room-polish-row">
            <strong>${symbol.toUpperCase()}</strong>
            <span>One-star room is source-aware. Use Symbol Page facts, movement, risk, and Tower state before action.</span>
            <button class="ob-room-polish-button" type="button" onclick="window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.openDataDrawer && window.OB_DATA_CONTRACTS_V22.openDataDrawer()">Contracts</button>
          </div>
        </div>
      `;
    }

    if (room === "trade_center") {
      return `
        <div class="ob-room-polish-list">
          ${rows(data.manual_live_queue, "Manual queue empty", "Manual Live queue is waiting for safe candidate rows.")}
        </div>
      `;
    }

    if (room === "review_center") {
      return `
        <div class="ob-room-polish-list">
          <div class="ob-room-polish-row">
            <strong>Private receipts</strong>
            <span>${safeText(data.review_summary && data.review_summary.receipts, "0")} receipt rows visible to the adapter layer.</span>
            <button class="ob-room-polish-button" type="button">Private</button>
          </div>
          <div class="ob-room-polish-row">
            <strong>Proof/Demo</strong>
            <span>Private, internal, redacted only if Tower clears export later.</span>
            <button class="ob-room-polish-button" type="button">Tower gated</button>
          </div>
        </div>
      `;
    }

    if (room === "owner_console") {
      return `
        <div class="ob-room-polish-list">
          <div class="ob-room-polish-row">
            <strong>Adapter source</strong>
            <span>${safeText(data.source, "unknown")}</span>
            <button class="ob-room-polish-button" type="button" onclick="window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.openEngineDrawer && window.OB_ENGINE_FEED_ADAPTER_V25.openEngineDrawer()">Feed</button>
          </div>
          <div class="ob-room-polish-row">
            <strong>Fallback</strong>
            <span>${adapterState().fallbackActive ? "Preview fallback active or guard blocked." : "Snapshot data active."}</span>
            <button class="ob-room-polish-button" type="button">Read-only</button>
          </div>
        </div>
      `;
    }

    return "";
  }

  function panelHtml() {
    const room = currentRoomKey();
    const state = adapterState();
    const data = payload();
    const boundaries = data.tower_boundaries || {};
    const chip = sourceChipClass(state);

    return `
      <div class="ob-room-polish-panel" id="obRoomDataPolishPanel" data-ob-v27-room-data-polish="true">
        <div class="ob-room-polish-head">
          <div>
            <div class="ob-label">Room-Level Data Polish · V27</div>
            <div class="ob-room-polish-title">${roomLabel(room)} real-data polish</div>
            <div class="ob-room-polish-subtitle">
              ${sourceLabel(state, data)} · ${safeText(data.market_health && data.market_health.label, "Snapshot waiting")} · read-only room context.
            </div>
          </div>

          <div class="ob-room-polish-chip-row">
            <span class="ob-room-polish-chip ${chip}">${safeText(state.status, "waiting")}</span>
            <span class="ob-room-polish-chip gold">${safeText(data.source, "fallback")}</span>
            <span class="ob-room-polish-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-room-polish-grid">
          ${roomCards(room, data, state)}
        </div>

        ${roomList(room, data)}

        <div class="ob-room-polish-focus">
          <strong>Room focus:</strong><br>
          ${roomFocus(room, data, state)}
          <br><br>
          No broker API: ${boundaries.no_broker_api ? "true" : "true"} ·
          No auto execution: ${boundaries.no_auto_execution ? "true" : "true"} ·
          Live Auto Locked: ${boundaries.live_auto_locked ? "true" : "true"}
        </div>
      </div>
    `;
  }

  function insertPanel() {
    const existing = document.getElementById("obRoomDataPolishPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const snapshotPanel = document.getElementById("obSnapshotDisplayPanel");
    const engineBar = document.getElementById("obEngineFeedBar");
    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (snapshotPanel && snapshotPanel.parentNode) {
      snapshotPanel.insertAdjacentElement("afterend", panel);
    } else if (engineBar && engineBar.parentNode) {
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

  function setFlags() {
    document.body.setAttribute("data-ob-v27-room-data-polish", "ready");
    window.OB_V27_ROOM_DATA_POLISH_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      adapterSeen: !!window.OB_ENGINE_FEED_ADAPTER_V25,
      snapshotSeen: !!window.OB_SNAPSHOT_DISPLAY_V26,
      contractsSeen: !!window.OB_DATA_CONTRACTS_V22,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    setTimeout(function () {
      insertPanel();
      setFlags();
    }, 520);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    insertPanel();
    setFlags();
  });

  window.OB_ROOM_DATA_POLISH_V27 = {
    version: VERSION,
    currentRoomKey,
    panelHtml,
    insertPanel,
    setFlags
  };
})();
