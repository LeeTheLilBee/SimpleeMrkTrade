// OBSERVATORY_V23_FINAL_VISUAL_CONSISTENCY_PASS_JS

(function () {
  const ROOM_LABELS = {
    dashboard: "Dashboard",
    market: "Market Map",
    symbol: "Symbol Page",
    trade: "Trade Center",
    review: "Review Center",
    owner: "Owner Console"
  };

  function currentRoom() {
    const path = window.location.pathname.toLowerCase();

    if (path.includes("/symbol/")) return ROOM_LABELS.symbol;
    if (path.includes("market-map")) return ROOM_LABELS.market;
    if (path.includes("trade-center")) return ROOM_LABELS.trade;
    if (path.includes("review-center")) return ROOM_LABELS.review;
    if (path.includes("owner-console")) return ROOM_LABELS.owner;
    return ROOM_LABELS.dashboard;
  }

  function ensureUniverseClass() {
    document.body.classList.add("ob-v23-visual-lock");
    const app = document.getElementById("ob-app");
    if (app) {
      app.classList.add("ob-universe");
      app.setAttribute("data-ob-v23-visual-lock", "true");
    }
  }

  function normalizeExternalLinks() {
    document.querySelectorAll("a").forEach(link => {
      const href = link.getAttribute("href") || "";
      if (href === "#") {
        link.setAttribute("role", "button");
      }
    });
  }

  function tagButtons() {
    document.querySelectorAll("button").forEach(button => {
      if (!button.getAttribute("type")) {
        button.setAttribute("type", "button");
      }
    });
  }

  function addVisualStatus() {
    if (document.getElementById("obVisualStatus")) return;

    const node = document.createElement("div");
    node.id = "obVisualStatus";
    node.className = "ob-visual-status";

    const dataLabel = window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.dataSourceLabel
      ? window.OB_DATA_CONTRACTS_V22.dataSourceLabel()
      : "Preview fallback";

    node.innerHTML = `<strong>OB V23</strong> · ${currentRoom()} · ${dataLabel} · Tower locked`;

    document.body.appendChild(node);
  }

  function markDrawerStack() {
    document.body.setAttribute("data-ob-drawers", "notifications settings beta mission data manual");
  }

  function smokeVisualFlags() {
    window.OB_VISUAL_CONSISTENCY_V23_STATUS = {
      room: currentRoom(),
      hasApp: !!document.getElementById("ob-app"),
      hasRouteBar: !!document.getElementById("obRouteBar"),
      hasMissionBar: !!document.getElementById("obMissionBar"),
      hasDataBar: !!document.getElementById("obDataStatusBar"),
      hasNotifications: !!window.OB_NOTIFICATIONS_SETTINGS_V20,
      hasBeta: !!window.OB_BETA_READINESS_V21,
      hasContracts: !!window.OB_DATA_CONTRACTS_V22,
      towerBoundary: "Tower owns identity, access, billing, clearance, permissions, locks.",
      noPublicProof: true,
      noBrokerApi: true,
      noAutoExecution: true
    };
  }

  function boot() {
    ensureUniverseClass();
    normalizeExternalLinks();
    tagButtons();
    markDrawerStack();

    setTimeout(function () {
      addVisualStatus();
      smokeVisualFlags();
    }, 220);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_VISUAL_CONSISTENCY_V23 = {
    currentRoom,
    ensureUniverseClass,
    addVisualStatus,
    smokeVisualFlags
  };
})();
window.OB_V23_LIVE_AUTO_LOCKED_LABEL = "Live Auto Locked";
