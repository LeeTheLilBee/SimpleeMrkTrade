// OBSERVATORY_V35_ENGINE_FEED_CANONICAL_ROOM_MAPPING_JS

(function () {
  const VERSION = "OB_V35_ENGINE_FEED_CANONICAL_ROOM_MAPPING";
  const ENDPOINT = "/ob/engine-room-mapping.json";

  // V35 SMOKE MARKERS
  // Engine Feed Canonical Room Mapping
  // Dashboard account focus market state mapping
  // Market Map constellation source labels mapping
  // Symbol Page one-symbol engine context mapping
  // Trade Center candidate queue mapping
  // Review Center receipt ledger mapping
  // Owner Console diagnostics source audit mapping
  // trusted read-only engine feed
  // trust labels integrated
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let mappingState = {
    status: "booting",
    httpStatus: null,
    source: "waiting",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function count(value) {
    return Array.isArray(value) ? value.length : Number(value || 0);
  }

  function currentRoomKey() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes("/symbol/")) return "symbol_page";
    if (path.includes("market-map")) return "market_map";
    if (path.includes("trade-center")) return "trade_center";
    if (path.includes("review-center")) return "review_center";
    if (path.includes("owner-console")) return "owner_console";
    return "dashboard";
  }

  function roomLabel(room) {
    return {
      dashboard: "Dashboard",
      market_map: "Market Map",
      symbol_page: "Symbol Page",
      trade_center: "Trade Center",
      review_center: "Review Center",
      owner_console: "Owner Console"
    }[room] || "OB Room";
  }

  function expandedPayload() {
    if (window.OB_ENGINE_FEED_EXPANSION_V32 && window.OB_ENGINE_FEED_EXPANSION_V32.getState) {
      const state = window.OB_ENGINE_FEED_EXPANSION_V32.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_FEED_EXPANDED_V32) return window.OB_ENGINE_FEED_EXPANDED_V32;

    return {
      source: "v35_expanded_fallback",
      counts: {},
      previews: {
        candidates: [],
        open_positions: [],
        ledger: [],
        trade_log: [],
        market_symbols: []
      },
      data_files: {}
    };
  }

  function trustPayload() {
    if (window.OB_ENGINE_TRUST_LABELS_V34_API && window.OB_ENGINE_TRUST_LABELS_V34_API.getState) {
      const state = window.OB_ENGINE_TRUST_LABELS_V34_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_TRUST_LABELS_V34) return window.OB_ENGINE_TRUST_LABELS_V34;

    return {
      trust: {
        level: "fallback",
        label: "Fallback / guarded",
        safeToDisplay: "fallback_only"
      },
      freshness_score: 72,
      display_label: "Fallback / guarded"
    };
  }

  function diagnosticsPayload() {
    if (window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API && window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API.getState) {
      const state = window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_FEED_DIAGNOSTICS_V33) return window.OB_ENGINE_FEED_DIAGNOSTICS_V33;

    return {
      display_label: "Fallback / guarded",
      freshness_score: 72,
      files: [],
      summary: {}
    };
  }

  function normalizeSymbol(row) {
    if (!row || typeof row !== "object") {
      return {
        symbol: "UNKNOWN",
        company: "Unknown",
        source: "fallback"
      };
    }

    const symbol = safeText(row.symbol || row.ticker || row.underlying || row.contractSymbol, "UNKNOWN").toUpperCase();

    return {
      symbol,
      company: safeText(row.company || row.name, symbol),
      strategy: safeText(row.strategy || row.tradeType || row.role, "Review"),
      status: safeText(row.status || row.state || row.position, "Read-only"),
      risk: safeText(row.risk || row.blocker || row.permission, "Guarded"),
      source: safeText(row.source, "expanded_feed")
    };
  }

  function canonicalFallback() {
    const expanded = expandedPayload();
    const trust = trustPayload();
    const diagnostics = diagnosticsPayload();

    const counts = expanded.counts || {};
    const previews = expanded.previews || {};
    const trustObj = trust.trust || {};

    const candidateRows = (previews.candidates || []).map(normalizeSymbol);
    const positionRows = (previews.open_positions || []).map(normalizeSymbol);
    const ledgerRows = (previews.ledger || previews.trade_log || []).map(normalizeSymbol);
    const marketRows = (previews.market_symbols || []).map(normalizeSymbol);

    return {
      version: VERSION,
      source: "v35_safe_canonical_fallback",
      mapping_status: "fallback",
      trust_label: safeText(trustObj.label, trust.display_label || "Fallback / guarded"),
      safe_to_display: safeText(trustObj.safeToDisplay, "fallback_only"),
      freshness_score: trust.freshness_score || diagnostics.freshness_score || 72,
      rooms: {
        dashboard: {
          room: "Dashboard",
          lane: "account / focus / market state",
          primary_source: "expanded_counts + trust_labels",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "Use expanded counts as read-only context. Do not treat fallback as live.",
          cards: [
            { label: "Candidates", value: count(counts.candidate_log) },
            { label: "Open positions", value: count(counts.open_positions) },
            { label: "Market symbols", value: count(counts.market_symbols) },
            { label: "Trust", value: safeText(trustObj.label, "Fallback / guarded") }
          ],
          rows: candidateRows.slice(0, 4)
        },
        market_map: {
          room: "Market Map",
          lane: "constellation source labels",
          primary_source: "market_universe + candidate_log",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "Map symbols and constellations only with freshness labels.",
          cards: [
            { label: "Symbols", value: count(counts.market_symbols) },
            { label: "Sectors", value: count(counts.sectors) },
            { label: "Candidates", value: count(counts.candidate_log) },
            { label: "Sky label", value: safeText(trustObj.label, "Fallback / guarded") }
          ],
          rows: marketRows.slice(0, 4)
        },
        symbol_page: {
          room: "Symbol Page",
          lane: "one-symbol engine context",
          primary_source: "candidate/open position/ledger preview",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "One-star context can read whether a symbol appears in engine-shaped data, but cannot create permission.",
          cards: [
            { label: "Symbol context", value: "read-only" },
            { label: "Candidate rows", value: count(candidateRows) },
            { label: "Position rows", value: count(positionRows) },
            { label: "Trust", value: safeText(trustObj.label, "Fallback / guarded") }
          ],
          rows: [...candidateRows, ...positionRows, ...ledgerRows].slice(0, 4)
        },
        trade_center: {
          room: "Trade Center",
          lane: "candidate queue mapping",
          primary_source: "candidate_log + manual queue",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "Candidate queue can show normalized read-only candidates with caution labels before owner review.",
          cards: [
            { label: "Candidate queue", value: count(candidateRows) },
            { label: "Manual queue", value: count(counts.manual_live_queue) },
            { label: "Open positions", value: count(positionRows) },
            { label: "Execution", value: "manual only" }
          ],
          rows: candidateRows.slice(0, 6)
        },
        review_center: {
          room: "Review Center",
          lane: "receipt + ledger mapping",
          primary_source: "ledger + receipts + trade_log",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "Review Center can map receipts and ledger/trade rows as private review context.",
          cards: [
            { label: "Ledger rows", value: count(counts.ledger) },
            { label: "Trade log", value: count(counts.trade_log) },
            { label: "Receipts", value: count(counts.review_receipts) },
            { label: "Proof", value: "private" }
          ],
          rows: ledgerRows.slice(0, 6)
        },
        owner_console: {
          room: "Owner Console",
          lane: "diagnostics + source audit",
          primary_source: "diagnostics + trust labels + data files",
          trust_label: safeText(trustObj.label, "Fallback / guarded"),
          focus: "Owner Console audits source status, freshness, missing files, fallback state, and safe-to-display labels.",
          cards: [
            { label: "Freshness", value: safeText(trust.freshness_score || diagnostics.freshness_score, "72") },
            { label: "Safe display", value: safeText(trustObj.safeToDisplay, "fallback_only") },
            { label: "Files tracked", value: count(diagnostics.files) },
            { label: "Source", value: safeText(expanded.source, "expanded fallback") }
          ],
          rows: (diagnostics.files || []).slice(0, 6).map(file => ({
            symbol: safeText(file.name, "source"),
            company: safeText(file.label, "diagnostic"),
            status: safeText(file.status, "unknown"),
            risk: safeText(file.safe_to_display, "caution"),
            source: "diagnostics"
          }))
        }
      },
      tower_boundaries: {
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        stale_data_cannot_create_permission: true,
        mapping_does_not_create_permission: true
      },
      warnings: [
        "Canonical room mapping is read-only.",
        "Trust labels must stay visible.",
        "Mapping does not create permission.",
        "No broker wiring."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = canonicalFallback();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      mapping_status: safe.mapping_status || "normalized",
      trust_label: safe.trust_label || fallback.trust_label,
      safe_to_display: safe.safe_to_display || fallback.safe_to_display,
      freshness_score: Number.isFinite(Number(safe.freshness_score)) ? Number(safe.freshness_score) : fallback.freshness_score,
      rooms: {
        ...(fallback.rooms || {}),
        ...(safe.rooms || {})
      },
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        stale_data_cannot_create_permission: true,
        mapping_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_ENGINE_ROOM_MAPPING_V35 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      engine_room_mapping_v35: normalized,
      canonical_room_mapping: normalized.rooms
    };

    window.dispatchEvent(new CustomEvent("obEngineRoomMappingUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchRoomMapping() {
    mappingState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      mappingState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        mappingState.status = "ready";
        mappingState.source = normalized.source || "room_mapping_snapshot";
        mappingState.payload = normalized;
        mappingState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(canonicalFallback());

        mappingState.status = "guarded_fallback";
        mappingState.source = "guarded_room_mapping_route_fallback";
        mappingState.payload = fallback;
        mappingState.fallbackActive = true;
        mappingState.error = "Room mapping route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(canonicalFallback());

        mappingState.status = "http_fallback";
        mappingState.source = "http_" + response.status + "_fallback";
        mappingState.payload = fallback;
        mappingState.fallbackActive = true;
        mappingState.error = "Room mapping route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(canonicalFallback());

      mappingState.status = "error_fallback";
      mappingState.source = "fetch_error_fallback";
      mappingState.payload = fallback;
      mappingState.fallbackActive = true;
      mappingState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return mappingState;
  }

  function card(label, value) {
    return `
      <div class="ob-engine-room-map-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function row(item) {
    return `
      <div class="ob-engine-room-map-row">
        <strong>${safeText(item.symbol, "source")}</strong>
        <span>${safeText(item.company, "mapped row")}</span>
        <span>${safeText(item.strategy || item.status || item.risk, "Read-only room mapping")}</span>
        <div class="ob-engine-room-map-status gold">${safeText(item.source, "mapped")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = mappingState.payload || canonicalFallback();
    const room = currentRoomKey();
    const roomData = payload.rooms && payload.rooms[room] ? payload.rooms[room] : payload.rooms.dashboard;
    const rows = Array.isArray(roomData.rows) ? roomData.rows : [];
    const cards = Array.isArray(roomData.cards) ? roomData.cards : [];

    return `
      <div class="ob-engine-room-map-panel" id="obEngineRoomMappingPanel" data-ob-v35-engine-room-mapping="true">
        <div class="ob-engine-room-map-head">
          <div>
            <div class="ob-label">Engine Feed Canonical Room Mapping · V35</div>
            <div class="ob-engine-room-map-title">${roomLabel(room)} canonical mapping</div>
            <div class="ob-engine-room-map-subtitle">
              ${safeText(roomData.lane, "room mapping")} · ${safeText(payload.trust_label, "Fallback / guarded")} · ${safeText(mappingState.status, "booting")}
            </div>
          </div>

          <div class="ob-engine-room-map-chip-row">
            <span class="ob-engine-room-map-chip ${mappingState.fallbackActive ? "gold" : "green"}">${mappingState.fallbackActive ? "Safe fallback" : "Mapping active"}</span>
            <span class="ob-engine-room-map-chip gold">${safeText(payload.safe_to_display, "caution")}</span>
            <span class="ob-engine-room-map-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-engine-room-map-grid">
          ${cards.map(item => card(item.label, item.value)).join("")}
        </div>

        <div class="ob-engine-room-map-current">
          <strong>${safeText(roomData.primary_source, "canonical engine feed")}</strong>
          <span>${safeText(roomData.focus, "This room receives read-only mapped engine context with trust labels preserved.")}</span>
        </div>

        <div class="ob-engine-room-map-list">
          ${rows.length ? rows.map(row).join("") : `
            <div class="ob-engine-room-map-row">
              <strong>WAIT</strong>
              <span>No mapped rows yet.</span>
              <span>Canonical mapping is active, but this room only has fallback context.</span>
              <div class="ob-engine-room-map-status gold">fallback</div>
            </div>
          `}
        </div>

        <div class="ob-engine-room-map-note">
          <strong>Soulaana:</strong><br>
          The same engine feed now speaks each room’s language. But language is not permission. Mapping is for understanding.
        </div>

        <div class="ob-engine-room-map-boundary">
          <strong>Boundary:</strong><br>
          Canonical room mapping is read-only. Trust labels stay visible. Stale or fallback data cannot create permission. No broker wiring. No broker API. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obEngineRoomMappingPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const trust = document.getElementById("obEngineTrustLabelsPanel");
    const diagnostics = document.getElementById("obEngineFeedDiagnosticsPanel");
    const expanded = document.getElementById("obEngineFeedExpandedPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (trust && trust.parentNode) {
      trust.insertAdjacentElement("afterend", panel);
    } else if (diagnostics && diagnostics.parentNode) {
      diagnostics.insertAdjacentElement("afterend", panel);
    } else if (expanded && expanded.parentNode) {
      expanded.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = mappingState.payload || canonicalFallback();

    document.body.setAttribute("data-ob-v35-engine-room-mapping", "ready");
    window.OB_V35_ENGINE_ROOM_MAPPING_STATE = {
      version: VERSION,
      status: mappingState.status,
      fallbackActive: mappingState.fallbackActive,
      currentRoom: currentRoomKey(),
      trustLabel: payload.trust_label,
      safeToDisplay: payload.safe_to_display,
      readOnly: true,
      canonicalRoomMapping: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(canonicalFallback());

    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchRoomMapping();
    }, 1500);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineTrustLabelsUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_ENGINE_ROOM_MAPPING_V35_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return mappingState; },
    canonicalFallback,
    normalizePayload,
    expose,
    fetchRoomMapping,
    renderPanel,
    setFlags
  };
})();
