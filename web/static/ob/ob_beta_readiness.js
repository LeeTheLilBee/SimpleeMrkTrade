// OBSERVATORY_V21_BETA_READINESS_TESTER_FLOW_JS

(function () {
  const BETA_KEY = "ob.v21.betaReadiness";
  const FEEDBACK_KEY = "ob.v21.betaFeedbackDrafts";

  const betaState = {
    access: "Invite-only",
    nda: "Required before access",
    mode: "Paper / Manual Live Level 1",
    proof: "Private proof only",
    billing: "Tower-owned, not OB-owned",
    broker: "Manual broker placement only"
  };

  const betaTabs = [
    { key: "checklist", label: "Beta Checklist" },
    { key: "tester", label: "Tester Rules" },
    { key: "sop", label: "Manual Live SOP" },
    { key: "feedback", label: "Feedback Questions" },
    { key: "proof", label: "Private Proof" },
    { key: "tower", label: "Tower Boundary" }
  ];

  const betaChecklist = [
    ["NDA required", "Tester must complete NDA/access rules before entering OB."],
    ["Private access only", "No public signup, no public proof, no public marketing route inside OB."],
    ["Mode is limited", "Beta starts with Paper and Manual Live Level 1 review behavior only."],
    ["Manual broker flow", "OB gives checklist. Owner/tester manually places or does not place at broker."],
    ["Receipts required", "Approve, reject, snooze, fill confirmation, and review actions should create receipts."],
    ["Feedback required", "Tester should report clarity, confusion, trust, and action-pressure concerns."]
  ];

  const testerRules = [
    ["No copying private voice", "Tester may not copy Soulaana, private OB language, strategy logic, or internal layouts."],
    ["No financial promises", "Tester must not treat OB as guaranteed profit or investment advice."],
    ["No public sharing", "Screenshots, proof, reports, and demo records stay private unless Tower clears them."],
    ["No credential sharing", "Invite access is personal and cannot be shared."],
    ["No broker automation", "Beta does not include broker API, one-click execution, or automated live trading."],
    ["Report confusion", "If a card feels unclear or emotionally pressuring, tester must flag it."]
  ];

  const manualLiveSOP = [
    ["OB detects", "OB identifies a candidate and creates a complete review card."],
    ["Tower checks", "The Tower permission state stays visible. Live Automated remains locked."],
    ["Tester reviews", "Tester reads Trade Center card, Soulaana note, risk, and broker checklist."],
    ["Tester decides", "Approve for manual placement, reject, or snooze / watch."],
    ["Broker is manual", "Tester manually enters the trade at broker if approved and appropriate."],
    ["OB records", "Tester confirms filled, submitted, not placed, changed, or canceled."],
    ["OB monitors", "If filled, OB tracks monitoring state and exit review receipts."],
    ["Review Center learns", "Receipts stay private and get classified in Review Center."]
  ];

  const feedbackQuestions = [
    {
      id: "clarity",
      label: "Could you tell what OB wanted you to review, without feeling rushed?",
      type: "select",
      options: ["Yes, clear", "Mostly clear", "Confusing", "Felt rushed"]
    },
    {
      id: "soulaana",
      label: "Did Soulaana explain the symbol/trade in a way that helped you understand what was going on?",
      type: "select",
      options: ["Very helpful", "Helpful", "Too much", "Not enough", "Confusing"]
    },
    {
      id: "risk",
      label: "Could you understand the risk, blocker, and Tower permission state?",
      type: "select",
      options: ["Yes", "Somewhat", "No", "I missed it"]
    },
    {
      id: "manual",
      label: "Did the Manual Live process make it clear that you must place trades manually at the broker?",
      type: "select",
      options: ["Yes", "Somewhat", "No", "I thought OB was executing"]
    },
    {
      id: "notes",
      label: "What confused you, what felt strong, and what should be improved before more testers enter?",
      type: "textarea"
    }
  ];

  function loadBetaStatus() {
    try {
      return JSON.parse(localStorage.getItem(BETA_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function saveBetaStatus(next) {
    localStorage.setItem(BETA_KEY, JSON.stringify({ ...loadBetaStatus(), ...next }));
  }

  function loadFeedbackDrafts() {
    try {
      return JSON.parse(localStorage.getItem(FEEDBACK_KEY) || "[]");
    } catch (error) {
      return [];
    }
  }

  function saveFeedbackDraft(draft) {
    const drafts = loadFeedbackDrafts();
    drafts.push({
      ...draft,
      time: new Date().toLocaleString(),
      private: true,
      towerBoundary: "Feedback is private and beta-gated."
    });
    localStorage.setItem(FEEDBACK_KEY, JSON.stringify(drafts.slice(-20)));
  }

  function closeDrawer() {
    const existing = document.getElementById("obBetaDrawerBackdrop");
    if (existing) existing.remove();
  }

  function statusCards() {
    return `
      <div class="ob-beta-status-grid">
        <div class="ob-beta-status-card"><span>Access</span><strong>${betaState.access}</strong></div>
        <div class="ob-beta-status-card"><span>NDA</span><strong>${betaState.nda}</strong></div>
        <div class="ob-beta-status-card"><span>Mode</span><strong>${betaState.mode}</strong></div>
        <div class="ob-beta-status-card"><span>Execution</span><strong>${betaState.broker}</strong></div>
      </div>
    `;
  }

  function listPanel(items) {
    return `
      <div class="ob-beta-list">
        ${items.map((item, index) => `
          <div class="ob-beta-list-item">
            <div class="ob-beta-list-dot">${index + 1}</div>
            <div class="ob-beta-list-copy">
              <strong>${item[0]}</strong>
              <span>${item[1]}</span>
            </div>
          </div>
        `).join("")}
      </div>
    `;
  }

  function feedbackPanel() {
    return `
      <div class="ob-beta-panel gold">
        <span>Feedback purpose</span>
        <strong>Beta feedback should tell us whether OB is clear, safe, useful, and non-pressuring before more testers enter.</strong>
      </div>

      <div class="ob-beta-question-list">
        ${feedbackQuestions.map(question => {
          if (question.type === "textarea") {
            return `
              <div class="ob-beta-question">
                <label for="obBetaFeedback_${question.id}">${question.label}</label>
                <textarea id="obBetaFeedback_${question.id}"></textarea>
              </div>
            `;
          }

          return `
            <div class="ob-beta-question">
              <label for="obBetaFeedback_${question.id}">${question.label}</label>
              <select id="obBetaFeedback_${question.id}">
                ${question.options.map(option => `<option value="${option}">${option}</option>`).join("")}
              </select>
            </div>
          `;
        }).join("")}
      </div>

      <div class="ob-beta-action-row">
        <button class="ob-beta-button" id="obBetaSaveFeedback">Save private feedback draft</button>
        <button class="ob-beta-button gold" id="obBetaViewFeedbackDrafts">View saved drafts</button>
      </div>

      <div class="ob-beta-receipt" id="obBetaFeedbackReceipt">
        <strong>No feedback draft saved yet.</strong><br>
        Feedback drafts are local/private placeholders for beta planning.
      </div>
    `;
  }

  function proofPanel() {
    return `
      <div class="ob-beta-panel red">
        <span>Private proof boundary</span>
        <strong>Proof/Demo records stay private. OB does not expose trust, personal, business, ATM, apartment, or beta tester data in public proof.</strong>
      </div>

      ${listPanel([
        ["Public proof is cut", "No public proof route, public performance page, public premium teaser, or public demo funnel inside OB."],
        ["Review Center holds proof", "Proof/Demo records belong in Review Center as private/internal records."],
        ["Tower clears export", "Any export, screenshot, or proof use requires Tower clearance and redaction."],
        ["Demo account stays clean", "Proof/Demo OB Account should show behavior without exposing private money or identities."]
      ])}
    `;
  }

  function towerPanel() {
    return `
      <div class="ob-beta-panel red">
        <span>Tower owns the gates</span>
        <strong>OB can show access status, locked states, and safe messages. The Tower owns login, signup/invite acceptance, billing, plan/access management, clearance, permissions, and emergency controls.</strong>
      </div>

      ${listPanel([
        ["No public signup in OB", "Invite acceptance belongs to The Tower, not OB."],
        ["No billing in OB", "Checkout, subscription, upgrade, payment, and customer portal are Tower-owned or SimpleePay-owned flows."],
        ["No Live Automated beta", "Live Automated remains locked and non-public."],
        ["Locked-content surfaces only", "OB can say access required and route back to Tower, but cannot own the gate."]
      ])}
    `;
  }

  function sopPanel() {
    return `
      <div class="ob-beta-panel green">
        <span>Manual Live Level 1 rule</span>
        <strong>OB is the brain. The Tower is the lock. Soulaana is the guidance. The tester/owner is the hand. The broker is the execution venue. OB remembers everything.</strong>
      </div>

      ${listPanel(manualLiveSOP)}
    `;
  }

  function testerPanel() {
    return `
      <div class="ob-beta-panel gold">
        <span>Tester rule</span>
        <strong>Beta testers are invited to help improve clarity and safety. They are not being invited into a public trading product.</strong>
      </div>

      ${listPanel(testerRules)}
    `;
  }

  function checklistPanel() {
    return `
      <div class="ob-beta-panel green">
        <span>Beta readiness</span>
        <strong>The beta version proves the private decision system, not broker automation or public proof.</strong>
      </div>

      ${listPanel(betaChecklist)}
    `;
  }

  function renderTab(tab) {
    const mount = document.getElementById("obBetaPanelMount");
    if (!mount) return;

    if (tab === "checklist") mount.innerHTML = checklistPanel();
    if (tab === "tester") mount.innerHTML = testerPanel();
    if (tab === "sop") mount.innerHTML = sopPanel();
    if (tab === "feedback") mount.innerHTML = feedbackPanel();
    if (tab === "proof") mount.innerHTML = proofPanel();
    if (tab === "tower") mount.innerHTML = towerPanel();

    document.querySelectorAll(".ob-beta-tab").forEach(button => {
      button.classList.toggle("active", button.dataset.betaTab === tab);
    });

    wireFeedbackButtons();
  }

  function wireFeedbackButtons() {
    const save = document.getElementById("obBetaSaveFeedback");
    if (save) {
      save.addEventListener("click", function () {
        const draft = {};
        feedbackQuestions.forEach(question => {
          const input = document.getElementById("obBetaFeedback_" + question.id);
          draft[question.id] = input ? input.value : "";
        });

        saveFeedbackDraft(draft);
        saveBetaStatus({ feedbackDraftSaved: true });

        const receipt = document.getElementById("obBetaFeedbackReceipt");
        if (receipt) {
          receipt.innerHTML = `
            <strong>Private feedback draft saved:</strong><br>
            ${new Date().toLocaleString()}<br>
            Stored locally for beta planning. Not exported. Not public.
          `;
        }
      });
    }

    const view = document.getElementById("obBetaViewFeedbackDrafts");
    if (view) {
      view.addEventListener("click", function () {
        const drafts = loadFeedbackDrafts();
        const receipt = document.getElementById("obBetaFeedbackReceipt");
        if (!receipt) return;

        receipt.innerHTML = drafts.length
          ? `<strong>Saved private feedback drafts:</strong><br>${drafts.map((draft, index) => `${index + 1}. ${draft.time} · Clarity: ${draft.clarity || "n/a"} · Manual: ${draft.manual || "n/a"}`).join("<br>")}`
          : `<strong>No feedback drafts saved yet.</strong><br>Complete the feedback questions and save a draft.`;
      });
    }
  }

  function openBetaDrawer(defaultTab) {
    closeDrawer();

    const backdrop = document.createElement("div");
    backdrop.id = "obBetaDrawerBackdrop";
    backdrop.className = "ob-beta-drawer-backdrop open";

    const drawer = document.createElement("div");
    drawer.className = "ob-beta-drawer";

    drawer.innerHTML = `
      <div class="ob-beta-head">
        <div>
          <strong>Private Beta Readiness</strong>
          <span>NDA required, invite-only, Manual Live Level 1, private proof, Tower-controlled access.</span>
        </div>
        <button class="ob-beta-close" id="obBetaClose">×</button>
      </div>

      ${statusCards()}

      <div class="ob-beta-guard-card">
        <strong>Beta boundary:</strong><br>
        This is not public launch, not broker API execution, not automated live trading, and not a public proof funnel.
      </div>

      <div class="ob-beta-tabs">
        ${betaTabs.map(tab => `
          <button class="ob-beta-tab" data-beta-tab="${tab.key}">${tab.label}</button>
        `).join("")}
      </div>

      <div id="obBetaPanelMount"></div>

      <div class="ob-beta-action-row">
        <button class="ob-beta-button gold" id="obBetaOpenTrade">Open Trade Center</button>
        <button class="ob-beta-button" id="obBetaOpenReview">Open Review Center</button>
        <button class="ob-beta-button red" id="obBetaCloseFooter">Close</button>
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obBetaClose").addEventListener("click", closeDrawer);
    document.getElementById("obBetaCloseFooter").addEventListener("click", closeDrawer);
    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });

    document.querySelectorAll(".ob-beta-tab").forEach(button => {
      button.addEventListener("click", function () {
        renderTab(this.dataset.betaTab);
      });
    });

    const openTrade = document.getElementById("obBetaOpenTrade");
    if (openTrade) {
      openTrade.addEventListener("click", function () {
        window.location.href = "/ob/trade-center";
      });
    }

    const openReview = document.getElementById("obBetaOpenReview");
    if (openReview) {
      openReview.addEventListener("click", function () {
        window.location.href = "/ob/review-center";
      });
    }

    renderTab(defaultTab || "checklist");
  }

  function buildBetaButton() {
    if (document.getElementById("obBetaFloatButton")) return;

    const float = document.getElementById("obNotifyFloat");
    const button = document.createElement("button");
    button.id = "obBetaFloatButton";
    button.className = "ob-beta-float-button";
    button.textContent = "Beta";
    button.addEventListener("click", function () {
      openBetaDrawer("checklist");
    });

    if (float) {
      float.prepend(button);
    } else {
      const wrap = document.createElement("div");
      wrap.id = "obBetaFloatWrap";
      wrap.className = "ob-notify-float";
      wrap.appendChild(button);
      document.body.appendChild(wrap);
    }
  }

  function addOwnerConsoleBetaHook() {
    const mount = document.getElementById("ownerConsoleMount");
    if (!mount || document.getElementById("obBetaOwnerHook")) return;

    const panel = document.createElement("div");
    panel.id = "obBetaOwnerHook";
    panel.className = "ob-panel manual-review-panel";

    panel.innerHTML = `
      <div class="manual-live-header-row">
        <div>
          <div class="ob-label">Beta Readiness</div>
          <div class="manual-live-title">Private tester flow</div>
          <div class="manual-live-subtitle">NDA, tester rules, Manual Live SOP, feedback questions, private proof, and Tower boundary are consolidated here.</div>
        </div>

        <div class="manual-live-chip-row">
          <span class="manual-live-chip gold">Invite-only</span>
          <span class="manual-live-chip green">SOP ready</span>
          <span class="manual-live-chip red">No public proof</span>
        </div>
      </div>

      <div class="ob-beta-action-row">
        <button class="ob-beta-button" id="obBetaOwnerOpen">Open Beta Readiness</button>
        <button class="ob-beta-button gold" id="obBetaOwnerFeedback">Feedback Questions</button>
        <button class="ob-beta-button red" id="obBetaOwnerTower">Tower Boundary</button>
      </div>
    `;

    mount.prepend(panel);

    document.getElementById("obBetaOwnerOpen").addEventListener("click", function () {
      openBetaDrawer("checklist");
    });

    document.getElementById("obBetaOwnerFeedback").addEventListener("click", function () {
      openBetaDrawer("feedback");
    });

    document.getElementById("obBetaOwnerTower").addEventListener("click", function () {
      openBetaDrawer("tower");
    });
  }

  function boot() {
    setTimeout(function () {
      buildBetaButton();
      addOwnerConsoleBetaHook();
    }, 140);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_BETA_READINESS_V21 = {
    betaState,
    betaChecklist,
    testerRules,
    manualLiveSOP,
    feedbackQuestions,
    openBetaDrawer,
    loadBetaStatus,
    saveBetaStatus,
    loadFeedbackDrafts
  };
})();
