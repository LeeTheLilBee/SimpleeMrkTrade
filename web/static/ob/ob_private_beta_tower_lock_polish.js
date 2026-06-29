// OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_POLISH_JS

(function () {
  const VERSION = "OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_POLISH";
  const ENDPOINT = "/ob/private-beta-tower-lock-polish.json";

  // SMOKE MARKERS
  // Private Beta Tower Lock Polish
  // Survey Paper beta flow
  // beta user locked states
  // Manual Live owner-only labels
  // Automated Live locked everywhere
  // Hybrid locked everywhere
  // Tower chips
  // mode chips
  // account chips
  // feedback intake visibility
  // issue triage visibility
  // fix verification visibility
  // next tester gate visibility
  // private route verification
  // no public proof leakage
  // no public access proof
  // dark UI polish
  // no broker API
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let polishState = {
    status: "booting",
    httpStatus: null,
    source: "fallback",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_004_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        feedback_intake: "/ob/private-beta-feedback-intake.json",
        issue_triage: "/ob/private-beta-issue-triage.json",
        fix_verification: "/ob/private-beta-fix-verification.json",
        next_tester_gate: "/ob/private-beta-next-tester-clearance.json",
        tower_mission_account_policy: "/tower/tower-mission-account-policy-registry-index-v451.json",
        tower_kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        tower_capital_safety: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      beta_flow: {
        label: "Standard beta flow",
        allowed_modes: ["survey", "paper"],
        visible_rooms: ["dashboard", "market_map", "symbol_page", "trade_center_preview", "review_center", "feedback"],
        locked_rooms_or_features: [
          "manual_live",
          "mission_account_capital_goals",
          "capital_deployment",
          "broker_checklist",
          "hybrid",
          "automated_live"
        ],
        message: "Beta users can observe, learn, paper trade, review, and submit feedback. Manual Live stays owner-only."
      },
      owner_flow: {
        label: "Owner operating flow",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1_preview"],
        owner_only_features: [
          "mission_accounts",
          "manual_live_level_1_operating_room",
          "receipt_review_foundation",
          "capital_safety_chips",
          "Tower clearance chips"
        ],
        message: "Owner can see the operating room and receipts framework, but OB still submits no orders."
      },
      tower_chips: [
        { chip_id: "tower_clearance", label: "Tower: clearance required", state: "required", tone: "gold" },
        { chip_id: "account_policy", label: "Account policy active", state: "active", tone: "green" },
        { chip_id: "kill_switch", label: "Kill switch board watched", state: "watched", tone: "gold" },
        { chip_id: "manual_live", label: "Manual Live owner-only", state: "owner_only", tone: "gold" },
        { chip_id: "broker_api", label: "Broker API disabled", state: "disabled", tone: "red" },
        { chip_id: "auto_execution", label: "Auto execution disabled", state: "disabled", tone: "red" }
      ],
      mode_chips: [
        { mode_id: "survey", label: "Survey", state: "open_for_beta", tone: "green" },
        { mode_id: "paper", label: "Paper", state: "open_for_beta", tone: "green" },
        { mode_id: "manual_live_level_1", label: "Manual Live L1", state: "owner_only", tone: "gold" },
        { mode_id: "hybrid", label: "Hybrid", state: "locked", tone: "red" },
        { mode_id: "automated_live", label: "Automated Live", state: "locked", tone: "red" },
        { mode_id: "live_auto", label: "Live Auto Locked", state: "locked", tone: "red" }
      ],
      account_chips: [
        { account_id: "standard_beta", label: "Beta: Paper Trading Account", state: "simple", tone: "green" },
        { account_id: "owner_mission", label: "Owner: Mission Accounts", state: "owner_only", tone: "gold" },
        { account_id: "proof_demo", label: "Proof/Demo: no real money", state: "demo_only", tone: "gold" },
        { account_id: "trust", label: "Trust: conservative", state: "protected", tone: "gold" },
        { account_id: "atm", label: "ATM: deployment watched", state: "watched", tone: "gold" },
        { account_id: "apartment", label: "Apartment: protected", state: "protected", tone: "gold" }
      ],
      private_route_verification: [
        { route: "/ob/account-experience.json", purpose: "owner/user account experience", expected_public_state: "protected_or_guarded" },
        { route: "/ob/manual-live-level-1.json", purpose: "Manual Live L1 operating room", expected_public_state: "protected_or_guarded" },
        { route: "/ob/receipts-review-foundation.json", purpose: "receipts review foundation", expected_public_state: "protected_or_guarded" },
        { route: "/ob/private-beta-feedback-intake.json", purpose: "feedback intake", expected_public_state: "protected_or_guarded" },
        { route: "/ob/private-beta-issue-triage.json", purpose: "issue triage", expected_public_state: "protected_or_guarded" },
        { route: "/ob/private-beta-fix-verification.json", purpose: "fix verification", expected_public_state: "protected_or_guarded" },
        { route: "/ob/private-beta-next-tester-clearance.json", purpose: "next tester gate", expected_public_state: "protected_or_guarded" },
        { route: "/proof", purpose: "legacy proof route", expected_public_state: "quarantined_403_or_404" },
        { route: "/premium-analysis", purpose: "legacy premium route", expected_public_state: "quarantined_403_or_404" }
      ],
      visibility_controls: [
        {
          control_id: "feedback_intake_visibility",
          label: "Feedback intake visibility",
          state: "private_beta_visible",
          detail: "Beta users can submit confusion/feedback safely."
        },
        {
          control_id: "issue_triage_visibility",
          label: "Issue triage visibility",
          state: "owner_review_visible",
          detail: "Owner can see issue priority and status."
        },
        {
          control_id: "fix_verification_visibility",
          label: "Fix verification visibility",
          state: "owner_review_visible",
          detail: "Fixes can be verified before next tester gate."
        },
        {
          control_id: "next_tester_gate_visibility",
          label: "Next tester gate visibility",
          state: "owner_review_visible",
          detail: "Next tester clearance remains Tower/owner-controlled."
        },
        {
          control_id: "manual_live_beta_lock",
          label: "Manual Live beta lock",
          state: "locked",
          detail: "Standard beta user cannot enter Manual Live."
        },
        {
          control_id: "public_proof_lock",
          label: "Public proof lock",
          state: "locked",
          detail: "No public proof leakage or public access proof."
        }
      ],
      polish_rules: [
        "Survey/Paper is the default beta user experience.",
        "Mission accounts stay owner-side.",
        "Manual Live is owner-only.",
        "Automated Live is locked everywhere.",
        "Hybrid remains locked.",
        "Tower chips explain clearance and lock state.",
        "Mode chips prevent confusion about what is simulated, paper, owner-only, or locked.",
        "Account chips prevent beta users from seeing owner mission complexity.",
        "Feedback/issue/fix/next-tester visibility is private-beta only.",
        "No public proof leakage.",
        "No broker API.",
        "No auto execution.",
        "No direct Vault upload."
      ],
      boundaries: {
        private_beta_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_public_access_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true,
        dark_ui_required: true
      }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      tower_sources: { ...(fallback.tower_sources || {}), ...(safe.tower_sources || {}) },
      beta_flow: { ...(fallback.beta_flow || {}), ...(safe.beta_flow || {}) },
      owner_flow: { ...(fallback.owner_flow || {}), ...(safe.owner_flow || {}) },
      tower_chips: Array.isArray(safe.tower_chips) ? safe.tower_chips : fallback.tower_chips,
      mode_chips: Array.isArray(safe.mode_chips) ? safe.mode_chips : fallback.mode_chips,
      account_chips: Array.isArray(safe.account_chips) ? safe.account_chips : fallback.account_chips,
      private_route_verification: Array.isArray(safe.private_route_verification) ? safe.private_route_verification : fallback.private_route_verification,
      visibility_controls: Array.isArray(safe.visibility_controls) ? safe.visibility_controls : fallback.visibility_controls,
      polish_rules: Array.isArray(safe.polish_rules) ? safe.polish_rules : fallback.polish_rules,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_public_access_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true,
        dark_ui_required: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_TOWER_LOCK_POLISH_GP004 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_tower_lock_polish_gp004: normalized,
      beta_survey_paper_only: true,
      manual_live_owner_only: true,
      no_public_proof: true,
      no_broker_api: true,
      no_auto_execution: true,
      hybrid_locked: true,
      automated_locked: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaTowerLockPolishUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchPolish() {
    polishState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      polishState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        polishState.status = "ready";
        polishState.source = normalized.source || "server";
        polishState.payload = normalized;
        polishState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        polishState.status = "guarded_fallback";
        polishState.source = "guarded_fallback";
        polishState.payload = fallback;
        polishState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      polishState.status = "error_fallback";
      polishState.source = "error_fallback";
      polishState.payload = fallback;
      polishState.fallbackActive = true;
      polishState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return polishState;
  }

  function toneClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("red") || text.includes("locked") || text.includes("disabled") || text.includes("quarantined")) return "red";
    if (text.includes("gold") || text.includes("owner") || text.includes("required") || text.includes("protected") || text.includes("watched")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-tower-lock-polish-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function chip(item) {
    return `<span class="ob-beta-tower-lock-polish-chip ${toneClass(item.tone || item.state)}">${safeText(item.label, "chip")}</span>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-beta-tower-lock-polish-row">
        <div class="ob-beta-tower-lock-polish-dot">${kind}</div>
        <div>
          <strong>${safeText(item.label || item.route || item.control_id, "Item")}</strong>
          <span>${safeText(item.state || item.expected_public_state || item.mode_id || item.account_id || item.control_id, "state")}</span>
        </div>
        <span>${safeText(item.detail || item.purpose || item.message || item.label, "Private beta control.")}</span>
        <div class="ob-beta-tower-lock-polish-status ${toneClass(item.tone || item.state || item.expected_public_state)}">${safeText(item.state || item.expected_public_state || "ready", "ready")}</div>
      </div>
    `;
  }

  function ruleRow(rule, index) {
    return `
      <div class="ob-beta-tower-lock-polish-row">
        <div class="ob-beta-tower-lock-polish-dot">✓</div>
        <div>
          <strong>Polish rule ${index + 1}</strong>
          <span>locked doctrine</span>
        </div>
        <span>${safeText(rule, "Rule")}</span>
        <div class="ob-beta-tower-lock-polish-status gold">active</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = polishState.payload || buildFallbackPayload();
    const towerChips = Array.isArray(payload.tower_chips) ? payload.tower_chips : [];
    const modeChips = Array.isArray(payload.mode_chips) ? payload.mode_chips : [];
    const accountChips = Array.isArray(payload.account_chips) ? payload.account_chips : [];
    const routes = Array.isArray(payload.private_route_verification) ? payload.private_route_verification : [];
    const visibility = Array.isArray(payload.visibility_controls) ? payload.visibility_controls : [];
    const rules = Array.isArray(payload.polish_rules) ? payload.polish_rules : [];
    const beta = payload.beta_flow || {};
    const owner = payload.owner_flow || {};

    return `
      <div class="ob-beta-tower-lock-polish-panel" id="obPrivateBetaTowerLockPolishPanel" data-ob-giant-pack-004="true">
        <div class="ob-beta-tower-lock-polish-head">
          <div>
            <div class="ob-label">OB Giant Pack 004 · Private Beta + Tower Lock Polish</div>
            <div class="ob-beta-tower-lock-polish-title">Private Beta Control Lock</div>
            <div class="ob-beta-tower-lock-polish-subtitle">
              ${safeText(polishState.status, "booting")} · Beta stays simple, owner controls stay Tower-gated, Live Auto remains locked.
            </div>
          </div>
          <div class="ob-beta-tower-lock-polish-chip-row">
            <span class="ob-beta-tower-lock-polish-chip green">Survey/Paper beta</span>
            <span class="ob-beta-tower-lock-polish-chip gold">Manual Live owner-only</span>
            <span class="ob-beta-tower-lock-polish-chip red">Hybrid locked</span>
            <span class="ob-beta-tower-lock-polish-chip red">Automated locked</span>
          </div>
        </div>

        <div class="ob-beta-tower-lock-polish-stat-grid">
          ${card("Beta", "Survey / Paper")}
          ${card("Manual Live", "Owner-only")}
          ${card("Tower chips", String(towerChips.length))}
          ${card("Private routes", String(routes.length))}
          ${card("Broker/API", "disabled")}
        </div>

        <div class="ob-beta-tower-lock-polish-grid">
          <div>
            <div class="ob-beta-tower-lock-polish-card">
              <span>Beta user locked state</span>
              <strong>${safeText(beta.label, "Standard beta flow")}</strong>
              <div class="ob-beta-tower-lock-polish-callout">
                <strong>Allowed:</strong><br>
                ${(beta.allowed_modes || []).join(" · ")}
              </div>
              <div class="ob-beta-tower-lock-polish-boundary">
                <strong>Locked:</strong><br>
                ${(beta.locked_rooms_or_features || []).join("<br>")}
              </div>
            </div>

            <div class="ob-beta-tower-lock-polish-card" style="margin-top: 11px;">
              <span>Owner operating state</span>
              <strong>${safeText(owner.label, "Owner operating flow")}</strong>
              <div class="ob-beta-tower-lock-polish-callout">
                ${safeText(owner.message, "Owner can operate only inside Tower boundaries.")}
              </div>
            </div>

            <div class="ob-beta-tower-lock-polish-card" style="margin-top: 11px;">
              <span>Tower chips</span>
              <div class="ob-beta-tower-lock-polish-chip-stack">${towerChips.map(chip).join("")}</div>
            </div>

            <div class="ob-beta-tower-lock-polish-card" style="margin-top: 11px;">
              <span>Mode chips</span>
              <div class="ob-beta-tower-lock-polish-chip-stack">${modeChips.map(chip).join("")}</div>
            </div>

            <div class="ob-beta-tower-lock-polish-card" style="margin-top: 11px;">
              <span>Account chips</span>
              <div class="ob-beta-tower-lock-polish-chip-stack">${accountChips.map(chip).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-beta-tower-lock-polish-section">
              <div class="ob-beta-tower-lock-polish-section-title">Private route verification</div>
              <div class="ob-beta-tower-lock-polish-list">${routes.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-beta-tower-lock-polish-section">
              <div class="ob-beta-tower-lock-polish-section-title">Visibility controls</div>
              <div class="ob-beta-tower-lock-polish-list">${visibility.map((item, index) => row(item, index, "V")).join("")}</div>
            </div>

            <div class="ob-beta-tower-lock-polish-section">
              <div class="ob-beta-tower-lock-polish-section-title">Polish rules</div>
              <div class="ob-beta-tower-lock-polish-list">${rules.map(ruleRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-beta-tower-lock-polish-callout">
          <strong>Source:</strong><br>
          GP004 wraps GP001 account experience, GP002 Manual Live operating room, GP003 receipts, and Tower capital safety controls into one clearer private-beta lock state.
        </div>

        <div class="ob-beta-tower-lock-polish-boundary">
          <strong>Boundary:</strong><br>
          No public proof leakage. No broker API. No auto execution. No direct Vault upload. Manual Live owner-only. Hybrid locked. Automated locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaTowerLockPolishPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const receiptsPanel = document.getElementById("obReceiptsReviewFoundationPanel");
    const manualPanel = document.getElementById("obManualLiveLevel1Panel");
    const accountPanel = document.getElementById("obAccountExperiencePanel");
    const dashboardFocus = document.querySelector("[data-ob-dashboard-focus]");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (receiptsPanel && receiptsPanel.parentNode) receiptsPanel.insertAdjacentElement("afterend", panel);
    else if (manualPanel && manualPanel.parentNode) manualPanel.insertAdjacentElement("afterend", panel);
    else if (accountPanel && accountPanel.parentNode) accountPanel.insertAdjacentElement("afterend", panel);
    else if (dashboardFocus && dashboardFocus.parentNode) dashboardFocus.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = polishState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-004-private-beta-tower-lock-polish", "ready");
    document.body.setAttribute("data-ob-beta-survey-paper-only", "true");
    document.body.setAttribute("data-ob-manual-live-owner-only", "true");
    document.body.setAttribute("data-ob-no-public-proof", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_POLISH_STATE = {
      version: VERSION,
      status: polishState.status,
      fallbackActive: polishState.fallbackActive,
      betaSurveyPaperOnly: true,
      manualLiveOwnerOnly: true,
      noPublicProof: true,
      noBrokerApi: true,
      noAutoExecution: true,
      hybridLocked: true,
      automatedLocked: true,
      liveAutoLocked: true,
      routeVerificationCount: payload.private_route_verification.length,
      visibilityControlCount: payload.visibility_controls.length
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchPolish();
    }, 3340);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_PRIVATE_BETA_TOWER_LOCK_POLISH_GP004_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return polishState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchPolish,
    renderPanel,
    setFlags
  };
})();
