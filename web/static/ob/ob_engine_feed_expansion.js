// OBSERVATORY_V32_REAL_ENGINE_FEED_EXPANSION_READ_ONLY_JS

(function () {
  const VERSION = "OB_V32_REAL_ENGINE_FEED_EXPANSION_READ_ONLY";
  const ENDPOINT = "/ob/engine-feed-expanded.json";

  // V32 SMOKE MARKERS
  // Real Engine Feed Expansion read-only
  // expanded engine feed snapshot
  // candidate_log bridge
  // open_positions bridge
  // ledger and review bridge
  // market_universe bridge
  // pipeline_status bridge
  // safe preview fallback
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let expandedState = {
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

  function adapterPayload() {
    const adapter = window.OB_ENGINE_FEED_ADAPTER_V25;
    if (adapter && adapter.getState && adapter.getState().payload) {
      return adapter.getState().payload;
    }
    if (adapter && adapter.fallbackSnapshot) {
      return adapter.fallbackSnapshot();
    }
    return {
      source: "v32_local_fallback",
      positions_preview: [],
      candidates_preview: [],
      manual_live_queue: [],
      review_summary: {},
      market_health: { label: "Fallback waiting", breadth: "0 symbols" },
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      }
    };
  }

  function fallbackPayload() {
    const adapter = adapterPayload();
    const contracts = window.OB_DATA_CONTRACTS_V22;
    const market = contracts && contracts.marketMapContract ? contracts.marketMapContract() : {};

    return {
      version: VERSION,
      source: "v32_safe_preview_fallback",
      expansion_status: "fallback",
      counts: {
        candidate_log: count(adapter.candidates_preview || market.candidates),
        open_positions: count(adapter.positions_preview),
        manual_live_queue: count(adapter.manual_live_queue),
        market_symbols: count(market.symbols),
        sectors: count(market.sectors),
        review_receipts: window.OB_MANUAL_LIVE_RECEIPTS_V29 && window.OB_MANUAL_LIVE_RECEIPTS_V29.allReceipts ? count(window.OB_MANUAL_LIVE_RECEIPTS_V29.allReceipts()) : 0
      },
      previews: {
        candidates: (adapter.candidates_preview || market.candidates || []).slice(0, 6),
        open_positions: (adapter.positions_preview || []).slice(0, 6),
        manual_live_queue: (adapter.manual_live_queue || []).slice(0, 6)
      },
      data_files: {
        candidate_log: "fallback",
        open_positions: "fallback",
        ledger: "fallback",
        market_universe: "fallback",
        pipeline_status: "fallback"
      },
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        read_only: true
      },
      warnings: [
        "Using safe preview fallback.",
        "No broker wiring.",
        "No execution permissions changed."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = fallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      expansion_status: safe.expansion_status || "normalized",
      counts: {
        ...(fallback.counts || {}),
        ...(safe.counts || {})
      },
      previews: {
        ...(fallback.previews || {}),
        ...(safe.previews || {})
      },
      data_files: {
        ...(fallback.data_files || {}),
        ...(safe.data_files || {})
      },
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        read_only: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings,
      raw_meta: safe.raw_meta || {}
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_ENGINE_FEED_EXPANDED_V32 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      engine_feed_expanded_v32: normalized,
      expanded_counts: normalized.counts,
      expanded_previews: normalized.previews
    };

    window.dispatchEvent(new CustomEvent("obEngineFeedExpandedUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchExpandedFeed() {
    expandedState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      expandedState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        expandedState.status = "ready";
        expandedState.source = normalized.source || "expanded_snapshot";
        expandedState.payload = normalized;
        expandedState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(fallbackPayload());

        expandedState.status = "guarded_fallback";
        expandedState.source = "guarded_expanded_route_fallback";
        expandedState.payload = fallback;
        expandedState.fallbackActive = true;
        expandedState.error = "Expanded route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(fallbackPayload());

        expandedState.status = "http_fallback";
        expandedState.source = "http_" + response.status + "_fallback";
        expandedState.payload = fallback;
        expandedState.fallbackActive = true;
        expandedState.error = "Expanded route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(fallbackPayload());

      expandedState.status = "error_fallback";
      expandedState.source = "fetch_error_fallback";
      expandedState.payload = fallback;
      expandedState.fallbackActive = true;
      expandedState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return expandedState;
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

  function card(label, value) {
    return `
      <div class="ob-engine-expanded-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function row(label, detail, status, kind) {
    return `
      <div class="ob-engine-expanded-row">
        <strong>${label}</strong>
        <span>${detail}</span>
        <div class="ob-engine-expanded-status ${kind || ""}">${status}</div>
      </div>
    `;
  }

  function roomFocus(room, payload) {
    if (room === "dashboard") return "Dashboard can now summarize broader engine-shaped data without making any execution decision.";
    if (room === "market_map") return "Market Map can read expanded symbol/candidate counts while keeping preview fallback honest.";
    if (room === "symbol_page") return "Symbol Page can understand whether a symbol appears in candidate/open-position/review feeds without creating permission.";
    if (room === "trade_center") return "Trade Center can see candidate_log, open_positions, and Manual Live queue counts as read-only context.";
    if (room === "review_center") return "Review Center can see ledger/review/receipt status while proof remains private and Tower-gated.";
    if (room === "owner_console") return "Owner Console can diagnose which engine files are present, guarded, missing, or fallback-driven.";
    return "Expanded engine feed is read-only context.";
  }

  function panelHtml() {
    const payload = expandedState.payload || fallbackPayload();
    const counts = payload.counts || {};
    const room = currentRoomKey();
    const statusKind = expandedState.fallbackActive ? "gold" : "green";

    return `
      <div class="ob-engine-expanded-panel" id="obEngineFeedExpandedPanel" data-ob-v32-engine-feed-expansion="true">
        <div class="ob-engine-expanded-head">
          <div>
            <div class="ob-label">Engine Feed Expansion · V32</div>
            <div class="ob-engine-expanded-title">Read-only expanded engine feed</div>
            <div class="ob-engine-expanded-subtitle">
              ${safeText(payload.source, "waiting")} · ${safeText(expandedState.status, "booting")} · ${roomFocus(room, payload)}
            </div>
          </div>

          <div class="ob-engine-expanded-chip-row">
            <span class="ob-engine-expanded-chip ${statusKind}">${expandedState.fallbackActive ? "Safe fallback" : "Expanded snapshot"}</span>
            <span class="ob-engine-expanded-chip gold">Read-only</span>
            <span class="ob-engine-expanded-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-engine-expanded-grid">
          ${card("Candidates", count(counts.candidate_log))}
          ${card("Open positions", count(counts.open_positions))}
          ${card("Manual queue", count(counts.manual_live_queue))}
          ${card("Ledger rows", count(counts.ledger))}
          ${card("Market symbols", count(counts.market_symbols))}
          ${card("Review receipts", count(counts.review_receipts))}
        </div>

        <div class="ob-engine-expanded-list">
          ${row("candidate_log bridge", `Status: ${safeText(payload.data_files && payload.data_files.candidate_log, "unknown")}`, "read-only", "green")}
          ${row("open_positions bridge", `Status: ${safeText(payload.data_files && payload.data_files.open_positions, "unknown")}`, "read-only", "green")}
          ${row("ledger and review bridge", `Ledger: ${safeText(payload.data_files && payload.data_files.ledger, "unknown")} · Receipts: ${count(counts.review_receipts)}`, "private", "gold")}
          ${row("market_universe bridge", `Symbols: ${count(counts.market_symbols)} · Sectors: ${count(counts.sectors)}`, "observe", "green")}
          ${row("pipeline_status bridge", `Status: ${safeText(payload.data_files && payload.data_files.pipeline_status, "unknown")}`, "diagnostic", "gold")}
        </div>

        <div class="ob-engine-expanded-note">
          <strong>Soulaana:</strong><br>
          More data does not mean more permission. This expansion helps the rooms see better. Tower still decides access. Manual Live still means owner review.
        </div>

        <div class="ob-engine-expanded-boundary">
          <strong>Boundary:</strong><br>
          Read-only feed expansion. No broker wiring. No broker API. No auto execution. Live Auto Locked. Proof and review data stay private.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obEngineFeedExpandedPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const qa = document.getElementById("obPrivateBetaQaPanel");
    const testerOps = document.getElementById("obBetaTesterOpsPanel");
    const receipts = document.getElementById("obManualLiveReceiptsPanel");
    const candidate = document.getElementById("obCandidateCardsPanel");
    const polish = document.getElementById("obRoomDataPolishPanel");
    const snapshot = document.getElementById("obSnapshotDisplayPanel");
    const engineBar = document.getElementById("obEngineFeedBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else if (testerOps && testerOps.parentNode) {
      testerOps.insertAdjacentElement("afterend", panel);
    } else if (receipts && receipts.parentNode) {
      receipts.insertAdjacentElement("afterend", panel);
    } else if (candidate && candidate.parentNode) {
      candidate.insertAdjacentElement("afterend", panel);
    } else if (polish && polish.parentNode) {
      polish.insertAdjacentElement("afterend", panel);
    } else if (snapshot && snapshot.parentNode) {
      snapshot.insertAdjacentElement("afterend", panel);
    } else if (engineBar && engineBar.parentNode) {
      engineBar.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    document.body.setAttribute("data-ob-v32-engine-feed-expansion", "ready");
    window.OB_V32_ENGINE_FEED_EXPANSION_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      status: expandedState.status,
      fallbackActive: expandedState.fallbackActive,
      readOnly: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(fallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchExpandedFeed();
    }, 1140);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_ENGINE_FEED_EXPANSION_V32 = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return expandedState; },
    fallbackPayload,
    normalizePayload,
    expose,
    fetchExpandedFeed,
    renderPanel,
    setFlags
  };
})();
