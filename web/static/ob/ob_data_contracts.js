
// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_JS
// OBDATA004_CANONICAL_ROOM_DATA_CONTRACTS
//
// Compatibility API retained.
// Fake preview synthesis removed.
//
// Every room reads the SAME canonical web projection.

(function () {
  "use strict";

  const CONTRACT_VERSION =
    "OB_DATA_CONTRACTS_V22_OBDATA004_CANONICAL";


  const contractDefinitions = {
    dashboard: [
      "account_snapshot",
      "mission_account",
      "open_positions_preview",
      "market_health",
      "tower_state",
      "dashboard_focus",
      "notifications_preview",
    ],

    marketMap: [
      "sectors",
      "symbols",
      "signals",
      "watchlist",
      "open_positions",
      "candidates",
      "source",
      "as_of",
      "freshness",
    ],

    symbolPage: [
      "symbol_header",
      "star_state",
      "star_facts",
      "soulaana_read",
      "risk_permission",
      "movement_field",
      "trade_context",
      "source",
      "as_of",
      "freshness",
    ],

    tradeCenter: [
      "open_positions",
      "signals",
      "watchlist",
      "candidates",
      "manual_live_queue",
      "source",
      "as_of",
      "freshness",
    ],

    reviewCenter: [
      "performance",
      "trade_replay",
      "reports",
      "journal_receipts",
      "review_summary",
      "source",
      "as_of",
      "freshness",
    ],

    ownerConsole: [
      "monitoring",
      "analytics",
      "intelligence",
      "diagnostics",
      "security_audit",
      "preview_controls",
    ],
  };


  const requiredSymbolFields = [
    "symbol",
  ];


  function clone(value) {
    try {
      return JSON.parse(
        JSON.stringify(value)
      );
    } catch (error) {
      return value;
    }
  }


  function safeObject(value) {
    return (
      value
      &&
      typeof value === "object"
      &&
      !Array.isArray(value)
    )
      ? value
      : {};
  }


  function safeArray(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function emptyProjection() {
    return {
      projection_status:
        "unavailable",

      freshness:
        "unavailable",

      source:
        null,

      as_of:
        null,

      current_eligible:
        false,

      display_eligible:
        false,

      market_health:
        {},

      sectors:
        [],

      symbols:
        [],

      signals:
        [],

      watchlist:
        [],

      positions_preview:
        [],

      candidates_preview:
        [],

      manual_live_queue:
        [],

      review_summary:
        {},

      account_snapshot:
        null,

      warnings: [],
    };
  }


  function projectionApi() {
    return (
      window.OB_CANONICAL_WEB_PROJECTION_OBDATA003_API
      ||
      window.OB_ENGINE_FEED_ADAPTER_V25
      ||
      null
    );
  }


  function projection() {
    const api =
      projectionApi();


    if (
      api
      &&
      typeof api.getProjection === "function"
    ) {
      return api.getProjection();
    }


    const snapshot =
      window.OB_ENGINE_FEED_SNAPSHOT_V25;


    if (
      snapshot
      &&
      typeof snapshot === "object"
    ) {
      return clone(
        snapshot
      );
    }


    return emptyProjection();
  }


  function getServerData() {
    return projection();
  }


  // Compatibility API:
  // Preview market data is deliberately unavailable to live contracts.
  function getPreviewData() {
    return {};
  }


  function getDataMode() {
    return "canonical";
  }


  function setDataMode() {
    return false;
  }


  function dataSourceLabel() {
    const data =
      projection();


    const source =
      data.source
      ||
      "source unavailable";


    const asOf =
      data.as_of
      ||
      "as-of unavailable";


    return (
      String(
        data.freshness
        ||
        "unavailable"
      )
      +
      " · "
      +
      source
      +
      " · "
      +
      asOf
    );
  }


  function displayEligible() {
    return Boolean(
      projection().display_eligible
    );
  }


  function normalizeSymbol(
    symbolObj,
    sector
  ) {
    if (
      !symbolObj
      ||
      typeof symbolObj !== "object"
    ) {
      return null;
    }


    const raw =
      clone(
        symbolObj
      );


    const symbol =
      (
        raw.symbol
        ||
        raw.ticker
        ||
        ""
      )
      .toString()
      .trim()
      .toUpperCase();


    if (!symbol) {
      return null;
    }


    return {
      ...raw,

      symbol,

      company:
        raw.company
        ||
        raw.company_name
        ||
        raw.name
        ||
        null,

      sectorName:
        raw.sectorName
        ||
        raw.sector
        ||
        (
          sector
          &&
          (
            sector.name
            ||
            sector.sector
          )
        )
        ||
        null,

      constellationName:
        raw.constellationName
        ||
        (
          sector
          &&
          sector.constellationName
        )
        ||
        null,

      tier:
        raw.tier
        ??
        null,

      tradeType:
        raw.tradeType
        ??
        raw.trade_type
        ??
        null,

      position:
        raw.position
        ??
        raw.status
        ??
        null,

      permission:
        raw.permission
        ??
        null,

      risk:
        raw.risk
        ??
        null,

      starName:
        raw.starName
        ??
        null,

      role:
        raw.role
        ??
        null,

      why:
        raw.why
        ??
        raw.opinion
        ??
        null,

      fact:
        raw.fact
        ??
        null,

      raw,
    };
  }


  function normalizeSector(
    sector,
    index
  ) {
    if (
      !sector
      ||
      typeof sector !== "object"
    ) {
      return null;
    }


    const raw =
      clone(
        sector
      );


    const symbols =
      safeArray(
        raw.symbols
      )
      .map(
        item =>
          normalizeSymbol(
            item,
            raw
          )
      )
      .filter(
        Boolean
      );


    return {
      ...raw,

      name:
        raw.name
        ||
        raw.sector
        ||
        null,

      constellationName:
        raw.constellationName
        ||
        null,

      strength:
        raw.strength
        ??
        null,

      mood:
        raw.mood
        ??
        null,

      crowding:
        raw.crowding
        ??
        null,

      symbols,

      raw,
    };
  }


  function sourceSectors() {
    const data =
      projection();


    if (
      !data.display_eligible
    ) {
      return {
        source:
          data.source
          ||
          null,

        freshness:
          data.freshness
          ||
          "unavailable",

        sectors:
          [],
      };
    }


    return {
      source:
        data.source
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",

      sectors:
        safeArray(
          data.sectors
        )
        .map(
          normalizeSector
        )
        .filter(
          Boolean
        ),
    };
  }


  function allSymbols() {
    const data =
      projection();


    if (
      !data.display_eligible
    ) {
      return [];
    }


    const direct =
      safeArray(
        data.symbols
      )
      .map(
        item =>
          normalizeSymbol(
            item,
            null
          )
      )
      .filter(
        Boolean
      );


    if (
      direct.length
    ) {
      return direct;
    }


    return sourceSectors()
      .sectors
      .flatMap(
        sector =>
          sector.symbols.map(
            symbol => ({
              ...symbol,

              sector:
                sector,
            })
          )
      );
  }


  function findSymbol(symbol) {
    const wanted =
      String(
        symbol
        ||
        ""
      )
      .trim()
      .toUpperCase();


    if (!wanted) {
      return null;
    }


    return (
      allSymbols().find(
        item =>
          item.symbol === wanted
      )
      ||
      null
    );
  }


  function openPositions() {
    const data =
      projection();


    return (
      data.display_eligible
    )
      ? clone(
          safeArray(
            data.positions_preview
          )
        )
      : [];
  }


  function signals() {
    const data =
      projection();


    return (
      data.display_eligible
    )
      ? clone(
          safeArray(
            data.signals
          )
        )
      : [];
  }


  function candidates() {
    const data =
      projection();


    return (
      data.display_eligible
    )
      ? clone(
          safeArray(
            data.candidates_preview
          )
        )
      : [];
  }


  function watchlist() {
    const data =
      projection();


    return (
      data.display_eligible
    )
      ? clone(
          safeArray(
            data.watchlist
          )
        )
      : [];
  }


  function manualLiveQueue() {
    const data =
      projection();


    return (
      data.display_eligible
    )
      ? clone(
          safeArray(
            data.manual_live_queue
          )
        )
      : [];
  }


  function marketHealth() {
    const data =
      projection();


    return {
      ...clone(
        safeObject(
          data.market_health
        )
      ),

      source:
        data.source
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",

      as_of:
        data.as_of
        ||
        null,

      current:
        Boolean(
          data.current_eligible
        ),

      projection_status:
        data.projection_status
        ||
        "unavailable",

      caution:
        data.reason
        ||
        null,
    };
  }


  function dashboardContract() {
    const data =
      projection();


    return {
      account_snapshot:
        clone(
          data.account_snapshot
          ||
          null
        ),

      mission_account:
        (
          window.OB_MISSION_ACCOUNTS_V18
          &&
          window.OB_MISSION_ACCOUNTS_V18.getSelectedMission
        )
          ? window.OB_MISSION_ACCOUNTS_V18.getSelectedMission()
          : null,

      open_positions_preview:
        openPositions().slice(
          0,
          3
        ),

      market_health:
        marketHealth(),

      tower_state: {
        label:
          "Tower Protected · Live Auto Locked",

        can_execute:
          false,

        live_auto_locked:
          true,
      },

      // Never fabricate current alerts/focus.
      dashboard_focus:
        [],

      notifications_preview:
        [],

      source:
        data.source
        ||
        null,

      as_of:
        data.as_of
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",
    };
  }


  function marketMapContract() {
    const data =
      projection();


    const sectorPayload =
      sourceSectors();


    return {
      sectors:
        sectorPayload.sectors,

      symbols:
        allSymbols(),

      signals:
        signals(),

      watchlist:
        watchlist(),

      open_positions:
        openPositions(),

      candidates:
        candidates(),

      source:
        data.source
        ||
        null,

      as_of:
        data.as_of
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",

      current:
        Boolean(
          data.current_eligible
        ),
    };
  }


  function symbolPageContract(symbol) {
    const data =
      projection();


    const wanted =
      String(
        symbol
        ||
        ""
      )
      .trim()
      .toUpperCase();


    const found =
      findSymbol(
        wanted
      );


    const safeHeader =
      found
      ||
      (
        wanted
          ? {
              symbol:
                wanted,

              unavailable:
                true,
            }
          : null
      );


    return {
      symbol_header:
        safeHeader,

      star_state: {
        tier:
          found
          ? found.tier
          : null,

        color:
          null,

        pulse:
          null,

        aura:
          null,
      },

      star_facts:
        found,

      soulaana_read: {
        summary:
          found
            ? (
                found.why
                ||
                "A source-backed symbol record is available."
              )
            : (
                wanted
                  ? (
                      "The canonical projection does not currently provide "
                      +
                      wanted
                      +
                      "."
                    )
                  : "No symbol was supplied."
              ),

        caution:
          data.reason
          ||
          null,

        next:
          data.current_eligible
            ? "Read the source-backed fields before deciding what deserves attention."
            : "Do not treat this room as current until provenance/freshness is restored.",
      },

      risk_permission: {
        risk:
          found
          ? found.risk
          : null,

        permission:
          found
          ? found.permission
          : null,

        tower:
          "Live Auto Locked",
      },

      movement_field: {
        phase:
          null,

        source:
          data.source
          ||
          null,

        as_of:
          data.as_of
          ||
          null,

        freshness:
          data.freshness
          ||
          "unavailable",
      },

      trade_context: {
        status:
          null,

        blocker:
          "No automatic execution. Live Auto Locked.",
      },

      source:
        data.source
        ||
        null,

      as_of:
        data.as_of
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",
    };
  }


  function tradeCenterContract() {
    const data =
      projection();


    return {
      open_positions:
        openPositions(),

      signals:
        signals(),

      watchlist:
        watchlist(),

      candidates:
        candidates(),

      manual_live_queue:
        manualLiveQueue(),

      source:
        data.source
        ||
        null,

      as_of:
        data.as_of
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",

      current:
        Boolean(
          data.current_eligible
        ),
    };
  }


  function reviewCenterContract() {
    const data =
      projection();


    return {
      // These remain empty unless a verified source explicitly projects them.
      performance:
        [],

      trade_replay:
        [],

      reports:
        [],

      journal_receipts:
        [],

      proof_demo_private:
        [],

      quarantined_rows:
        [],

      review_summary:
        data.display_eligible
          ? clone(
              safeObject(
                data.review_summary
              )
            )
          : {},

      source:
        data.source
        ||
        null,

      as_of:
        data.as_of
        ||
        null,

      freshness:
        data.freshness
        ||
        "unavailable",
    };
  }


  function ownerConsoleContract() {
    const data =
      projection();


    return {
      monitoring: {
        source:
          data.source
          ||
          null,

        freshness:
          data.freshness
          ||
          "unavailable",

        as_of:
          data.as_of
          ||
          null,

        projection_status:
          data.projection_status
          ||
          "unavailable",

        current_eligible:
          Boolean(
            data.current_eligible
          ),
      },

      analytics: {
        enabled:
          false,

        note:
          "No source-backed Owner Console analytics are projected yet.",
      },

      intelligence: {
        enabled:
          false,

        note:
          "No source-backed owner intelligence is fabricated here.",
      },

      diagnostics: {
        required_symbol_fields:
          requiredSymbolFields,

        source:
          data.source
          ||
          null,

        freshness:
          data.freshness
          ||
          "unavailable",

        reason:
          data.reason
          ||
          null,
      },

      security_audit: {
        tower_boundary:
          "Tower owns identity, access, clearance, permissions, and locks.",

        live_auto_locked:
          true,

        broker_api_enabled:
          false,

        capital_movement_enabled:
          false,
      },

      preview_controls: {
        fallback_enabled:
          false,

        demo_live_path_enabled:
          false,
      },
    };
  }


  function getRoomContract(
    room,
    args
  ) {
    if (
      room === "dashboard"
    ) {
      return dashboardContract();
    }


    if (
      room === "marketMap"
    ) {
      return marketMapContract();
    }


    if (
      room === "symbolPage"
    ) {
      return symbolPageContract(
        args
        &&
        args.symbol
      );
    }


    if (
      room === "tradeCenter"
    ) {
      return tradeCenterContract();
    }


    if (
      room === "reviewCenter"
    ) {
      return reviewCenterContract();
    }


    if (
      room === "ownerConsole"
    ) {
      return ownerConsoleContract();
    }


    return {
      error:
        "Unknown room contract",

      room,
    };
  }


  // Compatibility API retained.
  // It no longer patches preview/demo sectors into live OB_MARKET_DATA.
  function patchPreviewData() {
    return false;
  }


  function closeDrawer() {
    const existing =
      document.getElementById(
        "obDataDrawerBackdrop"
      );


    if (existing) {
      existing.remove();
    }
  }


  function openDataDrawer() {
    closeDrawer();


    const data =
      projection();


    const backdrop =
      document.createElement(
        "div"
      );


    backdrop.id =
      "obDataDrawerBackdrop";

    backdrop.className =
      "ob-data-drawer-backdrop open";


    const drawer =
      document.createElement(
        "div"
      );


    drawer.className =
      "ob-data-drawer";


    drawer.innerHTML = `
      <div class="ob-data-drawer-head">
        <div>
          <strong>
            Canonical OB Room Contracts
          </strong>

          <span>
            One projection. No preview synthesis.
          </span>
        </div>

        <button
          class="ob-data-close"
          id="obDataClose"
        >
          ×
        </button>
      </div>

      <div class="ob-data-contract-grid">
        <div class="ob-data-contract-card">
          <span>Mode</span>
          <strong>canonical</strong>
        </div>

        <div class="ob-data-contract-card">
          <span>Freshness</span>
          <strong>${data.freshness || "unavailable"}</strong>
        </div>

        <div class="ob-data-contract-card">
          <span>Source</span>
          <strong>${data.source || "not identified"}</strong>
        </div>

        <div class="ob-data-contract-card">
          <span>As of</span>
          <strong>${data.as_of || "not identified"}</strong>
        </div>
      </div>

      <div class="ob-data-contract-list">
        <div class="ob-data-contract-item">
          <div class="ob-data-contract-dot">1</div>

          <div class="ob-data-contract-copy">
            <strong>Current eligible</strong>

            <span>
              ${data.current_eligible ? "yes" : "no"}
            </span>
          </div>
        </div>

        <div class="ob-data-contract-item">
          <div class="ob-data-contract-dot">2</div>

          <div class="ob-data-contract-copy">
            <strong>Preview fallback</strong>

            <span>
              disabled
            </span>
          </div>
        </div>

        <div class="ob-data-contract-item">
          <div class="ob-data-contract-dot">3</div>

          <div class="ob-data-contract-copy">
            <strong>Reason</strong>

            <span>
              ${data.reason || "No reason supplied."}
            </span>
          </div>
        </div>
      </div>
    `;


    backdrop.appendChild(
      drawer
    );


    document.body.appendChild(
      backdrop
    );


    const close =
      document.getElementById(
        "obDataClose"
      );


    if (close) {
      close.addEventListener(
        "click",
        closeDrawer
      );
    }


    backdrop.addEventListener(
      "click",
      function (event) {
        if (
          event.target === backdrop
        ) {
          closeDrawer();
        }
      }
    );
  }


  const API = {
    version:
      CONTRACT_VERSION,

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

    marketHealth,

    manualLiveQueue,

    dashboardContract,

    marketMapContract,

    symbolPageContract,

    tradeCenterContract,

    reviewCenterContract,

    ownerConsoleContract,

    getRoomContract,

    patchPreviewData,

    openDataDrawer,

    preview_fallback_enabled:
      false,

    synthetic_market_state_enabled:
      false,

    safety: {
      read_only:
        true,

      broker_api_enabled:
        false,

      order_submission_enabled:
        false,

      capital_movement_enabled:
        false,

      auto_execution_enabled:
        false,

      live_auto_locked:
        true,

      gp066_advanced:
        false,
    },
  };


  window.OB_DATA_CONTRACTS_V22 =
    API;


  window.OB_CANONICAL_ROOM_CONTRACTS_OBDATA004_API =
    API;
})();
