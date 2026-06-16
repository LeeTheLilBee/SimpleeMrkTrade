// OBSERVATORY_V18_MISSION_ACCOUNT_SWITCHER_SESSION_CONTINUITY_JS

(function () {
  const MISSION_KEY = "ob.selectedMissionAccount.v18";

  const missionAccounts = [
    {
      id: "personal",
      label: "Personal OB",
      title: "Personal OB Account",
      purpose: "Owner learning, personal capital growth, and controlled Paper / Manual Live review.",
      entity: "Solice / Personal",
      risk: "Moderate guarded",
      mode: "Paper / Manual guarded",
      goal: "Build skill, proof, and personal capital without mixing business funds.",
      allowed: "Options-first review, stock fallback, owner testing, paper/manual review.",
      blocked: "Business spending, trust misuse, reckless overconcentration, Live Automated.",
      approvals: "Owner review required before manual placement."
    },
    {
      id: "trust",
      label: "Trust OB",
      title: "Trust OB Account",
      purpose: "Long-term family/trust capital stewardship with stronger protection.",
      entity: "Simplee Bowdre Living Irrevocable Trust",
      risk: "Conservative protected",
      mode: "Paper only / Manual guarded later",
      goal: "Protect principal, build family capital, avoid reckless options behavior.",
      allowed: "Conservative review, strict reserves, lower exposure, receipts.",
      blocked: "High-risk trades, personal spending, trust misuse, duplicate crowding.",
      approvals: "Owner/Tower approval and stronger review required."
    },
    {
      id: "business",
      label: "Simplee World / Business OB",
      title: "Simplee World / Business OB Account",
      purpose: "Parent company capital growth and future venture funding readiness.",
      entity: "Simplee World / Business lane",
      risk: "Growth controlled",
      mode: "Paper / Manual guarded",
      goal: "Build business expansion capital with clean receipts.",
      allowed: "Growth setups, business milestone tracking, review receipts.",
      blocked: "Personal mixing, unclear withdrawals, ecosystem overexposure.",
      approvals: "Owner review and business-purpose receipt required."
    },
    {
      id: "atm",
      label: "SimpleeOnTheGo / ATM OB",
      title: "SimpleeOnTheGo ATM Growth Account",
      purpose: "Build capital for ATM route acquisition, vault cash, repairs, and expansion.",
      entity: "SimpleeOnTheGo LLC lane",
      risk: "Moderate conservative",
      mode: "Paper / Manual guarded",
      goal: "$10k first acquisition reserve, then protect operating capital.",
      allowed: "Milestone-driven growth, acquisition reserve tracking, ATM-only withdrawals.",
      blocked: "Personal spending, apartment funding, trust misuse, Live Automated.",
      approvals: "Owner approval plus ATM-purpose receipt required."
    },
    {
      id: "apartment",
      label: "SimpleeProperty / Apartment OB",
      title: "SimpleeProperty Apartment Reserve Account",
      purpose: "Build and protect apartment acquisition reserves for 4–5 building target.",
      entity: "SimpleeProperty lane",
      risk: "Conservative reserve",
      mode: "Paper / Watch-heavy",
      goal: "Down payment, inspections, earnest money, closing cost, repair reserve readiness.",
      allowed: "Capital preservation, low drawdown rules, reserve-first review.",
      blocked: "High-risk options, gambling behavior, non-property withdrawals.",
      approvals: "Owner approval and property acquisition purpose required."
    },
    {
      id: "proof",
      label: "Proof / Demo OB",
      title: "Proof / Demo OB Account",
      purpose: "Private beta proof and educational records without exposing private accounts.",
      entity: "Internal proof lane",
      risk: "Clean / redacted",
      mode: "Paper / Demo",
      goal: "Show system behavior safely while keeping private data hidden.",
      allowed: "Demo records, redacted screenshots, educational receipts.",
      blocked: "Private financial exposure, public proof without Tower clearance.",
      approvals: "Tower clearance required before export or public use."
    }
  ];

  const sessionContinuity = [
    {
      title: "Six protected rooms are real",
      detail: "Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console are now live as protected OB rooms."
    },
    {
      title: "Current layer: Mission Accounts",
      detail: "OB accounts are missions, not just balances. The selected account changes how the system should frame risk, purpose, and action."
    },
    {
      title: "Manual Live remains Level 1",
      detail: "OB can detect, explain, prepare, and record. Owner still places trades manually at the broker."
    },
    {
      title: "Tower boundary remains intact",
      detail: "The Tower owns identity, access, billing, clearance, permissions, locks, and sensitive controls."
    },
    {
      title: "Next likely build",
      detail: "Manual Live Level 1 full loop: approval receipt, broker checklist, fill confirmation, monitoring, and Review Center receipt."
    }
  ];

  function getMissionById(id) {
    return missionAccounts.find(account => account.id === id) || missionAccounts[0];
  }

  function getSelectedMission() {
    const stored = localStorage.getItem(MISSION_KEY) || "personal";
    return getMissionById(stored);
  }

  function setSelectedMission(id) {
    const mission = getMissionById(id);
    localStorage.setItem(MISSION_KEY, mission.id);
    document.body.setAttribute("data-ob-mission", mission.id);
    updateMissionUI(mission);
  }

  function createChip(text, cls) {
    return `<span class="ob-mission-pill ${cls || ""}">${text}</span>`;
  }

  function missionDetailCard(label, value) {
    return `
      <div class="ob-mission-detail-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function renderMissionDrawer(mission) {
    closeMissionDrawer();

    const backdrop = document.createElement("div");
    backdrop.className = "ob-mission-drawer-backdrop open";
    backdrop.id = "obMissionDrawerBackdrop";

    const drawer = document.createElement("div");
    drawer.className = "ob-mission-drawer";
    drawer.id = "obMissionDrawer";

    drawer.innerHTML = `
      <div class="ob-mission-drawer-title">
        <div>
          <strong>${mission.title}</strong>
          <span>${mission.purpose}</span>
        </div>
        <button class="ob-mission-close" id="obMissionCloseButton">×</button>
      </div>

      <div class="ob-mission-detail-grid">
        ${missionDetailCard("Entity / lane", mission.entity)}
        ${missionDetailCard("Risk profile", mission.risk)}
        ${missionDetailCard("Allowed mode", mission.mode)}
        ${missionDetailCard("Capital goal", mission.goal)}
        ${missionDetailCard("Allowed behavior", mission.allowed)}
        ${missionDetailCard("Blocked behavior", mission.blocked)}
        ${missionDetailCard("Approval rule", mission.approvals)}
        ${missionDetailCard("Tower state", "Tower controls permission and clearance")}
      </div>

      <div class="ob-mission-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        This account has a job. We do not treat trust money like personal money, ATM money like apartment money, or proof money like private money. Pick the mission before you read the signal.
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obMissionCloseButton").addEventListener("click", closeMissionDrawer);
    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeMissionDrawer();
    });
  }

  function renderSessionDrawer() {
    closeMissionDrawer();

    const backdrop = document.createElement("div");
    backdrop.className = "ob-mission-drawer-backdrop open";
    backdrop.id = "obMissionDrawerBackdrop";

    const drawer = document.createElement("div");
    drawer.className = "ob-mission-drawer";
    drawer.id = "obMissionDrawer";

    drawer.innerHTML = `
      <div class="ob-mission-drawer-title">
        <div>
          <strong>Session Continuity</strong>
          <span>Consolidated build state across OB rooms and current execution lane.</span>
        </div>
        <button class="ob-mission-close" id="obMissionCloseButton">×</button>
      </div>

      <div class="ob-session-list">
        ${sessionContinuity.map((item, index) => `
          <div class="ob-session-item">
            <div class="ob-session-dot">${index + 1}</div>
            <div class="ob-session-copy">
              <strong>${item.title}</strong>
              <span>${item.detail}</span>
            </div>
          </div>
        `).join("")}
      </div>

      <div class="ob-mission-note">
        <strong style="color: var(--ob-gold);">Current reminder:</strong><br>
        Build lane stays inside Colab and the SimpleeMrkTrade repo. No Tower file changes unless the task is explicitly Tower work. Keep OB private, clean, and Tower-controlled.
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obMissionCloseButton").addEventListener("click", closeMissionDrawer);
    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeMissionDrawer();
    });
  }

  function closeMissionDrawer() {
    const existing = document.getElementById("obMissionDrawerBackdrop");
    if (existing) existing.remove();
  }

  function updateMissionUI(mission) {
    const select = document.getElementById("obMissionSelect");
    const title = document.getElementById("obMissionTitle");
    const purpose = document.getElementById("obMissionPurpose");
    const chips = document.getElementById("obMissionChips");

    if (select) select.value = mission.id;
    if (title) title.textContent = mission.title;
    if (purpose) purpose.textContent = mission.purpose;

    if (chips) {
      chips.innerHTML = [
        createChip(mission.risk, mission.risk.toLowerCase().includes("conservative") ? "gold" : "green"),
        createChip(mission.mode, "gold"),
        createChip("Live Auto Locked", "red")
      ].join("");
    }

    document.body.setAttribute("data-ob-mission", mission.id);
  }

  function buildMissionBar() {
    if (document.getElementById("obMissionBar")) return;

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const bar = document.createElement("div");
    bar.className = "ob-mission-bar";
    bar.id = "obMissionBar";

    bar.innerHTML = `
      <div class="ob-mission-select-wrap">
        <label class="ob-mission-select-label" for="obMissionSelect">Current Mission Account</label>
        <select class="ob-mission-select" id="obMissionSelect">
          ${missionAccounts.map(account => `
            <option value="${account.id}">${account.label}</option>
          `).join("")}
        </select>
      </div>

      <div class="ob-mission-summary">
        <div class="ob-mission-title-row">
          <div class="ob-mission-title" id="obMissionTitle">Mission Account</div>
          <div id="obMissionChips"></div>
        </div>
        <div class="ob-mission-purpose" id="obMissionPurpose"></div>
      </div>

      <div class="ob-mission-actions">
        <button class="ob-mission-button" id="obMissionDetailsButton">Mission Rules</button>
        <button class="ob-mission-button" id="obSessionContinuityButton">Session Continuity</button>
        <button class="ob-mission-button red" type="button">Tower Controls Permission</button>
      </div>
    `;

    const routeBar = document.getElementById("obRouteBar");
    if (routeBar && routeBar.parentNode) {
      routeBar.insertAdjacentElement("afterend", bar);
    } else {
      layer.prepend(bar);
    }

    const selected = getSelectedMission();
    updateMissionUI(selected);

    document.getElementById("obMissionSelect").addEventListener("change", function () {
      setSelectedMission(this.value);
    });

    document.getElementById("obMissionDetailsButton").addEventListener("click", function () {
      renderMissionDrawer(getSelectedMission());
    });

    document.getElementById("obSessionContinuityButton").addEventListener("click", renderSessionDrawer);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(buildMissionBar, 0);
  });

  window.OB_MISSION_ACCOUNTS_V18 = {
    missionAccounts,
    sessionContinuity,
    getSelectedMission,
    setSelectedMission
  };
})();
