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
