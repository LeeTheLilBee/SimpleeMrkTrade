// OBSERVATORY_REVIEW_CENTER_V15_REAL_ROOM_JS

const OB_REVIEW_TABS = [
  { key: "performance", label: "Performance" },
  { key: "replay", label: "Trade Replay" },
  { key: "reports", label: "Reports" },
  { key: "journal", label: "Journal / Receipts" },
  { key: "proof", label: "Proof / Demo Records" }
];

const OB_REVIEW_ROWS = {
  performance: [
    {
      title: "Account Performance Snapshot",
      subtitle: "Official paper account review",
      status: "Official",
      result: "+8.4%",
      quality: "Clean",
      scope: "Paper",
      risk: "Controlled",
      lesson: "The system performed best when it respected position limits and did not over-repeat crowded tech names.",
      soulaana: "Good. But do not let a good snapshot make you arrogant. The lesson is discipline, not celebration.",
      symbol: "MU"
    },
    {
      title: "Sector Performance",
      subtitle: "Semiconductor lane led the review period",
      status: "Needs Review",
      result: "+5.1%",
      quality: "Strong but crowded",
      scope: "Sector",
      risk: "Crowding",
      lesson: "Semiconductors helped performance, but correlation risk rose when too many names leaned the same direction.",
      soulaana: "The lane was bright, yes. But bright lanes can still get crowded. We keep the blessing and check the weight.",
      symbol: "AMD"
    }
  ],
  replay: [
    {
      title: "MU Option Premium Replay",
      subtitle: "Entry, hold, and target review",
      status: "Clean replay",
      result: "Target zone",
      quality: "Good discipline",
      scope: "Trade",
      risk: "Moderate",
      lesson: "Premium-mode tracking kept the trade review focused on contract movement instead of confusing it with stock-only logic.",
      soulaana: "This is the kind of replay I like. Clear reason, clear premium path, clear boundary. Keep that.",
      symbol: "MU"
    },
    {
      title: "AMD Watch-to-Candidate Replay",
      subtitle: "Signal formed but required confirmation",
      status: "Learning",
      result: "Watched",
      quality: "Patient",
      scope: "Signal",
      risk: "Crowding",
      lesson: "The watch state prevented early action before confirmation was clean.",
      soulaana: "Patience counted as a win here. Not every win is money. Sometimes the win is not touching something too early.",
      symbol: "AMD"
    }
  ],
  reports: [
    {
      title: "Weekly OB Report",
      subtitle: "Performance, open risk, and candidate behavior",
      status: "Generated",
      result: "Ready",
      quality: "Private",
      scope: "Report",
      risk: "Low",
      lesson: "Weekly reporting should separate official, test, quarantined, and excluded records before showing totals.",
      soulaana: "Numbers without labels will lie to you. Official is official. Test is test. Keep the truth clean.",
      symbol: "NVDA"
    },
    {
      title: "Risk Discipline Report",
      subtitle: "Crowding, duplicate risk, and cooldown behavior",
      status: "Needs Review",
      result: "Guarded",
      quality: "Useful",
      scope: "Risk",
      risk: "Moderate",
      lesson: "Duplicate protection and cooldowns need to stay visible before Manual Live action.",
      soulaana: "This is one of those boring reports that saves money. Respect it.",
      symbol: "SMCI"
    }
  ],
  journal: [
    {
      title: "Decision Receipt Chain",
      subtitle: "Approved / rejected / snoozed action records",
      status: "Audit",
      result: "Receipts visible",
      quality: "Traceable",
      scope: "Receipt",
      risk: "Low",
      lesson: "Every manual action needs a receipt that separates OB recommendation, owner approval, broker fill, and monitoring state.",
      soulaana: "Receipts are not clutter. Receipts are memory. Memory keeps you from rewriting the story later.",
      symbol: "MU"
    },
    {
      title: "Quarantine Notes",
      subtitle: "Excluded rows and test artifacts",
      status: "Protected",
      result: "Separated",
      quality: "Clean",
      scope: "Journal",
      risk: "Misreporting",
      lesson: "Quarantined/test rows should never blend with official performance.",
      soulaana: "We do not let messy data sit at the dinner table with official numbers. Separate it.",
      symbol: "INTC"
    }
  ],
  proof: [
    {
      title: "Private Proof Account",
      subtitle: "Internal demo/proof records only",
      status: "Private",
      result: "Not public",
      quality: "Redacted",
      scope: "Proof",
      risk: "Privacy",
      lesson: "Proof records stay private unless The Tower explicitly clears what can be shown.",
      soulaana: "Private proof is still proof. It does not need to be public to be real.",
      symbol: "AMZN"
    },
    {
      title: "Demo Record Snapshot",
      subtitle: "Educational behavior without private exposure",
      status: "Demo",
      result: "Safe",
      quality: "Clean",
      scope: "Demo",
      risk: "Exposure",
      lesson: "Demo/proof records need redaction and separation from trust, business, and personal accounts.",
      soulaana: "Show the lesson, not the family wallet. That is the rule.",
      symbol: "MSFT"
    }
  ]
};

function obReviewRows(tab) {
  return OB_REVIEW_ROWS[tab] || OB_REVIEW_ROWS.performance;
}

function obReviewSummary() {
  return [
    { label: "Official Results", value: "+8.4%" },
    { label: "Reviewed Trades", value: "14" },
    { label: "Clean Receipts", value: "21" },
    { label: "Quarantined", value: "3" },
    { label: "Tower State", value: "Private" }
  ];
}

function obReviewChipClass(row) {
  const status = String(row.status || "").toLowerCase();
  if (status.includes("official") || status.includes("clean") || status.includes("generated")) return "green";
  if (status.includes("quarantine") || status.includes("protected")) return "red";
  return "gold";
}

function obReviewTimeline(row) {
  return [
    ["Signal / record", row.subtitle],
    ["Review truth", row.lesson],
    ["Soulaana read", row.soulaana],
    ["Next step", row.risk === "Misreporting" || row.risk === "Privacy" ? "Keep separated and gated." : "Keep reviewing with clean labels."]
  ];
}

function obOpenReviewSymbol(row) {
  if (!row.symbol) return;
  window.location.href = "/ob/symbol/" + encodeURIComponent(row.symbol);
}

function obRecordReviewAction(title, action) {
  const receipt = document.getElementById("reviewReceiptBox");
  if (!receipt) return;

  const now = new Date().toLocaleString();

  receipt.innerHTML = `
    <strong>Review receipt updated:</strong><br>
    Record: ${title}<br>
    Action: ${action}<br>
    Time: ${now}<br>
    Review state: ${action}<br>
    Note: Review Center records are private unless Tower clears export or proof use.
  `;
}

function obRenderSelectedReview(row, tab) {
  const panel = document.getElementById("reviewDetailPanel");
  const timeline = obReviewTimeline(row);

  panel.innerHTML = `
    <div class="review-detail-title">${row.title}</div>
    <div class="review-detail-subtitle">${row.subtitle}</div>

    <div class="review-detail-stack">
      <div class="review-detail-card gold">
        <span>Status</span>
        <strong>${row.status}</strong>
      </div>

      <div class="review-detail-card green">
        <span>Result / quality</span>
        <strong>${row.result} · ${row.quality}</strong>
      </div>

      <div class="review-detail-card">
        <span>Scope</span>
        <strong>${row.scope}</strong>
      </div>

      <div class="review-detail-card red">
        <span>Risk to watch</span>
        <strong>${row.risk}</strong>
      </div>

      <div class="review-soulaana-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        ${row.soulaana}
      </div>

      <div class="review-detail-card">
        <span>Replay / receipt timeline</span>
        <div class="review-timeline">
          ${timeline.map((item, index) => `
            <div class="review-timeline-item">
              <div class="review-timeline-dot">${index + 1}</div>
              <div class="review-timeline-copy">
                <strong>${item[0]}</strong>
                <p>${item[1]}</p>
              </div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="review-action-stack">
        <button class="review-action-button" onclick="obOpenReviewSymbol(${JSON.stringify(row).replace(/"/g, '&quot;')})">Open Symbol Context</button>
        <button class="review-action-button aqua" onclick="obRecordReviewAction('${row.title}', 'Marked reviewed')">Mark reviewed</button>
        <button class="review-action-button" onclick="obRecordReviewAction('${row.title}', 'Add owner note')">Add owner note</button>
        <button class="review-action-button red" onclick="obRecordReviewAction('${row.title}', 'Quarantine / exclude')">Quarantine / exclude</button>
      </div>

      <div class="review-receipt-box" id="reviewReceiptBox">
        <strong>No review receipt yet.</strong><br>
        Choose an action to create a Review Center receipt preview.
      </div>
    </div>
  `;
}

function obRenderReviewRows(tab) {
  const rows = obReviewRows(tab);
  const list = document.getElementById("reviewRowList");

  list.innerHTML = rows.map((row, index) => `
    <div class="review-row ${index === 0 ? "active" : ""}" data-index="${index}">
      <div class="review-row-top">
        <div>
          <div class="review-row-title">${row.title}</div>
          <div class="review-row-subtitle">${row.subtitle}</div>
        </div>

        <div class="review-row-state">
          <span class="review-mini-chip ${obReviewChipClass(row)}">${row.status}</span>
          <span class="review-mini-chip gold">Private</span>
        </div>
      </div>

      <div class="review-row-metrics">
        <div class="review-row-metric"><span>Result</span><strong>${row.result}</strong></div>
        <div class="review-row-metric"><span>Quality</span><strong>${row.quality}</strong></div>
        <div class="review-row-metric"><span>Scope</span><strong>${row.scope}</strong></div>
        <div class="review-row-metric"><span>Risk</span><strong>${row.risk}</strong></div>
      </div>
    </div>
  `).join("");

  list.querySelectorAll(".review-row").forEach((item) => {
    item.addEventListener("click", () => {
      list.querySelectorAll(".review-row").forEach(row => row.classList.remove("active"));
      item.classList.add("active");
      obRenderSelectedReview(rows[Number(item.dataset.index)], tab);
    });
  });

  if (rows[0]) {
    obRenderSelectedReview(rows[0], tab);
  }
}

function obSetReviewTab(tab) {
  document.querySelectorAll(".review-tab").forEach(button => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });

  const title = document.getElementById("reviewListTitle");
  const subtitle = document.getElementById("reviewListSubtitle");

  const label = OB_REVIEW_TABS.find(item => item.key === tab).label;
  title.textContent = label;

  subtitle.textContent = tab === "proof"
    ? "Private proof and demo records stay gated unless Tower clears them."
    : "Click a record to review the lesson, receipt, and next action.";

  obRenderReviewRows(tab);
}

function obRenderReviewCenter() {
  const mount = document.getElementById("reviewCenterMount");

  mount.innerHTML = `
    <div class="review-center-shell">
      <div class="ob-panel trade-control-strip">
        <div class="ob-label">Review Snapshot</div>

        <div class="review-summary-grid">
          ${obReviewSummary().map(item => `
            <div class="review-summary-card">
              <span>${item.label}</span>
              <strong>${item.value}</strong>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="ob-panel review-tabs">
        ${OB_REVIEW_TABS.map((tab, index) => `
          <button class="review-tab ${index === 0 ? "active" : ""}" data-tab="${tab.key}">
            ${tab.label}
          </button>
        `).join("")}
      </div>

      <div class="review-main-grid">
        <div class="ob-panel review-list-panel">
          <div class="ob-label">Review Center</div>
          <div class="detail-title" id="reviewListTitle">Performance</div>
          <div class="detail-sub" id="reviewListSubtitle">Click a record to review the lesson, receipt, and next action.</div>
          <div class="review-row-list" id="reviewRowList"></div>
        </div>

        <div class="ob-panel review-detail-panel" id="reviewDetailPanel"></div>
      </div>
    </div>
  `;

  document.querySelectorAll(".review-tab").forEach(button => {
    button.addEventListener("click", () => obSetReviewTab(button.dataset.tab));
  });

  obSetReviewTab("performance");
}

document.addEventListener("DOMContentLoaded", obRenderReviewCenter);

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.reviewCenterContract) {
  window.OB_REVIEW_CENTER_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.reviewCenterContract();
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
