// OBSERVATORY_TRADE_CENTER_V14_REAL_ROOM_JS

const OB_TRADE_TABS = [
  { key: "positions", label: "Open Positions" },
  { key: "signals", label: "Signals" },
  { key: "watchlist", label: "Watchlist" },
  { key: "candidates", label: "Candidates" },
  { key: "manual", label: "Manual Live Queue" }
];

function obFlattenSymbols() {
  const sectors = (window.OB_MARKET_DATA && window.OB_MARKET_DATA.sectors) || [];
  const rows = [];

  sectors.forEach((sector) => {
    sector.symbols.forEach((symbolObj) => {
      rows.push({
        ...symbolObj,
        sectorName: sector.name,
        constellationName: sector.constellationName,
        sectorStrength: sector.strength
      });
    });
  });

  return rows;
}

function obTradeRows(tab) {
  const all = obFlattenSymbols();

  if (tab === "positions") {
    return all.filter(row => String(row.position || "").toLowerCase().includes("open") || ["MU", "AMD", "INTC"].includes(row.symbol)).slice(0, 6);
  }

  if (tab === "signals") {
    return all.filter(row => row.tier === "hot" || row.tier === "watch").slice(0, 8);
  }

  if (tab === "watchlist") {
    return all.filter(row => row.tier === "watch" || String(row.position || "").toLowerCase().includes("watch")).slice(0, 8);
  }

  if (tab === "candidates") {
    return all.filter(row => row.tier === "hot").slice(0, 8);
  }

  if (tab === "manual") {
    return all.filter(row => row.tier === "hot").slice(0, 5).map((row, index) => ({
      ...row,
      manualStatus: index === 0 ? "Needs owner review" : "Waiting"
    }));
  }

  return all.slice(0, 8);
}

function obTradeStatus(row, tab) {
  if (tab === "manual") return row.manualStatus || "Waiting";
  if (tab === "positions") return row.position || "Open / Review";
  if (tab === "signals") return row.tier === "hot" ? "Signal active" : "Signal forming";
  if (tab === "watchlist") return "Watching";
  if (tab === "candidates") return "Candidate";
  return "Review";
}

function obTradeRisk(row) {
  if (row.tier === "hot") return row.risk || "Moderate";
  if (row.tier === "watch") return row.risk || "Guarded";
  return row.risk || "Low priority";
}

function obTradeConfidence(row) {
  if (row.tier === "hot") return "82";
  if (row.tier === "watch") return "61";
  return "38";
}

function obTradeAction(row, tab) {
  if (tab === "manual") return "Review ticket";
  if (tab === "positions") return "Manage";
  if (tab === "signals") return "Open symbol";
  if (tab === "watchlist") return "Keep watch";
  if (tab === "candidates") return "Review";
  return "Inspect";
}

function obTradeSoulaana(row, tab) {
  if (tab === "manual") {
    return "This is the manual lane, so we slow down. OB may prepare the card, but you do not place anything until permission, risk, and the broker checklist agree.";
  }

  if (tab === "positions") {
    return "Open positions get protection before excitement. Manage what is already alive before reaching for a new star.";
  }

  if (tab === "signals") {
    return "A signal is an invitation to review, not a command to act. If the reason is not clean, let the star keep proving itself.";
  }

  if (tab === "watchlist") {
    return "Watching is discipline. You are allowed to notice without needing to touch it.";
  }

  if (tab === "candidates") {
    return "Candidate means close to action, not entitled to action. It still has to pass risk, permission, and account fit.";
  }

  return "Review before action. Clean beats fast.";
}

function obTicketPreview(row, tab) {
  if (tab === "manual" || tab === "candidates") {
    return {
      contract: `${row.symbol} next monthly call`,
      entry: "Review entry zone",
      stop: "Premium stop required",
      target: "Target only if movement confirms",
      blocker: "Live automated locked"
    };
  }

  if (tab === "positions") {
    return {
      contract: row.tradeType || "Option premium mode",
      entry: "Already open / tracked",
      stop: "Follow active premium stop",
      target: "Review target zone",
      blocker: "Manage before adding"
    };
  }

  return {
    contract: "No order ticket",
    entry: "No entry yet",
    stop: "Not assigned",
    target: "Not assigned",
    blocker: "Watch / review only"
  };
}

function obOpenSymbol(row) {
  window.location.href = "/ob/symbol/" + encodeURIComponent(row.symbol);
}

function obRecordTradeAction(symbol, action) {
  const receipt = document.getElementById("tradeReceiptPreview");
  if (!receipt) return;

  const now = new Date().toLocaleString();

  receipt.innerHTML = `
    <strong>Receipt updated:</strong><br>
    Symbol: ${symbol}<br>
    Action: ${action}<br>
    Time: ${now}<br>
    Execution responsibility: Owner at brokerage only if later approved.<br>
    OB status: ${action === "Approve for manual placement" ? "Awaiting broker checklist review" : action}
  `;
}

function obRenderSelectedTrade(row, tab) {
  const panel = document.getElementById("tradeSelectedPanel");
  const ticket = obTicketPreview(row, tab);

  panel.innerHTML = `
    <div class="trade-selected-title">${row.symbol}</div>
    <div class="trade-selected-subtitle">${row.company || row.symbol} · ${row.constellationName}</div>

    <div class="trade-detail-stack">
      <div class="trade-detail-card gold">
        <span>Status</span>
        <strong>${obTradeStatus(row, tab)}</strong>
      </div>

      <div class="trade-detail-card green">
        <span>Confidence / setup</span>
        <strong>${obTradeConfidence(row)} · ${row.role || "Market watch"}</strong>
      </div>

      <div class="trade-detail-card">
        <span>Asset type</span>
        <strong>${row.tradeType || "Watch only"}</strong>
      </div>

      <div class="trade-detail-card red">
        <span>Risk / blocker</span>
        <strong>${obTradeRisk(row)} · ${ticket.blocker}</strong>
      </div>

      <div class="ticket-box">
        <div class="ticket-line"><span>Contract</span><strong>${ticket.contract}</strong></div>
        <div class="ticket-line"><span>Entry</span><strong>${ticket.entry}</strong></div>
        <div class="ticket-line"><span>Stop</span><strong>${ticket.stop}</strong></div>
        <div class="ticket-line"><span>Target</span><strong>${ticket.target}</strong></div>
      </div>

      <div class="trade-soulaana-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        ${obTradeSoulaana(row, tab)}
      </div>

      <div class="trade-action-stack">
        <button class="trade-action-button" onclick="obOpenSymbol(${JSON.stringify(row).replace(/"/g, '&quot;')})">Open Symbol Page</button>
        <button class="trade-action-button aqua" onclick="obRecordTradeAction('${row.symbol}', 'Snooze / watch')">Snooze / watch</button>
        <button class="trade-action-button" onclick="obRecordTradeAction('${row.symbol}', 'Approve for manual placement')">Approve for manual placement</button>
        <button class="trade-action-button red" onclick="obRecordTradeAction('${row.symbol}', 'Rejected')">Reject</button>
      </div>

      <div class="trade-receipt-preview" id="tradeReceiptPreview">
        <strong>No receipt yet.</strong><br>
        Choose an action to create a review receipt preview.
      </div>
    </div>
  `;
}

function obRenderTradeRows(tab) {
  const rows = obTradeRows(tab);
  const list = document.getElementById("tradeRowList");

  list.innerHTML = rows.map((row, index) => `
    <div class="trade-row ${index === 0 ? "active" : ""}" data-symbol="${row.symbol}" data-index="${index}">
      <div class="trade-row-top">
        <div>
          <div class="trade-symbol">${row.symbol}</div>
          <div class="trade-name">${row.company || row.symbol} · ${row.constellationName}</div>
        </div>

        <div class="trade-state">
          <span class="trade-mini-chip ${row.tier === "hot" ? "green" : row.tier === "watch" ? "gold" : "red"}">${obTradeStatus(row, tab)}</span>
          <span class="trade-mini-chip red">Live locked</span>
        </div>
      </div>

      <div class="trade-row-metrics">
        <div class="trade-row-metric"><span>Type</span><strong>${row.tradeType || "Watch"}</strong></div>
        <div class="trade-row-metric"><span>Risk</span><strong>${obTradeRisk(row)}</strong></div>
        <div class="trade-row-metric"><span>Score</span><strong>${obTradeConfidence(row)}</strong></div>
        <div class="trade-row-metric"><span>Action</span><strong>${obTradeAction(row, tab)}</strong></div>
      </div>
    </div>
  `).join("");

  list.querySelectorAll(".trade-row").forEach((item) => {
    item.addEventListener("click", () => {
      list.querySelectorAll(".trade-row").forEach(row => row.classList.remove("active"));
      item.classList.add("active");
      obRenderSelectedTrade(rows[Number(item.dataset.index)], tab);
    });
  });

  if (rows[0]) {
    obRenderSelectedTrade(rows[0], tab);
  }
}

function obSetTradeTab(tab) {
  document.querySelectorAll(".trade-tab").forEach(button => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });

  const title = document.getElementById("tradeListTitle");
  const subtitle = document.getElementById("tradeListSubtitle");

  const label = OB_TRADE_TABS.find(item => item.key === tab).label;
  title.textContent = label;
  subtitle.textContent = tab === "manual"
    ? "Manual Live candidates require owner review before any broker action."
    : "Click a row to open Soulaana's detail and action context.";

  obRenderTradeRows(tab);
}

function obRenderTradeCenter() {
  const mount = document.getElementById("tradeCenterMount");

  mount.innerHTML = `
    <div class="trade-center-shell">
      <div class="ob-panel trade-control-strip">
        <div class="ob-label">Control Strip</div>

        <div class="trade-control-grid">
          <div class="trade-control-card"><span>Mode</span><strong>Paper / Manual guarded</strong></div>
          <div class="trade-control-card"><span>Slots</span><strong>2 open slots</strong></div>
          <div class="trade-control-card"><span>Daily entries</span><strong>0 / 6 used</strong></div>
          <div class="trade-control-card"><span>Risk state</span><strong>Guarded</strong></div>
          <div class="trade-control-card"><span>Tower</span><strong>Clear · Live auto locked</strong></div>
        </div>
      </div>

      <div class="ob-panel trade-tabs">
        ${OB_TRADE_TABS.map((tab, index) => `
          <button class="trade-tab ${index === 0 ? "active" : ""}" data-tab="${tab.key}">
            ${tab.label}
          </button>
        `).join("")}
      </div>

      <div class="trade-center-grid">
        <div class="ob-panel trade-list-panel">
          <div class="ob-label">Trade Center</div>
          <div class="detail-title" id="tradeListTitle">Open Positions</div>
          <div class="detail-sub" id="tradeListSubtitle">Click a row to open Soulaana's detail and action context.</div>
          <div class="trade-row-list" id="tradeRowList"></div>
        </div>

        <div class="ob-panel trade-selected-panel" id="tradeSelectedPanel"></div>
      </div>
    </div>
  `;

  document.querySelectorAll(".trade-tab").forEach(button => {
    button.addEventListener("click", () => obSetTradeTab(button.dataset.tab));
  });

  obSetTradeTab("positions");
}

document.addEventListener("DOMContentLoaded", obRenderTradeCenter);

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.tradeCenterContract) {
  window.OB_TRADE_CENTER_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.tradeCenterContract();
}
