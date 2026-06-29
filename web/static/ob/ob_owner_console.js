// OBSERVATORY_OWNER_CONSOLE_V17_REAL_ROOM_JS

const OB_OWNER_TABS = [
  { key: "monitoring", label: "Monitoring" },
  { key: "analytics", label: "Analytics" },
  { key: "intelligence", label: "Intelligence" },
  { key: "diagnostics", label: "Diagnostics" },
  { key: "security", label: "Security / Audit" },
  { key: "preview", label: "Preview Controls" }
];

const OB_OWNER_ROWS = {
  monitoring: [
    {
      title: "OB room health",
      subtitle: "Dashboard, Market Map, Symbol Page, Trade Center, Review Center",
      status: "Healthy",
      metricA: "5 real rooms",
      metricB: "Nav connected",
      metricC: "Private",
      metricD: "Tower controlled",
      risk: "Low",
      action: "Keep route smoke checks active.",
      soulaana: "This is good. The rooms are becoming real, but we still do not confuse real rooms with finished product. Keep checking flow."
    },
    {
      title: "Manual Live readiness",
      subtitle: "Trade Context, Manual Queue, Review receipts",
      status: "Guarded",
      metricA: "UI ready",
      metricB: "Broker manual",
      metricC: "Receipts preview",
      metricD: "No API execution",
      risk: "Moderate",
      action: "Build full fill confirmation flow before beta.",
      soulaana: "Manual Live is not automated. Keep saying that. OB may guide, but the owner is still the hand."
    }
  ],
  analytics: [
    {
      title: "Room flow analytics",
      subtitle: "Observe → Symbol → Trade → Review",
      status: "Needs wiring",
      metricA: "Preview data",
      metricB: "Clicks later",
      metricC: "No public funnel",
      metricD: "Private beta",
      risk: "Low",
      action: "Track room transitions after beta users exist.",
      soulaana: "Do not overbuild analytics before the flow is used. First make the path clean, then measure the path."
    },
    {
      title: "Symbol engagement",
      subtitle: "Clicked stars and watched candidates",
      status: "Planned",
      metricA: "Stars",
      metricB: "Signals",
      metricC: "Watchlist",
      metricD: "Candidates",
      risk: "Low",
      action: "Connect to real event receipts later.",
      soulaana: "The user should not feel watched. The system should feel accountable."
    }
  ],
  intelligence: [
    {
      title: "Crowding and repeat behavior",
      subtitle: "Sector concentration and duplicate pressure",
      status: "Guarded",
      metricA: "Tech bright",
      metricB: "Semis active",
      metricC: "Crowding visible",
      metricD: "Tower gate",
      risk: "Correlation",
      action: "Keep anti-crowding visible across mission accounts.",
      soulaana: "A lot of green in one lane can still be danger. Blessing does not mean overload."
    },
    {
      title: "Strategy degradation watch",
      subtitle: "Edge fatigue and regime mismatch",
      status: "Planned",
      metricA: "Future",
      metricB: "Engine layer",
      metricC: "Review needed",
      metricD: "Receipts",
      risk: "Drift",
      action: "Wire after real engine state feeds the rooms.",
      soulaana: "If the edge gets tired, the system has to admit it. No silent drifting."
    }
  ],
  diagnostics: [
    {
      title: "Route coverage",
      subtitle: "Protected room routes",
      status: "Healthy",
      metricA: "/ob/dashboard",
      metricB: "/ob/market-map",
      metricC: "/ob/trade-center",
      metricD: "/ob/review-center",
      risk: "Low",
      action: "Add Owner Console route smoke to ongoing checks.",
      soulaana: "Routes are doors. Doors need locks and checks."
    },
    {
      title: "Static asset health",
      subtitle: "Shared OB theme and room JS",
      status: "Healthy",
      metricA: "Theme",
      metricB: "Nav shell",
      metricC: "Room JS",
      metricD: "Market data",
      risk: "Low",
      action: "Keep shared CSS from becoming cluttered.",
      soulaana: "One universe, separate rooms. That is the visual law."
    }
  ],
  security: [
    {
      title: "Tower boundary",
      subtitle: "Access, identity, billing, permissions",
      status: "Locked",
      metricA: "Tower owns",
      metricB: "OB displays",
      metricC: "No billing",
      metricD: "No public proof",
      risk: "Boundary",
      action: "Do not add OB billing, login, or public proof pages.",
      soulaana: "The Tower is the lock. OB does not need to pretend it owns the keys."
    },
    {
      title: "Private proof control",
      subtitle: "Proof/Demo stays internal",
      status: "Owner-only",
      metricA: "Private",
      metricB: "Redacted",
      metricC: "Review Center",
      metricD: "Tower clear",
      risk: "Exposure",
      action: "Keep proof/demo records private unless Tower explicitly clears export.",
      soulaana: "Show the lesson, not the family wallet."
    }
  ],
  preview: [
    {
      title: "Room preview controls",
      subtitle: "Owner-only UI state toggles",
      status: "Preview",
      metricA: "Theme",
      metricB: "Mode chips",
      metricC: "Room states",
      metricD: "Locked actions",
      risk: "Low",
      action: "Later add owner-only toggles for preview/demo states.",
      soulaana: "Preview controls are for building, not pretending. Keep them owner-only."
    },
    {
      title: "Beta readiness checklist",
      subtitle: "NDA, tester flow, SOP, feedback",
      status: "Needs review",
      metricA: "NDA",
      metricB: "SOP",
      metricC: "Questions",
      metricD: "Access rules",
      risk: "Beta",
      action: "Prepare beta operating docs while final rooms finish.",
      soulaana: "Beta is not public. Beta is protected learning."
    }
  ]
};

function obOwnerRows(tab) {
  return OB_OWNER_ROWS[tab] || OB_OWNER_ROWS.monitoring;
}

function obOwnerSummary() {
  return [
    { label: "Real Rooms", value: "5 / 6" },
    { label: "Tower Boundary", value: "Locked" },
    { label: "Live Auto", value: "Blocked" },
    { label: "Proof", value: "Private" },
    { label: "Manual Live", value: "Guarded" },
    { label: "Beta State", value: "Build" }
  ];
}

function obOwnerChipClass(row) {
  const status = String(row.status || "").toLowerCase();
  if (status.includes("healthy")) return "green";
  if (status.includes("locked") || status.includes("owner")) return "red";
  return "gold";
}

function obOwnerRecordAction(title, action) {
  const receipt = document.getElementById("ownerReceiptBox");
  if (!receipt) return;

  const now = new Date().toLocaleString();

  receipt.innerHTML = `
    <strong>Owner receipt updated:</strong><br>
    Console item: ${title}<br>
    Action: ${action}<br>
    Time: ${now}<br>
    Scope: Owner Console preview record.<br>
    Note: System truth remains Tower-controlled.
  `;
}

function obRenderSelectedOwner(row, tab) {
  const panel = document.getElementById("ownerDetailPanel");

  panel.innerHTML = `
    <div class="owner-detail-title">${row.title}</div>
    <div class="owner-detail-subtitle">${row.subtitle}</div>

    <div class="owner-detail-stack">
      <div class="owner-detail-card ${obOwnerChipClass(row)}">
        <span>Status</span>
        <strong>${row.status}</strong>
      </div>

      <div class="owner-detail-card gold">
        <span>Risk</span>
        <strong>${row.risk}</strong>
      </div>

      <div class="owner-detail-card">
        <span>Recommended action</span>
        <strong>${row.action}</strong>
      </div>

      <div class="owner-console-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        ${row.soulaana}
      </div>

      <div class="owner-warning-box">
        <strong>Owner boundary:</strong><br>
        This console can display system truth and preview controls, but The Tower owns identity, access, billing, permissions, locks, and emergency controls.
      </div>

      <div class="owner-action-stack">
        <button class="owner-action-button aqua" onclick="obOwnerRecordAction('${row.title}', 'Marked reviewed')">Mark reviewed</button>
        <button class="owner-action-button" onclick="obOwnerRecordAction('${row.title}', 'Add owner note')">Add owner note</button>
        <button class="owner-action-button red" onclick="obOwnerRecordAction('${row.title}', 'Escalate to Tower review')">Escalate to Tower review</button>
      </div>

      <div class="owner-receipt-box" id="ownerReceiptBox">
        <strong>No owner receipt yet.</strong><br>
        Choose an action to create an Owner Console receipt preview.
      </div>
    </div>
  `;
}

function obRenderOwnerRows(tab) {
  const rows = obOwnerRows(tab);
  const list = document.getElementById("ownerRowList");

  list.innerHTML = rows.map((row, index) => `
    <div class="owner-row ${index === 0 ? "active" : ""}" data-index="${index}">
      <div class="owner-row-top">
        <div>
          <div class="owner-row-title">${row.title}</div>
          <div class="owner-row-subtitle">${row.subtitle}</div>
        </div>

        <div class="owner-row-state">
          <span class="owner-mini-chip ${obOwnerChipClass(row)}">${row.status}</span>
          <span class="owner-mini-chip red">Owner-only</span>
        </div>
      </div>

      <div class="owner-row-metrics">
        <div class="owner-row-metric"><span>Metric A</span><strong>${row.metricA}</strong></div>
        <div class="owner-row-metric"><span>Metric B</span><strong>${row.metricB}</strong></div>
        <div class="owner-row-metric"><span>Metric C</span><strong>${row.metricC}</strong></div>
        <div class="owner-row-metric"><span>Metric D</span><strong>${row.metricD}</strong></div>
      </div>
    </div>
  `).join("");

  list.querySelectorAll(".owner-row").forEach((item) => {
    item.addEventListener("click", () => {
      list.querySelectorAll(".owner-row").forEach(row => row.classList.remove("active"));
      item.classList.add("active");
      obRenderSelectedOwner(rows[Number(item.dataset.index)], tab);
    });
  });

  if (rows[0]) {
    obRenderSelectedOwner(rows[0], tab);
  }
}

function obSetOwnerTab(tab) {
  document.querySelectorAll(".owner-tab").forEach(button => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });

  const title = document.getElementById("ownerListTitle");
  const subtitle = document.getElementById("ownerListSubtitle");

  const label = OB_OWNER_TABS.find(item => item.key === tab).label;
  title.textContent = label;
  subtitle.textContent = tab === "security"
    ? "Security/Audit shows boundaries. The Tower still owns the real locks."
    : "Click an item to review system truth, Soulaana guidance, and owner action.";

  obRenderOwnerRows(tab);
}

function obRenderOwnerConsole() {
  const mount = document.getElementById("ownerConsoleMount");

  mount.innerHTML = `
    <div class="owner-console-shell">
      <div class="ob-panel trade-control-strip">
        <div class="ob-label">Owner Snapshot</div>

        <div class="owner-status-grid">
          ${obOwnerSummary().map(item => `
            <div class="owner-status-card">
              <span>${item.label}</span>
              <strong>${item.value}</strong>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="ob-panel owner-tabs">
        ${OB_OWNER_TABS.map((tab, index) => `
          <button class="owner-tab ${index === 0 ? "active" : ""}" data-tab="${tab.key}">
            ${tab.label}
          </button>
        `).join("")}
      </div>

      <div class="owner-main-grid">
        <div class="ob-panel owner-list-panel">
          <div class="ob-label">Owner Console</div>
          <div class="detail-title" id="ownerListTitle">Monitoring</div>
          <div class="detail-sub" id="ownerListSubtitle">Click an item to review system truth, Soulaana guidance, and owner action.</div>
          <div class="owner-row-list" id="ownerRowList"></div>
        </div>

        <div class="ob-panel owner-detail-panel" id="ownerDetailPanel"></div>
      </div>
    </div>
  `;

  document.querySelectorAll(".owner-tab").forEach(button => {
    button.addEventListener("click", () => obSetOwnerTab(button.dataset.tab));
  });

  obSetOwnerTab("monitoring");
}

document.addEventListener("DOMContentLoaded", obRenderOwnerConsole);

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.ownerConsoleContract) {
  window.OB_OWNER_CONSOLE_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.ownerConsoleContract();
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
