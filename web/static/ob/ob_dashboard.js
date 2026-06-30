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

// OBSERVATORY_V29_MANUAL_LIVE_RECEIPTS_REVIEW_INTEGRATION_ROOM_FLAG
window.OB_V29_MANUAL_LIVE_RECEIPTS_READY = true;

// OBSERVATORY_V31_FINAL_PRIVATE_BETA_QA_PASS_ROOM_FLAG
window.OB_V31_PRIVATE_BETA_QA_READY = true;

// OBSERVATORY_V32_REAL_ENGINE_FEED_EXPANSION_READ_ONLY_ROOM_FLAG
window.OB_V32_ENGINE_FEED_EXPANSION_READY = true;

// OBSERVATORY_V34_ENGINE_FEED_TRUST_LABELS_ROOM_WARNINGS_ROOM_FLAG
window.OB_V34_ENGINE_TRUST_LABELS_READY = true;

// OBSERVATORY_V35_ENGINE_FEED_CANONICAL_ROOM_MAPPING_ROOM_FLAG
window.OB_V35_ENGINE_ROOM_MAPPING_READY = true;

// OBSERVATORY_V36_OWNER_CONSOLE_SOURCE_AUDIT_ACTION_PLAN_ROOM_FLAG
window.OB_V36_OWNER_SOURCE_AUDIT_READY = true;

// OBSERVATORY_V37_PRIVATE_BETA_LAUNCH_CONTROL_CHECKLIST_ROOM_FLAG
window.OB_V37_PRIVATE_BETA_LAUNCH_CONTROL_READY = true;

// OBSERVATORY_V38_PRIVATE_BETA_TESTER_INVITE_PACKET_BUILDER_ROOM_FLAG
window.OB_V38_PRIVATE_BETA_INVITE_PACKET_READY = true;

// OBSERVATORY_V39_TESTER_FEEDBACK_INTAKE_CONFUSION_REPORT_PACKET_ROOM_FLAG
window.OB_V39_PRIVATE_BETA_FEEDBACK_INTAKE_READY = true;

// OBSERVATORY_V40_OWNER_TESTER_FEEDBACK_REVIEW_QUEUE_ROOM_FLAG
window.OB_V40_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_READY = true;

// OBSERVATORY_V41_GUIDED_PRIVATE_BETA_SESSION_RUNBOOK_ROOM_FLAG
window.OB_V41_PRIVATE_BETA_SESSION_RUNBOOK_READY = true;

// OBSERVATORY_V42_PRIVATE_BETA_ISSUE_TRIAGE_FIX_PRIORITY_ROOM_FLAG
window.OB_V42_PRIVATE_BETA_ISSUE_TRIAGE_READY = true;

// OBSERVATORY_V43_PRIVATE_BETA_SESSION_CLOSEOUT_REPORT_ROOM_FLAG
window.OB_V43_PRIVATE_BETA_SESSION_CLOSEOUT_READY = true;

// OBSERVATORY_V44_PRIVATE_BETA_FIX_VERIFICATION_CHECKLIST_ROOM_FLAG
window.OB_V44_PRIVATE_BETA_FIX_VERIFICATION_READY = true;

// OBSERVATORY_V45_NEXT_TESTER_CLEARANCE_GATE_ROOM_FLAG
window.OB_V45_PRIVATE_BETA_NEXT_TESTER_GATE_READY = true;

// OB_GIANT_PACK_001_OWNER_USER_ACCOUNT_EXPERIENCE_ROOM_FLAG
window.OB_GIANT_PACK_001_ACCOUNT_EXPERIENCE_READY = true;

// OB_GIANT_PACK_002_MANUAL_LIVE_LEVEL_1_OPERATING_ROOM_FLAG
window.OB_GIANT_PACK_002_MANUAL_LIVE_L1_READY = true;

// OB_GIANT_PACK_003_RECEIPTS_REVIEW_CENTER_FOUNDATION_FLAG
window.OB_GIANT_PACK_003_RECEIPTS_REVIEW_READY = true;

// OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_POLISH_FLAG
window.OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_READY = true;

// OB_GIANT_PACK_005_MANUAL_LIVE_SAFETY_PREFLIGHT_GATE_FLAG
window.OB_GIANT_PACK_005_MANUAL_LIVE_PREFLIGHT_READY = true;

// OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET_FLAG
window.OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET_READY = true;

// OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_FLAG
window.OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_READY = true;

// OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_FLAG
window.OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_READY = true;

// OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT_FLAG
window.OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_READY = true;

// OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_READY = true;

// OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_FLAG
window.OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_READY = true;

// OB_GIANT_PACK_012_REHEARSAL_RECORD_PERSISTENCE_CONTRACT_FLAG
window.OB_GIANT_PACK_012_REHEARSAL_RECORD_CONTRACTS_READY = true;

// OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_FLAG
window.OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_READY = true;

// OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_FLAG
window.OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_READY = true;

// OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_FLAG
window.OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_READY = true;

// OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_WIRING_PREP_FLAG
window.OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_PREP_READY = true;

// OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER_FLAG
window.OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER_READY = true;

// OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS_FLAG
window.OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS_READY = true;

// OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE_FLAG
window.OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE_READY = true;

// OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL_FLAG
window.OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL_READY = true;

// OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_CONTRACT_FLAG
window.OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_READY = true;

// OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_FLAG
window.OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_READY = true;

// OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_FLAG
window.OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_READY = true;

// OB_GIANT_PACK_024_PRACTICE_LESSON_REVIEW_QUEUE_FLAG
window.OB_GIANT_PACK_024_PRACTICE_LESSON_REVIEW_QUEUE_READY = true;

// OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_FLAG
window.OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_READY = true;

// OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_FLAG
window.OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_READY = true;

// OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_FLAG
window.OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_READY = true;

// OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_FLAG
window.OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_READY = true;

// OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_FLAG
window.OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_READY = true;

// OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_FLAG
window.OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_READY = true;

// OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_FLAG
window.OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_READY = true;

// OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_FLAG
window.OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_READY = true;

// OB_GIANT_PACK_035_MANUAL_LIVE_OPERATOR_CONFIDENCE_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_035_MANUAL_LIVE_OPERATOR_CONFIDENCE_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_FLAG
window.OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_READY = true;

// OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_FLAG
window.OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_READY = true;

// OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_FLAG
window.OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_READY = true;
