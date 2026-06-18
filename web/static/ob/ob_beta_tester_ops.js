// OBSERVATORY_V30_BETA_TESTER_OPERATIONS_PACK_JS
// RECOVERED_SAFE_V30_TESTER_OPS_ASSET

(function () {
  const VERSION = "OB_V30_BETA_TESTER_OPERATIONS_PACK";

  // V30 SMOKE MARKERS
  // Beta Tester Operations Pack
  // tester checklist
  // tester feedback packet
  // NDA invite required reminder
  // what to do first guide
  // bug confusion reporting flow
  // owner review queue for tester feedback
  // private beta boundaries
  // no public launch
  // No broker API
  // No auto execution
  // Live Auto Locked

  const testerChecklist = [
    { title: "NDA / invite required", detail: "Tester access starts only after Tower-approved invite and NDA/access rules are complete.", bucket: "access" },
    { title: "Start in Dashboard", detail: "Check mode, Tower state, mission account, snapshot source, and Soulaana guidance.", bucket: "first" },
    { title: "Read Market Map", detail: "Observe constellation counts and candidate cards without treating them as execution orders.", bucket: "first" },
    { title: "Open Symbol Page", detail: "Open one star and check movement, risk, permission, and Soulaana explanation.", bucket: "first" },
    { title: "Trade Center review only", detail: "Review candidate queue and Manual Live status. No broker API. No auto execution.", bucket: "manual" },
    { title: "Record confusion", detail: "Flag anything unclear, rushed, scary, broken, or hard to understand.", bucket: "feedback" },
    { title: "Review Center receipts", detail: "Confirm receipts are private, filtered, classified, and not public proof.", bucket: "review" },
    { title: "Owner review queue", detail: "Owner reviews tester feedback before changing permissions, copy, UI, or beta scope.", bucket: "owner" }
  ];

  const feedbackQuestions = [
    "What did you think OB wanted you to do first?",
    "Did anything feel like pressure to trade instead of review?",
    "Could you tell whether data was snapshot data or preview fallback?",
    "Could you find Tower state, Live Auto Locked, and no-execution boundaries?",
    "Which room confused you most?",
    "What felt broken, crowded, slow, or hard to trust?"
  ];

  const ownerQueueSeed = [
    { title: "Tester clarity review", room: "All rooms", priority: "high", detail: "Confirm testers understand review-first behavior." },
    { title: "Boundary comprehension", room: "Trade Center", priority: "high", detail: "Confirm testers see no broker API, no auto execution, Live Auto Locked, and owner responsibility." },
    { title: "Private proof review", room: "Review Center", priority: "medium", detail: "Confirm proof/demo and tester feedback stay private." }
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

  function renderPanel() {
    if (document.getElementById("obBetaTesterOpsPanel")) return;

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const panel = document.createElement("div");
    panel.id = "obBetaTesterOpsPanel";
    panel.setAttribute("data-ob-v30-beta-tester-ops", "true");
    panel.className = "ob-beta-ops-panel ob-panel";
    panel.innerHTML = `
      <div class="ob-beta-ops-head">
        <div>
          <div class="ob-label">Beta Tester Operations · V30</div>
          <div class="ob-beta-ops-title">Beta Tester Operations Pack</div>
          <div class="ob-beta-ops-subtitle">Private beta workflow: invite/NDA, do-first guide, feedback packet, reporting flow, and owner queue.</div>
        </div>
        <div class="ob-beta-ops-chip-row">
          <span class="ob-beta-ops-chip green">Tester checklist</span>
          <span class="ob-beta-ops-chip gold">Owner review queue</span>
          <span class="ob-beta-ops-chip red">Private beta</span>
        </div>
      </div>

      <div class="ob-beta-ops-note">
        <strong>Soulaana:</strong><br>
        Beta testers are here to help us see what is clear, confusing, and unsafe. They are not here to receive public trading signals or public proof.
      </div>

      <div class="ob-beta-ops-boundary">
        <strong>Protected boundary:</strong><br>
        NDA / invite required. No public launch. No public proof. No broker API. No auto execution. Live Auto Locked. Tower owns identity, access, billing, clearance, permissions, locks, and export approval.
      </div>
    `;

    const receiptsPanel = document.getElementById("obManualLiveReceiptsPanel");
    const candidatePanel = document.getElementById("obCandidateCardsPanel");

    if (receiptsPanel && receiptsPanel.parentNode) {
      receiptsPanel.insertAdjacentElement("afterend", panel);
    } else if (candidatePanel && candidatePanel.parentNode) {
      candidatePanel.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    document.body.setAttribute("data-ob-v30-beta-tester-ops", "ready");
    window.OB_V30_BETA_TESTER_OPS_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      checklistCount: testerChecklist.length,
      feedbackQuestions: feedbackQuestions.length,
      ownerQueue: ownerQueueSeed.length,
      ndaInviteRequired: true,
      privateBeta: true,
      noPublicLaunch: true,
      noPublicProof: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    setTimeout(function () {
      renderPanel();
      setFlags();
    }, 900);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_BETA_TESTER_OPS_V30 = {
    version: VERSION,
    testerChecklist,
    feedbackQuestions,
    ownerQueueSeed,
    renderPanel,
    setFlags
  };
})();
