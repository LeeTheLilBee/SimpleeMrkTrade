// OBSERVATORY_DASHBOARD_V16_REAL_ROOM_JS

function obDashboardSymbols() {
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

function obDashboardHotSymbols() {
  return obDashboardSymbols().filter(row => row.tier === "hot").slice(0, 4);
}

function obDashboardOpenPositions() {
  const all = obDashboardSymbols();
  return all.filter(row => String(row.position || "").toLowerCase().includes("open") || ["MU", "AMD", "INTC"].includes(row.symbol)).slice(0, 3);
}

function obDashboardMarketHealth() {
  const all = obDashboardSymbols();
  const hot = all.filter(row => row.tier === "hot").length;
  const watch = all.filter(row => row.tier === "watch").length;
  const background = all.filter(row => row.tier === "background").length;

  return {
    score: 82,
    label: "Healthy but guarded",
    breadth: hot + " hot · " + watch + " watch · " + background + " background",
    regime: "Risk-on pockets",
    caution: "Semiconductor strength is active, but crowding must stay visible.",
    soulaana: "Market health is good enough to pay attention, not good enough to get careless. The bright stars are useful, but Tower boundaries still matter."
  };
}

function obPositionStatus(symbolObj) {
  if (String(symbolObj.position || "").toLowerCase().includes("open")) return "Open / Review";
  if (symbolObj.tier === "hot") return "Candidate watch";
  if (symbolObj.tier === "watch") return "Watchlist";
  return "Background";
}

function obPositionRisk(symbolObj) {
  if (symbolObj.risk) return symbolObj.risk;
  if (symbolObj.tier === "hot") return "Moderate";
  if (symbolObj.tier === "watch") return "Guarded";
  return "Low priority";
}

function obPositionSoulaana(symbolObj) {
  if (symbolObj.tier === "hot") {
    return "Auntie says: this one is bright, but bright is not permission. Manage the risk, check the account fit, and do not let momentum make you sloppy.";
  }

  if (symbolObj.tier === "watch") {
    return "Auntie says: this one is leaning forward, but it still has to earn trust. Watch it without rushing it.";
  }

  return "Auntie says: this is context, not action. Leave it quiet unless OB gives you a cleaner reason.";
}

function obRenderDashboard() {
  const mount = document.getElementById("dashboardMount");
  const health = obDashboardMarketHealth();
  const positions = obDashboardOpenPositions();
  const hotSymbols = obDashboardHotSymbols();

  mount.innerHTML = `
    <div class="dashboard-shell">
      <div class="dashboard-hero-grid">
        <div class="ob-panel dashboard-hero-panel">
          <div class="ob-label">Welcome back</div>
          <h2 class="dashboard-welcome">What matters right now.</h2>
          <div class="dashboard-subcopy">
            This is the control room. OB is watching the market sky, your active risk, and the Tower permission state before anything moves toward action.
          </div>

          <div class="dashboard-soulaana-read">
            <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
            ${health.soulaana} Your job is not to touch everything glowing. Your job is to move clean, protect the account, and only escalate what survives review.
          </div>

          <div class="dashboard-hero-actions">
            <a class="dashboard-action-button" href="/ob/market-map">Open Market Map</a>
            <a class="dashboard-action-button" href="/ob/trade-center">Review Trade Center</a>
            <a class="dashboard-action-button" href="/ob/review-center">Open Review Center</a>
            <a class="dashboard-action-button locked" href="#">Live Auto Locked</a>
          </div>
        </div>

        <div class="ob-panel dashboard-health-panel">
          <div class="ob-label">Account Health Score</div>

          <div class="health-gauge-wrap">
            <div class="health-gauge">
              <div class="health-pointer"></div>
              <div class="health-center">
                <strong>${health.score}</strong>
                <span>${health.label}</span>
              </div>
            </div>
          </div>

          <div class="health-explain">
            <strong style="color: var(--ob-gold);">Why it is ${health.score}:</strong><br>
            The account looks healthy because open risk is controlled and the market has active pockets. It is not a perfect score because crowding and Live Auto lock still require discipline.
          </div>
        </div>
      </div>

      <div class="ob-panel dashboard-section-panel">
        <div class="ob-label">Account Snapshot</div>

        <div class="dashboard-metric-grid">
          <div class="dashboard-metric-card"><span>Current OB Account</span><strong>Personal OB · Paper</strong></div>
          <div class="dashboard-metric-card"><span>Mode</span><strong>Paper / Manual guarded</strong></div>
          <div class="dashboard-metric-card"><span>Tower State</span><strong>Clear · Live Auto Locked</strong></div>
          <div class="dashboard-metric-card"><span>Market Health</span><strong>${health.label}</strong></div>
        </div>
      </div>

      <div class="dashboard-main-grid">
        <div class="ob-panel dashboard-section-panel">
          <div class="ob-label">Open Positions Preview</div>
          <div class="detail-title">Positions that need eyes</div>
          <div class="detail-sub">Each position gets its own box because each one has its own risk, reason, and next move.</div>

          <div class="dashboard-position-grid">
            ${positions.map(row => `
              <div class="dashboard-position-card">
                <div class="dashboard-position-top">
                  <div>
                    <div class="dashboard-symbol">${row.symbol}</div>
                    <div class="dashboard-position-sub">${row.company || row.symbol} · ${row.constellationName}</div>
                  </div>

                  <div class="dashboard-chip-row">
                    <span class="dashboard-mini-chip ${row.tier === "hot" ? "green" : "gold"}">${obPositionStatus(row)}</span>
                    <span class="dashboard-mini-chip red">Live locked</span>
                  </div>
                </div>

                <div class="dashboard-position-metrics">
                  <div class="dashboard-position-metric"><span>Type</span><strong>${row.tradeType || "Option-first"}</strong></div>
                  <div class="dashboard-position-metric"><span>Entry</span><strong>Review zone</strong></div>
                  <div class="dashboard-position-metric"><span>Stop</span><strong>Premium stop</strong></div>
                  <div class="dashboard-position-metric"><span>Target</span><strong>Target zone</strong></div>
                </div>

                <div class="dashboard-position-note">
                  ${obPositionSoulaana(row)}
                  <br><br>
                  <strong style="color: var(--ob-gold);">Could mess it up:</strong>
                  crowding, sector reversal, wide option spread, or ignoring Tower permission.
                </div>
              </div>
            `).join("")}
          </div>
        </div>

        <div class="dashboard-side-stack">
          <div class="ob-panel dashboard-section-panel">
            <div class="ob-label">Market Health</div>
            <div class="detail-title">${health.label}</div>
            <div class="detail-sub">${health.breadth}</div>

            <div class="dashboard-list">
              <div class="dashboard-list-item">
                <strong>Regime</strong>
                <span>${health.regime}</span>
              </div>

              <div class="dashboard-list-item">
                <strong>Caution</strong>
                <span>${health.caution}</span>
              </div>

              <div class="dashboard-list-item">
                <strong>Brightest stars</strong>
                <span>${hotSymbols.map(row => row.symbol).join(", ")}</span>
              </div>
            </div>
          </div>

          <div class="ob-panel dashboard-section-panel">
            <div class="ob-label">Dashboard Focus</div>

            <div class="dashboard-list">
              <div class="dashboard-list-item">
                <strong>1. Review active risk</strong>
                <span>Check open positions before adding anything new.</span>
              </div>

              <div class="dashboard-list-item">
                <strong>2. Inspect Market Map</strong>
                <span>Start with the brightest constellations and avoid crowded chasing.</span>
              </div>

              <div class="dashboard-list-item">
                <strong>3. Keep Manual Live locked</strong>
                <span>Only review candidates. Broker placement remains owner-controlled.</span>
              </div>
            </div>
          </div>

          <div class="ob-panel dashboard-section-panel">
            <div class="ob-label">Notifications Preview</div>

            <div class="dashboard-list">
              <div class="dashboard-alert-item">
                <strong>Manual Live candidate ready</strong>
                <span>MU CALL · Moderate risk · Review Trade Center.</span>
              </div>

              <div class="dashboard-alert-item">
                <strong>Sector crowding watch</strong>
                <span>Semiconductors are bright but need correlation review.</span>
              </div>

              <div class="dashboard-alert-item">
                <strong>Review receipt pending</strong>
                <span>One action receipt needs Review Center classification.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

document.addEventListener("DOMContentLoaded", obRenderDashboard);

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.dashboardContract) {
  window.OB_DASHBOARD_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.dashboardContract();
}

// OBSERVATORY_V23_FINAL_VISUAL_CONSISTENCY_PASS_ROOM_FLAG
window.OB_V23_ROOM_VISUAL_READY = true;

// OBSERVATORY_V25_SAFE_ENGINE_FEED_ADAPTER_ROOM_FLAG
window.OB_V25_ENGINE_FEED_READY = true;

// OBSERVATORY_V26_REAL_SNAPSHOT_DISPLAY_WIRING_ROOM_FLAG
window.OB_V26_SNAPSHOT_DISPLAY_READY = true;

// OBSERVATORY_V27_ROOM_LEVEL_REAL_DATA_POLISH_ROOM_FLAG
window.OB_V27_ROOM_DATA_POLISH_READY = true;

// OBSERVATORY_V28_CANDIDATE_SIGNAL_CARD_NORMALIZATION_ROOM_FLAG
window.OB_V28_CANDIDATE_CARDS_READY = true;
