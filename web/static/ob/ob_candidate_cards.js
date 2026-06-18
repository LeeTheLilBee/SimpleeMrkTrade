// OBSERVATORY_V28_CANDIDATE_SIGNAL_CARD_NORMALIZATION_JS

(function () {
  const VERSION = "OB_V28_CANDIDATE_SIGNAL_CARD_NORMALIZATION";

  // V28 SMOKE MARKERS
  // Candidate Signal Card Normalization
  // Market Map candidate cards
  // Symbol Page candidate card
  // Trade Center candidate queue cards
  // Manual Live normalized cards
  // Review Center receipt candidate normalization
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

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function count(value) {
    return Array.isArray(value) ? value.length : 0;
  }

  function adapterState() {
    if (window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.getState) {
      return window.OB_ENGINE_FEED_ADAPTER_V25.getState();
    }

    return {
      status: "adapter unavailable",
      fallbackActive: true,
      payload: null,
      httpStatus: null
    };
  }

  function adapterPayload() {
    const state = adapterState();

    if (state && state.payload) {
      return state.payload;
    }

    if (window.OB_ENGINE_FEED_ADAPTER_V25 && window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot) {
      return window.OB_ENGINE_FEED_ADAPTER_V25.fallbackSnapshot();
    }

    return {
      source: "candidate_card_fallback",
      candidates_preview: [],
      manual_live_queue: [],
      positions_preview: [],
      review_summary: { receipts: 0 },
      tower_boundaries: {
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      }
    };
  }

  function contracts() {
    return window.OB_DATA_CONTRACTS_V22 || null;
  }

  function contractRows() {
    const c = contracts();

    if (!c || !c.marketMapContract) {
      return [];
    }

    const market = c.marketMapContract();
    const merged = [
      ...(market.candidates || []),
      ...(market.signals || []),
      ...(market.watchlist || [])
    ];

    const seen = new Set();
    return merged.filter(item => {
      const symbol = safeText(item.symbol, "UNKNOWN").toUpperCase();
      if (seen.has(symbol)) return false;
      seen.add(symbol);
      return true;
    });
  }

  function manualReceipts() {
    if (window.OB_MANUAL_LIVE_V19 && window.OB_MANUAL_LIVE_V19.loadReceipts) {
      return window.OB_MANUAL_LIVE_V19.loadReceipts();
    }

    return [];
  }

  function classifyRisk(value) {
    const risk = safeText(value, "Guarded").toLowerCase();

    if (risk.includes("high") || risk.includes("crowd") || risk.includes("elevated")) return "High attention";
    if (risk.includes("moderate")) return "Moderate";
    if (risk.includes("low")) return "Low";
    return safeText(value, "Guarded");
  }

  function normalizeState(row) {
    const status = safeText(row.manualStatus || row.status || row.position || row.tier, "Watch").toLowerCase();

    if (status.includes("needs owner review")) return "Needs owner review";
    if (status.includes("monitor")) return "Monitoring";
    if (status.includes("reject")) return "Rejected";
    if (status.includes("snooze")) return "Snoozed";
    if (status.includes("candidate") || status.includes("hot")) return "Candidate";
    if (status.includes("watch")) return "Watch";
    return "Normalized";
  }

  function normalizedClass(card) {
    const state = safeText(card.normalizedState, "").toLowerCase();
    const risk = safeText(card.risk, "").toLowerCase();

    if (risk.includes("high") || state.includes("rejected")) return "blocked";
    if (state.includes("candidate") || state.includes("needs owner review") || state.includes("monitoring")) return "hot";
    return "watch";
  }

  function normalizeCandidate(input, source) {
    const row = input || {};
    const symbol = safeText(row.symbol, "UNKNOWN").toUpperCase();
    const company = safeText(row.company, symbol);
    const state = normalizeState(row);

    return {
      version: VERSION,
      symbol,
      company,
      strategy: safeText(row.strategy || row.tradeType || row.role, "Option-first review"),
      confidence: safeText(row.confidence || row.score || row.tier, "Review"),
      risk: classifyRisk(row.risk || row.blocker || row.permission),
      direction: safeText(row.direction || row.position || row.tradeType, "Watch"),
      contract: safeText(row.contract || row.contractSymbol || row.suggested_contract, symbol + " next review contract"),
      permission: safeText(row.permission, "Paper Allowed · Live Auto Locked"),
      source: safeText(source || row.source, "normalized"),
      normalizedState: state,
      receiptState: safeText(row.receiptState || row.action || state, state),
      why: safeText(row.why || row.fact || row.notes, "OB is normalizing this candidate so every room speaks the same language."),
      blocker: safeText(row.blocker, "Live Auto Locked. Manual placement only."),
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true,
      raw: row
    };
  }

  function candidateRowsForRoom(room) {
    const payload = adapterPayload();
    const fromAdapter = [
      ...(payload.candidates_preview || []),
      ...(payload.manual_live_queue || []),
      ...(payload.positions_preview || [])
    ];

    const fromContracts = contractRows();

    if (room === "review_center") {
      return manualReceipts().slice(-6).map(receipt => normalizeCandidate({
        symbol: receipt.symbol,
        company: receipt.company,
        strategy: receipt.strategy,
        status: receipt.status,
        action: receipt.action,
        contract: receipt.contract,
        notes: receipt.responsibility,
        risk: "Receipt review",
        permission: receipt.tower || "Live Auto Locked"
      }, "review_receipt"));
    }

    if (room === "symbol_page") {
      const symbol = window.location.pathname.split("/").filter(Boolean).pop() || "MU";
      const found = [...fromAdapter, ...fromContracts].find(item => safeText(item.symbol, "").toUpperCase() === symbol.toUpperCase());
      return [normalizeCandidate(found || { symbol, company: symbol, risk: "Symbol context", position: "Watch" }, "symbol_page")];
    }

    if (room === "trade_center") {
      return [
        ...(payload.manual_live_queue || []),
        ...(payload.candidates_preview || []),
        ...fromContracts.slice(0, 3)
      ].slice(0, 8).map(row => normalizeCandidate(row, "trade_center"));
    }

    if (room === "market_map") {
      return [
        ...(payload.candidates_preview || []),
        ...fromContracts
      ].slice(0, 8).map(row => normalizeCandidate(row, "market_map"));
    }

    if (room === "owner_console") {
      return [
        normalizeCandidate({
          symbol: "ENGINE",
          company: "Engine Feed Adapter",
          strategy: "Diagnostics",
          confidence: adapterState().status,
          risk: adapterState().fallbackActive ? "Fallback active" : "Snapshot active",
          position: "Read-only diagnostics",
          permission: "Tower guarded · Live Auto Locked",
          contract: "No execution contract"
        }, "owner_console")
      ];
    }

    return [
      ...(payload.candidates_preview || []),
      ...(payload.positions_preview || []),
      ...fromContracts.slice(0, 3)
    ].slice(0, 6).map(row => normalizeCandidate(row, "dashboard"));
  }

  function summary(room, cards) {
    const needsReview = cards.filter(card => card.normalizedState === "Needs owner review").length;
    const candidates = cards.filter(card => card.normalizedState === "Candidate").length;
    const monitoring = cards.filter(card => card.normalizedState === "Monitoring").length;
    const watch = cards.filter(card => card.normalizedState === "Watch").length;
    const highRisk = cards.filter(card => safeText(card.risk, "").toLowerCase().includes("high")).length;

    return {
      total: cards.length,
      needsReview,
      candidates,
      monitoring,
      watch,
      highRisk,
      room
    };
  }

  function summaryCard(label, value) {
    return `
      <div class="ob-candidate-summary-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function badge(value, kind) {
    return `<span class="ob-candidate-badge ${kind || ""}">${value}</span>`;
  }

  function candidateCard(card) {
    const className = normalizedClass(card);
    const riskClass = safeText(card.risk, "").toLowerCase().includes("high") ? "red" : safeText(card.risk, "").toLowerCase().includes("moderate") ? "gold" : "green";

    return `
      <div class="ob-candidate-card ${className}" data-ob-v28-candidate-card="${card.symbol}">
        <div class="ob-candidate-card-top">
          <div>
            <div class="ob-candidate-symbol">${card.symbol}</div>
            <div class="ob-candidate-company">${card.company}</div>
          </div>

          <div class="ob-candidate-badge-stack">
            ${badge(card.normalizedState, className === "blocked" ? "red" : className === "hot" ? "green" : "gold")}
            ${badge(card.source, "gold")}
          </div>
        </div>

        <div class="ob-candidate-metrics">
          <div class="ob-candidate-metric"><span>Strategy</span><strong>${card.strategy}</strong></div>
          <div class="ob-candidate-metric"><span>Confidence</span><strong>${card.confidence}</strong></div>
          <div class="ob-candidate-metric"><span>Risk</span><strong>${card.risk}</strong></div>
          <div class="ob-candidate-metric"><span>Permission</span><strong>${card.permission}</strong></div>
          <div class="ob-candidate-metric"><span>Contract</span><strong>${card.contract}</strong></div>
          <div class="ob-candidate-metric"><span>Boundary</span><strong>No broker API</strong></div>
        </div>

        <div class="ob-candidate-note">
          <strong style="color: var(--ob-gold);">Normalized read:</strong><br>
          ${card.why}
        </div>

        <div class="ob-candidate-action-row">
          <button class="ob-candidate-button" type="button" onclick="window.location.href='/ob/symbol/${card.symbol}'">Open Symbol</button>
          <button class="ob-candidate-button" type="button" onclick="window.location.href='/ob/trade-center'">Trade Center</button>
        </div>
      </div>
    `;
  }

  function panelFocus(room) {
    if (room === "market_map") {
      return "Market Map now speaks the same candidate language as Trade Center: symbol, strategy, risk, permission, source, and state.";
    }

    if (room === "symbol_page") {
      return "Symbol Page gets the same normalized candidate card, but it stays one-star focused and does not create permission.";
    }

    if (room === "trade_center") {
      return "Trade Center candidate and Manual Live rows now share one clean card shape before owner review.";
    }

    if (room === "review_center") {
      return "Review Center receipts can be read back as normalized candidate history without exposing private proof.";
    }

    if (room === "owner_console") {
      return "Owner Console can audit candidate-card normalization and confirm the read-only boundaries stay intact.";
    }

    return "Dashboard can summarize candidate state without changing execution or permission.";
  }

  function panelHtml() {
    const room = currentRoomKey();
    const cards = candidateRowsForRoom(room);
    const totals = summary(room, cards);
    const state = adapterState();
    const sourceClass = state.fallbackActive ? "gold" : "green";

    return `
      <div class="ob-candidate-normal-panel" id="obCandidateCardsPanel" data-ob-v28-candidate-normalization="true">
        <div class="ob-candidate-normal-head">
          <div>
            <div class="ob-label">Candidate / Signal Card Normalization · V28</div>
            <div class="ob-candidate-normal-title">${roomLabel(room)} normalized cards</div>
            <div class="ob-candidate-normal-subtitle">
              One card language for Market Map, Symbol Page, Trade Center, Manual Live, and Review Center receipts.
            </div>
          </div>

          <div class="ob-candidate-normal-chip-row">
            <span class="ob-candidate-normal-chip ${sourceClass}">${state.fallbackActive ? "Preview fallback" : "Snapshot active"}</span>
            <span class="ob-candidate-normal-chip gold">${safeText(state.status, "waiting")}</span>
            <span class="ob-candidate-normal-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-candidate-summary-strip">
          ${summaryCard("Cards", totals.total)}
          ${summaryCard("Needs review", totals.needsReview)}
          ${summaryCard("Candidates", totals.candidates)}
          ${summaryCard("Monitoring", totals.monitoring)}
          ${summaryCard("High risk", totals.highRisk)}
        </div>

        <div class="ob-candidate-card-grid">
          ${cards.length ? cards.slice(0, 6).map(candidateCard).join("") : `
            <div class="ob-candidate-card watch">
              <div class="ob-candidate-symbol">WAIT</div>
              <div class="ob-candidate-company">No candidate rows available yet.</div>
              <div class="ob-candidate-note">Preview fallback is active. OB is not pretending missing data is live.</div>
            </div>
          `}
        </div>

        <div class="ob-candidate-boundary">
          <strong>Boundary:</strong><br>
          ${panelFocus(room)}
          <br><br>
          No broker API: true · No auto execution: true · Live Auto Locked: true
        </div>
      </div>
    `;
  }

  function insertPanel() {
    const existing = document.getElementById("obCandidateCardsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const roomPolish = document.getElementById("obRoomDataPolishPanel");
    const snapshot = document.getElementById("obSnapshotDisplayPanel");
    const engineBar = document.getElementById("obEngineFeedBar");
    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (roomPolish && roomPolish.parentNode) {
      roomPolish.insertAdjacentElement("afterend", panel);
    } else if (snapshot && snapshot.parentNode) {
      snapshot.insertAdjacentElement("afterend", panel);
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
    document.body.setAttribute("data-ob-v28-candidate-card-normalization", "ready");
    window.OB_V28_CANDIDATE_CARD_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      adapterSeen: !!window.OB_ENGINE_FEED_ADAPTER_V25,
      contractsSeen: !!window.OB_DATA_CONTRACTS_V22,
      manualLiveSeen: !!window.OB_MANUAL_LIVE_V19,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    setTimeout(function () {
      insertPanel();
      setFlags();
    }, 660);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    insertPanel();
    setFlags();
  });

  window.OB_CANDIDATE_CARDS_V28 = {
    version: VERSION,
    normalizeCandidate,
    candidateRowsForRoom,
    panelHtml,
    insertPanel,
    setFlags
  };
})();
