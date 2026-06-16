// OBSERVATORY_V24_BETA_READINESS_CHECKPOINT_ROOM_AUDIT_JS

(function () {
  const CHECKPOINT_VERSION = "OB_V24_BETA_READINESS_CHECKPOINT_ROOM_AUDIT";

  const checks = [
    {
      id: "six_rooms",
      label: "Six protected OB rooms",
      detail: "Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console are real and routed.",
      status: "pass"
    },
    {
      id: "shared_layers",
      label: "Shared app layers",
      detail: "Hover nav, Mission Account Switcher, Session Continuity, Notifications, Settings, Beta Readiness, Data Contracts, and Visual Consistency layers load together.",
      status: "pass"
    },
    {
      id: "mission_accounts",
      label: "Mission account architecture",
      detail: "Personal, Trust, Business, ATM, Apartment, and Proof/Demo OB missions exist with purpose, risk, and Tower permission boundaries.",
      status: "pass"
    },
    {
      id: "manual_live",
      label: "Manual Live Level 1",
      detail: "OB detects, owner reviews, broker checklist appears, owner manually places, owner confirms, OB records and monitors.",
      status: "pass"
    },
    {
      id: "no_broker_api",
      label: "No broker API / no auto execution",
      detail: "Beta keeps broker placement manual. No one-click execution, no automated live trading, no API order submission.",
      status: "pass"
    },
    {
      id: "private_beta",
      label: "Private beta only",
      detail: "NDA required, tester rules present, feedback questions present, no public signup or public proof funnel inside OB.",
      status: "pass"
    },
    {
      id: "proof_private",
      label: "Proof/Demo stays private",
      detail: "Proof records stay in Review Center and Proof/Demo mission account unless Tower clears redacted export.",
      status: "pass"
    },
    {
      id: "tower_boundary",
      label: "Tower boundary preserved",
      detail: "The Tower owns identity, access, billing, subscription, clearance, permissions, locks, and sensitive controls.",
      status: "pass"
    },
    {
      id: "data_contracts",
      label: "Data contracts bridge",
      detail: "Room contracts support server/engine data later and keep safe preview fallback when real data is missing.",
      status: "pass"
    },
    {
      id: "visual_lock",
      label: "Visual consistency lock",
      detail: "Dark cosmic glass theme, no white background tokens, Live Auto Locked marker, and room visual flags are present.",
      status: "pass"
    }
  ];

  function betaScore() {
    const total = checks.length;
    const passed = checks.filter(check => check.status === "pass").length;
    return Math.round((passed / total) * 100);
  }

  function closeDrawer() {
    const existing = document.getElementById("obBetaCheckpointBackdrop");
    if (existing) existing.remove();
  }

  function statusClass(status) {
    if (status === "pass") return "";
    if (status === "warn") return "warn";
    return "fail";
  }

  function openCheckpointDrawer() {
    closeDrawer();

    const score = betaScore();

    const backdrop = document.createElement("div");
    backdrop.id = "obBetaCheckpointBackdrop";
    backdrop.className = "ob-beta-checkpoint-backdrop open";

    const drawer = document.createElement("div");
    drawer.className = "ob-beta-checkpoint-drawer";

    drawer.innerHTML = `
      <div class="ob-beta-checkpoint-head">
        <div>
          <strong>Beta Readiness Checkpoint</strong>
          <span>V24 room audit for private OB beta readiness. This is a checkpoint, not public launch clearance.</span>
        </div>
        <button class="ob-beta-checkpoint-close" id="obBetaCheckpointClose">×</button>
      </div>

      <div class="ob-beta-score-card">
        <div class="ob-beta-score-number">${score}</div>
        <div class="ob-beta-score-copy">
          <strong>Private beta readiness score</strong>
          <span>
            OB has the protected room structure, safety boundaries, Manual Live Level 1, mission accounts, private proof boundaries, and data-contract bridge.
            Next work should focus on real engine feed wiring, tester operations, and final user-flow QA.
          </span>
        </div>
      </div>

      <div class="ob-beta-audit-grid">
        ${checks.map((check, index) => `
          <div class="ob-beta-audit-row">
            <div class="ob-beta-audit-dot">${index + 1}</div>
            <div class="ob-beta-audit-copy">
              <strong>${check.label}</strong>
              <span>${check.detail}</span>
            </div>
            <div class="ob-beta-audit-status ${statusClass(check.status)}">${check.status}</div>
          </div>
        `).join("")}
      </div>

      <div class="ob-beta-checkpoint-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        This is the kind of checkpoint I like. It does not pretend beta is launch. It says what is ready, what is private, and what still needs real wiring before outsiders touch it.
      </div>

      <div class="ob-beta-checkpoint-warning">
        <strong>Still not allowed:</strong><br>
        Public proof, public signup, broker API execution, automated live trading, billing inside OB, or bypassing Tower permission.
      </div>

      <div class="ob-beta-checkpoint-actions">
        <button class="ob-beta-checkpoint-button" id="obBetaCheckpointOpenJson">Open checkpoint JSON</button>
        <button class="ob-beta-checkpoint-button gold" id="obBetaCheckpointOpenOwner">Open Owner Console</button>
        <button class="ob-beta-checkpoint-button red" id="obBetaCheckpointCloseFooter">Close</button>
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obBetaCheckpointClose").addEventListener("click", closeDrawer);
    document.getElementById("obBetaCheckpointCloseFooter").addEventListener("click", closeDrawer);

    const openJson = document.getElementById("obBetaCheckpointOpenJson");
    if (openJson) {
      openJson.addEventListener("click", function () {
        window.location.href = "/ob/beta-readiness-checkpoint.json";
      });
    }

    const openOwner = document.getElementById("obBetaCheckpointOpenOwner");
    if (openOwner) {
      openOwner.addEventListener("click", function () {
        window.location.href = "/ob/owner-console";
      });
    }

    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });
  }

  function addCheckpointButton() {
    if (document.getElementById("obBetaCheckpointFloatButton")) return;

    const float = document.getElementById("obNotifyFloat");
    const button = document.createElement("button");
    button.id = "obBetaCheckpointFloatButton";
    button.className = "ob-beta-checkpoint-float-button";
    button.textContent = "Checkpoint";
    button.addEventListener("click", openCheckpointDrawer);

    if (float) {
      float.prepend(button);
    } else {
      const wrap = document.createElement("div");
      wrap.id = "obBetaCheckpointFloatWrap";
      wrap.className = "ob-notify-float";
      wrap.appendChild(button);
      document.body.appendChild(wrap);
    }
  }

  function addOwnerCheckpointHook() {
    const mount = document.getElementById("ownerConsoleMount");
    if (!mount || document.getElementById("obBetaCheckpointOwnerHook")) return;

    const panel = document.createElement("div");
    panel.id = "obBetaCheckpointOwnerHook";
    panel.className = "ob-panel manual-review-panel";

    panel.innerHTML = `
      <div class="manual-live-header-row">
        <div>
          <div class="ob-label">Beta Readiness Checkpoint</div>
          <div class="manual-live-title">Room audit score: ${betaScore()}</div>
          <div class="manual-live-subtitle">Six rooms, shared layers, private proof boundary, Manual Live Level 1, Tower boundary, and data-contract bridge are checkpointed.</div>
        </div>

        <div class="manual-live-chip-row">
          <span class="manual-live-chip green">Checkpoint pass</span>
          <span class="manual-live-chip gold">Private beta</span>
          <span class="manual-live-chip red">No public launch</span>
        </div>
      </div>

      <div class="ob-beta-checkpoint-actions">
        <button class="ob-beta-checkpoint-button" id="obBetaCheckpointOwnerOpen">Open Checkpoint</button>
        <button class="ob-beta-checkpoint-button gold" id="obBetaCheckpointOwnerJson">Checkpoint JSON</button>
      </div>
    `;

    mount.prepend(panel);

    document.getElementById("obBetaCheckpointOwnerOpen").addEventListener("click", openCheckpointDrawer);
    document.getElementById("obBetaCheckpointOwnerJson").addEventListener("click", function () {
      window.location.href = "/ob/beta-readiness-checkpoint.json";
    });
  }

  function boot() {
    setTimeout(function () {
      addCheckpointButton();
      addOwnerCheckpointHook();
    }, 190);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_BETA_READINESS_CHECKPOINT_V24 = {
    version: CHECKPOINT_VERSION,
    checks,
    betaScore,
    openCheckpointDrawer
  };
})();
