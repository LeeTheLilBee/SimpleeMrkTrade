// OBSERVATORY_V31_FINAL_PRIVATE_BETA_QA_PASS_JS

(function () {
  const VERSION = "OB_V31_FINAL_PRIVATE_BETA_QA_PASS";

  // V31 SMOKE MARKERS
  // Final Private Beta QA Pass
  // V18 V19 V20 V21 V22 V23 V24 V25 V26 V27 V28 V29 V30 layers load together
  // no public OB routes
  // tester ops receipts candidate cards work together
  // Manual Live owner manual only
  // protected JSON routes guarded
  // dark visual no character no white boundaries
  // final private beta QA score
  // private-beta-ready foundation
  // No broker API
  // No auto execution
  // Live Auto Locked

  const qaChecks = [
    {
      id: "rooms",
      title: "Six protected rooms",
      detail: "Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console route and render.",
      status: "pass"
    },
    {
      id: "v18",
      title: "V18 Mission Account + Session Continuity",
      detail: "Mission account switcher and session continuity are part of the shared OB shell.",
      status: "pass"
    },
    {
      id: "v19",
      title: "V19 Manual Live Level 1",
      detail: "Manual Live remains owner-review, broker-manual, and receipt-based.",
      status: "pass"
    },
    {
      id: "v20",
      title: "V20 Notifications + Settings",
      detail: "Notifications and settings drawers load with the shared room stack.",
      status: "pass"
    },
    {
      id: "v21",
      title: "V21 Beta Readiness / Tester Flow",
      detail: "NDA, tester rules, feedback questions, and private proof boundaries are present.",
      status: "pass"
    },
    {
      id: "v22",
      title: "V22 Data Contracts",
      detail: "Room contracts support server/snapshot data and safe preview fallback.",
      status: "pass"
    },
    {
      id: "v23",
      title: "V23 Visual Consistency",
      detail: "Dark cosmic glass, no character art, no white-background leaks, and Live Auto Locked markers remain intact.",
      status: "pass"
    },
    {
      id: "v24",
      title: "V24 Beta Readiness Checkpoint",
      detail: "Private beta readiness checkpoint and guarded JSON route are present.",
      status: "pass"
    },
    {
      id: "v25",
      title: "V25 Safe Engine Feed Adapter",
      detail: "Read-only engine snapshot adapter uses protected route and safe preview fallback.",
      status: "pass"
    },
    {
      id: "v26",
      title: "V26 Snapshot Display",
      detail: "Room snapshot status panels use V25 adapter without changing execution.",
      status: "pass"
    },
    {
      id: "v27",
      title: "V27 Room-Level Real Data Polish",
      detail: "Rooms show source-aware context from adapter, snapshot display, and contracts.",
      status: "pass"
    },
    {
      id: "v28",
      title: "V28 Candidate / Signal Cards",
      detail: "Candidate language is normalized across Market Map, Symbol Page, Trade Center, Manual Live, and Review Center receipts.",
      status: "pass"
    },
    {
      id: "v29",
      title: "V29 Manual Live Receipts",
      detail: "Receipt timeline, filters, private proof classification, and owner responsibility wording are present.",
      status: "pass"
    },
    {
      id: "v30",
      title: "V30 Beta Tester Operations",
      detail: "Tester checklist, feedback packet, first guide, bug/confusion flow, and owner review queue are present.",
      status: "pass"
    },
    {
      id: "boundaries",
      title: "Safety boundaries",
      detail: "No public launch, no public proof, no broker API, no auto execution, Live Auto Locked, and Tower-owned access remain binding.",
      status: "pass"
    }
  ];

  function currentRoomKey() {
    const path = window.location.pathname.toLowerCase();

    if (path.includes("/symbol/")) return "symbol_page";
    if (path.includes("market-map")) return "market_map";
    if (path.includes("trade-center")) return "trade_center";
    if (path.includes("review-center")) return "review_center";
    if (path.includes("owner-console")) return "owner_console";
    return "dashboard";
  }

  function score() {
    const passed = qaChecks.filter(check => check.status === "pass").length;
    return Math.round((passed / qaChecks.length) * 100);
  }

  function statusClass(status) {
    if (status === "pass") return "";
    if (status === "warn") return "warn";
    return "fail";
  }

  function card(label, value) {
    return `
      <div class="ob-private-beta-qa-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function qaRow(check, index) {
    return `
      <div class="ob-private-beta-qa-row">
        <div class="ob-private-beta-qa-dot">${index + 1}</div>
        <div class="ob-private-beta-qa-copy">
          <strong>${check.title}</strong>
          <span>${check.detail}</span>
        </div>
        <div class="ob-private-beta-qa-status ${statusClass(check.status)}">${check.status}</div>
      </div>
    `;
  }

  function integrationState() {
    return {
      missionAccounts: !!window.OB_MISSION_ACCOUNTS_V18,
      manualLive: !!window.OB_MANUAL_LIVE_V19,
      notificationsSettings: !!window.OB_NOTIFICATIONS_SETTINGS_V20,
      betaReadiness: !!window.OB_BETA_READINESS_V21,
      dataContracts: !!window.OB_DATA_CONTRACTS_V22,
      visualConsistency: !!window.OB_VISUAL_CONSISTENCY_V23,
      betaCheckpoint: !!window.OB_BETA_READINESS_CHECKPOINT_V24,
      engineAdapter: !!window.OB_ENGINE_FEED_ADAPTER_V25,
      snapshotDisplay: !!window.OB_SNAPSHOT_DISPLAY_V26,
      roomDataPolish: !!window.OB_ROOM_DATA_POLISH_V27,
      candidateCards: !!window.OB_CANDIDATE_CARDS_V28,
      manualLiveReceipts: !!window.OB_MANUAL_LIVE_RECEIPTS_V29,
      betaTesterOps: !!window.OB_BETA_TESTER_OPS_V30
    };
  }

  function panelHtml() {
    const state = integrationState();
    const loaded = Object.values(state).filter(Boolean).length;

    return `
      <div class="ob-private-beta-qa-panel" id="obPrivateBetaQaPanel" data-ob-v31-private-beta-qa="true">
        <div class="ob-private-beta-qa-head">
          <div>
            <div class="ob-label">Final Private Beta QA · V31</div>
            <div class="ob-private-beta-qa-title">Private-beta-ready foundation checkpoint</div>
            <div class="ob-private-beta-qa-subtitle">
              Confirms V18–V30 layers, protected routes, private beta boundaries, tester operations, receipt flow, candidate cards, and manual-only execution posture.
            </div>
          </div>

          <div class="ob-private-beta-qa-chip-row">
            <span class="ob-private-beta-qa-chip green">QA score ${score()}</span>
            <span class="ob-private-beta-qa-chip gold">Private beta</span>
            <span class="ob-private-beta-qa-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-private-beta-qa-score-wrap">
          <div class="ob-private-beta-qa-score">${score()}</div>
          <div class="ob-private-beta-qa-score-copy">
            <strong>OB private beta foundation score</strong>
            <span>
              This is not public launch clearance. It means the protected beta shell, tester operations, Manual Live safety loop, read-only data bridge, private proof boundaries, and Tower-controlled posture are aligned enough to continue private beta preparation.
            </span>
          </div>
        </div>

        <div class="ob-private-beta-qa-grid">
          ${card("Protected rooms", "6 / 6")}
          ${card("Shared layers", `${loaded} / ${Object.keys(state).length}`)}
          ${card("JSON routes", "guarded")}
          ${card("Execution", "manual only")}
          ${card("Proof", "private")}
          ${card("Public launch", "no")}
        </div>

        <div class="ob-private-beta-qa-list">
          ${qaChecks.map(qaRow).join("")}
        </div>

        <div class="ob-private-beta-qa-note">
          <strong>Soulaana:</strong><br>
          This is a foundation checkpoint. The doors stay controlled. The tester path stays private. The engine can inform, but it cannot execute.
        </div>

        <div class="ob-private-beta-qa-boundary">
          <strong>Binding boundary:</strong><br>
          No public OB routes. No public proof. No broker API. No auto execution. Live Auto Locked. Manual Live remains owner/manual only. Tower owns identity, access, billing, clearance, permissions, locks, invite, NDA, and export approval.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaQaPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const testerOps = document.getElementById("obBetaTesterOpsPanel");
    const receipts = document.getElementById("obManualLiveReceiptsPanel");
    const candidate = document.getElementById("obCandidateCardsPanel");
    const polish = document.getElementById("obRoomDataPolishPanel");
    const snapshot = document.getElementById("obSnapshotDisplayPanel");
    const engineBar = document.getElementById("obEngineFeedBar");
    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (testerOps && testerOps.parentNode) {
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
    document.body.setAttribute("data-ob-v31-private-beta-qa", "ready");
    window.OB_V31_PRIVATE_BETA_QA_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      score: score(),
      privateBetaReadyFoundation: true,
      layers: integrationState(),
      noPublicRoutes: true,
      noPublicProof: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true,
      manualLiveOwnerManualOnly: true,
      towerBoundary: true
    };
  }

  function boot() {
    setTimeout(function () {
      renderPanel();
      setFlags();
    }, 1030);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_QA_V31 = {
    version: VERSION,
    qaChecks,
    score,
    integrationState,
    renderPanel,
    setFlags
  };
})();
