// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_JS

(function () {
  const CONTRACT_VERSION = "OB_DATA_CONTRACTS_V22";
  const DATA_SOURCE_KEY = "ob.v22.dataSourceMode";

  const contractDefinitions = {
    dashboard: [
      "account_snapshot",
      "mission_account",
      "open_positions_preview",
      "market_health",
      "tower_state",
      "dashboard_focus",
      "notifications_preview"
    ],
    marketMap: [
      "sectors",
      "symbols",
      "signals",
      "watchlist",
      "open_positions",
      "candidates",
      "sector_drawers"
    ],
    symbolPage: [
      "symbol_header",
      "star_state",
      "star_facts",
      "soulaana_read",
      "risk_permission",
      "movement_field",
      "trade_context"
    ],
    tradeCenter: [
      "open_positions",
      "signals",
      "watchlist",
      "candidates",
      "manual_live_queue",
      "selected_detail",
      "receipts"
    ],
    reviewCenter: [
      "performance",
      "trade_replay",
      "reports",
      "journal_receipts",
      "proof_demo_private",
      "quarantined_rows"
    ],
    ownerConsole: [
      "monitoring",
      "analytics",
      "intelligence",
      "diagnostics",
      "security_audit",
      "preview_controls"
    ]
  };

  const requiredSymbolFields = [
    "symbol",
    "company",
    "tier",
    "tradeType",
    "position",
    "permission",
    "risk",
    "starName",
    "role",
    "why",
    "fact"
  ];

  function clone(value) {
    try {
      return JSON.parse(JSON.stringify(value));
    } catch (error) {
      return value;
    }
  }

  function compact(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return value;
  }

  function getServerData() {
    return window.OB_SERVER_DATA || window.OB_ENGINE_DATA || window.OB_ROOM_DATA || {};
  }

  function getPreviewData() {
    return window.OB_MARKET_DATA || {};
  }

  function getDataMode() {
    return localStorage.getItem(DATA_SOURCE_KEY) || "auto";
  }

  function setDataMode(mode) {
    localStorage.setItem(DATA_SOURCE_KEY, mode);
    window.location.reload();
  }

  function dataSourceLabel() {
    const server = getServerData();
    const hasServer = !!(server && Object.keys(server).length);
    const mode = getDataMode();

    if (mode === "preview") return "Preview fallback";
    if (mode === "server") return hasServer ? "Server / engine data" : "Server requested, fallback active";
    if (hasServer) return "Auto · server/engine data";
    return "Auto · preview fallback";
  }

  function normalizeSymbol(symbolObj, sector) {
    const symbol = compact(symbolObj.symbol, "UNKNOWN");
    const company = compact(symbolObj.company, symbol);
    const tier = compact(symbolObj.tier, "background");

    return {
      symbol: String(symbol).toUpperCase(),
      company,
      sectorName: compact(sector && sector.name, compact(symbolObj.sectorName, "Unknown Sector")),
      constellationName: compact(sector && sector.constellationName, compact(symbolObj.constellationName, "Unknown Constellation")),
      tier,
      tradeType: compact(symbolObj.tradeType, tier === "background" ? "Watch only" : "Option-first review"),
      position: compact(symbolObj.position, tier === "hot" ? "Candidate watch" : "Watch"),
      permission: compact(symbolObj.permission, tier === "background" ? "Watch Only" : "Paper Allowed · Live Locked"),
      risk: compact(symbolObj.risk, tier === "hot" ? "Moderate" : tier === "watch" ? "Guarded" : "Low priority"),
      starName: compact(symbolObj.starName, String(symbol).toUpperCase() + " Star"),
      role: compact(symbolObj.role, tier === "hot" ? "Momentum Leader" : "Market watch"),
      why: compact(symbolObj.why, "OB is tracking this symbol as part of its constellation context."),
      fact: compact(symbolObj.fact, "This star is part of OB's private market sky."),
      raw: symbolObj
    };
  }

  function normalizeSector(sector, index) {
    const name = compact(sector.name, "Sector " + (index + 1));
    const symbols = Array.isArray(sector.symbols) ? sector.symbols : [];

    return {
      name,
      constellationName: compact(sector.constellationName, name + " Constellation"),
      strength: compact(sector.strength, "Unknown"),
      mood: compact(sector.mood, "Guarded"),
      crowding: compact(sector.crowding, "Unknown"),
      symbols: symbols.map(symbolObj => normalizeSymbol(symbolObj, sector)),
      raw: sector
    };
  }

  function sourceSectors() {
    const mode = getDataMode();
    const server = getServerData();
    const preview = getPreviewData();

    const serverSectors =
      server.sectors ||
      (server.market_map && server.market_map.sectors) ||
      (server.marketMap && server.marketMap.sectors);

    if (mode !== "preview" && Array.isArray(serverSectors) && serverSectors.length) {
      return { source: "server", sectors: serverSectors.map(normalizeSector) };
    }

    if (Array.isArray(preview.sectors) && preview.sectors.length) {
      return { source: "preview", sectors: preview.sectors.map(normalizeSector) };
    }

    return {
      source: "fallback",
      sectors: [
        normalizeSector({
          name: "Fallback Sector",
          constellationName: "Fallback Constellation",
          strength: "Preview",
          symbols: [
            {
              symbol: "MU",
              company: "Micron Technology",
              tier: "hot",
              tradeType: "Option-first review",
              position: "Candidate watch",
              permission: "Paper Allowed · Live Locked",
              risk: "Moderate",
              starName: "Aster Memory",
              role: "Momentum Leader"
            }
          ]
        }, 0)
      ]
    };
  }

  function allSymbols() {
    return sourceSectors().sectors.flatMap(sector => sector.symbols.map(symbol => ({ ...symbol, sector })));
  }

  function findSymbol(symbol) {
    const wanted = String(symbol || "MU").toUpperCase();
    return allSymbols().find(item => item.symbol === wanted) || allSymbols()[0];
  }

  function openPositions() {
    return allSymbols()
      .filter(item => String(item.position || "").toLowerCase().includes("open") || ["MU", "AMD", "INTC"].includes(item.symbol))
      .slice(0, 8);
  }

  function signals() {
    return allSymbols().filter(item => item.tier === "hot" || item.tier === "watch").slice(0, 12);
  }

  function candidates() {
    return allSymbols().filter(item => item.tier === "hot").slice(0, 8);
  }

  function watchlist() {
    return allSymbols().filter(item => item.tier === "watch" || String(item.position || "").toLowerCase().includes("watch")).slice(0, 10);
  }

  function marketHealth() {
    const symbols = allSymbols();
    const hot = symbols.filter(item => item.tier === "hot").length;
    const watch = symbols.filter(item => item.tier === "watch").length;
    const background = symbols.filter(item => item.tier === "background").length;
    const source = sourceSectors().source;

    return {
      score: hot >= 3 ? 82 : hot >= 1 ? 72 : 58,
      label: hot >= 3 ? "Healthy but guarded" : hot >= 1 ? "Selective" : "Quiet / guarded",
      breadth: `${hot} hot · ${watch} watch · ${background} background`,
      regime: hot >= 1 ? "Risk-on pockets" : "No broad leadership",
      caution: source === "preview" || source === "fallback"
        ? "Preview fallback data is active. Real engine wiring is not complete."
        : "Engine data is active. Validate freshness and Tower permission before action.",
      source
    };
  }

  function manualLiveQueue() {
    return candidates().slice(0, 5).map((item, index) => ({
      ...item,
      manualStatus: index === 0 ? "Needs owner review" : "Waiting",
      blocker: "Live Automated locked. Manual placement only.",
      contract: item.symbol + " next monthly call"
    }));
  }

  function dashboardContract() {
    return {
      account_snapshot: {
        current_account: "Mission account selected in V18",
        mode: "Paper / Manual guarded",
        tower_state: "Clear · Live Auto Locked",
        data_source: dataSourceLabel()
      },
      mission_account: window.OB_MISSION_ACCOUNTS_V18 && window.OB_MISSION_ACCOUNTS_V18.getSelectedMission
        ? window.OB_MISSION_ACCOUNTS_V18.getSelectedMission()
        : null,
      open_positions_preview: openPositions().slice(0, 3),
      market_health: marketHealth(),
      tower_state: {
        label: "Tower Clear · Live Auto Locked",
        can_execute: false,
        manual_live_level: 1
      },
      dashboard_focus: [
        "Review active risk",
        "Inspect Market Map",
        "Use Manual Live Level 1 only"
      ],
      notifications_preview: [
        "Manual Live candidate ready",
        "Sector crowding watch",
        "Review receipt pending"
      ]
    };
  }

  function marketMapContract() {
    const sectorPayload = sourceSectors();
    return {
      sectors: sectorPayload.sectors,
      symbols: allSymbols(),
      signals: signals(),
      watchlist: watchlist(),
      open_positions: openPositions(),
      candidates: candidates(),
      source: sectorPayload.source
    };
  }

  function symbolPageContract(symbol) {
    const found = findSymbol(symbol);
    return {
      symbol_header: found,
      star_state: {
        tier: found.tier,
        color: found.tier === "hot" ? "green_gold" : found.tier === "watch" ? "gold_aqua" : "blue_gray",
        pulse: found.tier === "hot" ? "steady" : "slow",
        aura: found.position && String(found.position).toLowerCase().includes("open") ? "protected" : "watch"
      },
      star_facts: found,
      soulaana_read: {
        summary: found.why,
        caution: found.risk,
        next: "Review permission, movement, and mission account before action."
      },
      risk_permission: {
        risk: found.risk,
        permission: found.permission,
        tower: "Live Automated locked. Manual review only."
      },
      movement_field: {
        phase: found.tier === "hot" ? "Brightening" : found.tier === "watch" ? "Forming" : "Quiet",
        source: dataSourceLabel()
      },
      trade_context: {
        status: found.tier === "hot" ? "Needs owner review" : "Watch only",
        blocker: "Live Automated locked."
      }
    };
  }

  function tradeCenterContract() {
    return {
      open_positions: openPositions(),
      signals: signals(),
      watchlist: watchlist(),
      candidates: candidates(),
      manual_live_queue: manualLiveQueue(),
      data_source: dataSourceLabel()
    };
  }

  function reviewCenterContract() {
    const manualReceipts = window.OB_MANUAL_LIVE_V19 && window.OB_MANUAL_LIVE_V19.loadReceipts
      ? window.OB_MANUAL_LIVE_V19.loadReceipts()
      : [];

    return {
      performance: [],
      trade_replay: [],
      reports: [],
      journal_receipts: manualReceipts,
      proof_demo_private: [],
      quarantined_rows: [],
      data_source: dataSourceLabel()
    };
  }

  function ownerConsoleContract() {
    return {
      monitoring: {
        rooms: 6,
        source: dataSourceLabel(),
        contracts: Object.keys(contractDefinitions).length
      },
      analytics: {
        enabled: false,
        note: "Analytics wiring later."
      },
      intelligence: {
        enabled: false,
        note: "Strategy degradation and regime intelligence wiring later."
      },
      diagnostics: {
        required_symbol_fields: requiredSymbolFields,
        source: sourceSectors().source
      },
      security_audit: {
        tower_boundary: "Tower owns identity, access, billing, clearance, permissions, locks."
      },
      preview_controls: {
        fallback_enabled: true,
        server_data_supported: true
      }
    };
  }

  function getRoomContract(room, args) {
    if (room === "dashboard") return dashboardContract();
    if (room === "marketMap") return marketMapContract();
    if (room === "symbolPage") return symbolPageContract(args && args.symbol);
    if (room === "tradeCenter") return tradeCenterContract();
    if (room === "reviewCenter") return reviewCenterContract();
    if (room === "ownerConsole") return ownerConsoleContract();
    return {
      error: "Unknown room contract",
      room
    };
  }

  function patchPreviewData() {
    const sectors = sourceSectors().sectors.map(sector => ({
      ...sector.raw,
      name: sector.name,
      constellationName: sector.constellationName,
      strength: sector.strength,
      mood: sector.mood,
      crowding: sector.crowding,
      symbols: sector.symbols.map(symbol => ({
        ...symbol.raw,
        ...symbol
      }))
    }));

    window.OB_MARKET_DATA = window.OB_MARKET_DATA || {};
    window.OB_MARKET_DATA.sectors = sectors;
  }

  function closeDrawer() {
    const existing = document.getElementById("obDataDrawerBackdrop");
    if (existing) existing.remove();
  }

  function contractItem(title, detail, index) {
    return `
      <div class="ob-data-contract-item">
        <div class="ob-data-contract-dot">${index + 1}</div>
        <div class="ob-data-contract-copy">
          <strong>${title}</strong>
          <span>${detail}</span>
        </div>
      </div>
    `;
  }

  function openDataDrawer() {
    closeDrawer();

    const health = marketHealth();
    const source = sourceSectors();
    const serverKeys = Object.keys(getServerData() || {});
    const previewKeys = Object.keys(getPreviewData() || {});

    const backdrop = document.createElement("div");
    backdrop.id = "obDataDrawerBackdrop";
    backdrop.className = "ob-data-drawer-backdrop open";

    const drawer = document.createElement("div");
    drawer.className = "ob-data-drawer";

    drawer.innerHTML = `
      <div class="ob-data-drawer-head">
        <div>
          <strong>OB Data Contracts</strong>
          <span>V22 bridge layer for real engine/server data with safe preview fallback.</span>
        </div>
        <button class="ob-data-close" id="obDataClose">×</button>
      </div>

      <div class="ob-data-contract-grid">
        <div class="ob-data-contract-card"><span>Source mode</span><strong>${getDataMode()}</strong></div>
        <div class="ob-data-contract-card"><span>Active source</span><strong>${dataSourceLabel()}</strong></div>
        <div class="ob-data-contract-card"><span>Sector count</span><strong>${source.sectors.length}</strong></div>
        <div class="ob-data-contract-card"><span>Symbol count</span><strong>${allSymbols().length}</strong></div>
        <div class="ob-data-contract-card"><span>Signals</span><strong>${signals().length}</strong></div>
        <div class="ob-data-contract-card"><span>Candidates</span><strong>${candidates().length}</strong></div>
      </div>

      <div class="ob-data-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        This is the bridge, not the engine itself. If real data is missing, OB must say fallback is active instead of pretending the feed is live.
      </div>

      <div class="ob-data-warning">
        <strong>Tower boundary:</strong><br>
        Data can inform review. It cannot bypass Tower permission, Live Auto locks, Manual Live Level 1, or mission account rules.
      </div>

      <div class="ob-data-contract-list">
        ${Object.entries(contractDefinitions).map(([room, fields], index) => contractItem(
          room,
          fields.join(" · "),
          index
        )).join("")}
      </div>

      <div class="ob-data-note">
        <strong>Server keys:</strong> ${serverKeys.length ? serverKeys.join(", ") : "none detected"}<br>
        <strong>Preview keys:</strong> ${previewKeys.length ? previewKeys.join(", ") : "none detected"}<br>
        <strong>Market health:</strong> ${health.label} · ${health.breadth}
      </div>

      <div class="ob-data-status-actions" style="margin-top: 12px; justify-content: flex-start;">
        <button class="ob-data-chip clickable" data-ob-data-mode="auto">Auto</button>
        <button class="ob-data-chip clickable" data-ob-data-mode="preview">Preview fallback</button>
        <button class="ob-data-chip clickable" data-ob-data-mode="server">Prefer server</button>
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obDataClose").addEventListener("click", closeDrawer);

    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });

    drawer.querySelectorAll("[data-ob-data-mode]").forEach(button => {
      button.addEventListener("click", function () {
        setDataMode(this.getAttribute("data-ob-data-mode"));
      });
    });
  }

  function buildDataStatusBar() {
    if (document.getElementById("obDataStatusBar")) return;

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const health = marketHealth();
    const source = sourceSectors();

    const bar = document.createElement("div");
    bar.className = "ob-data-status-bar";
    bar.id = "obDataStatusBar";

    const chipClass = source.source === "server" ? "green" : source.source === "preview" ? "gold" : "red";

    bar.innerHTML = `
      <div class="ob-data-status-main">
        <div class="ob-data-status-title">Data Bridge · ${dataSourceLabel()}</div>
        <div class="ob-data-status-subtitle">
          ${health.label} · ${health.breadth} · Contracts ready for Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console.
        </div>
      </div>

      <div class="ob-data-status-actions">
        <span class="ob-data-chip ${chipClass}">${source.source}</span>
        <span class="ob-data-chip gold">Fallback safe</span>
        <span class="ob-data-chip red">Live Auto Locked</span>
        <button class="ob-data-chip clickable" id="obDataContractsOpen">Data Contracts</button>
      </div>
    `;

    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    if (missionBar && missionBar.parentNode) {
      missionBar.insertAdjacentElement("afterend", bar);
    } else if (routeBar && routeBar.parentNode) {
      routeBar.insertAdjacentElement("afterend", bar);
    } else {
      layer.prepend(bar);
    }

    document.getElementById("obDataContractsOpen").addEventListener("click", openDataDrawer);
  }

  function boot() {
    patchPreviewData();
    setTimeout(buildDataStatusBar, 160);
  }

  patchPreviewData();
  document.addEventListener("DOMContentLoaded", boot);

  window.OB_DATA_CONTRACTS_V22 = {
    version: CONTRACT_VERSION,
    contractDefinitions,
    requiredSymbolFields,
    getServerData,
    getPreviewData,
    getDataMode,
    setDataMode,
    dataSourceLabel,
    normalizeSymbol,
    normalizeSector,
    sourceSectors,
    allSymbols,
    findSymbol,
    openPositions,
    signals,
    candidates,
    watchlist,
    manualLiveQueue,
    marketHealth,
    getRoomContract,
    dashboardContract,
    marketMapContract,
    symbolPageContract,
    tradeCenterContract,
    reviewCenterContract,
    ownerConsoleContract,
    openDataDrawer
  };
})();
