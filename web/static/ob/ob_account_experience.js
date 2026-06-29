// OB_GIANT_PACK_001_OWNER_USER_ACCOUNT_EXPERIENCE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_001_OWNER_USER_ACCOUNT_EXPERIENCE";
  const ENDPOINT = "/ob/account-experience.json";

  // SMOKE MARKERS
  // Owner mission accounts
  // Standard beta user simple account
  // Advanced account placeholder
  // Tower account experience permissions
  // mission_account_enabled
  // optional_goal_accounts
  // manual_live_owner_only
  // Manual Live owner-only
  // Hybrid locked
  // Automated locked
  // no public signup
  // no broker API
  // no auto execution
  // Live Auto Locked

  let accountState = {
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

  function ownerMissionAccounts() {
    return [
      {
        account_id: "ob_acct_trust",
        label: "Trust OB Account",
        lane: "Trust",
        purpose: "Protect and grow trust capital.",
        risk_profile: "lowest",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1"],
        capital_goal: "First funding lane; preserve protected floor before dispersal.",
        deployment_rules: "Tower approval required before trust withdrawals or mission dispersal.",
        tower_clearance: "required",
        current_status: "policy-ready",
        next_action: "Use only after Tower account policy confirms protected floor."
      },
      {
        account_id: "ob_acct_personal",
        label: "Personal OB Account",
        lane: "Personal",
        purpose: "Owner liquidity and learning flexibility.",
        risk_profile: "moderate-capped",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1"],
        capital_goal: "Owner liquidity without borrowing from mission lanes.",
        deployment_rules: "Receipted owner withdrawal only.",
        tower_clearance: "required",
        current_status: "policy-ready",
        next_action: "Keep separate from trust, ATM, and apartment capital."
      },
      {
        account_id: "ob_acct_simplee_world",
        label: "Simplee World OB Account",
        lane: "Simplee World",
        purpose: "Business growth capital for the parent ecosystem.",
        risk_profile: "moderate",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1"],
        capital_goal: "Business operating and build capital.",
        deployment_rules: "Cannot fund personal spending; Tower receipt required.",
        tower_clearance: "required",
        current_status: "policy-ready",
        next_action: "Use business-only purpose labels."
      },
      {
        account_id: "ob_acct_atm",
        label: "SimpleeOnTheGo / ATM OB Account",
        lane: "SimpleeOnTheGo / ATM",
        purpose: "Build toward ATM route acquisition and vault cash support.",
        risk_profile: "low-to-moderate then low near target",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1"],
        capital_goal: "First major deployment target around $10k.",
        deployment_rules: "Risk reduces near deployment zone; withdrawal only for approved ATM move.",
        tower_clearance: "required",
        current_status: "policy-ready",
        next_action: "Track readiness toward first ATM route capital move."
      },
      {
        account_id: "ob_acct_apartment",
        label: "SimpleeProperty / Apartment OB Account",
        lane: "SimpleeProperty / Apartment",
        purpose: "Apartment acquisition reserve and lender-readiness capital.",
        risk_profile: "lowest",
        allowed_modes: ["survey", "paper", "manual_live_owner_level_1_later"],
        capital_goal: "4–5 building apartment acquisition path.",
        deployment_rules: "Capital preservation first; no aggressive options; Tower + Vault-ready receipt required.",
        tower_clearance: "required",
        current_status: "protected-policy-ready",
        next_action: "Keep conservative until acquisition packet is lender-ready."
      },
      {
        account_id: "ob_acct_proof_demo",
        label: "Proof/Demo OB Account",
        lane: "Proof/Demo",
        purpose: "Safe demonstration records only.",
        risk_profile: "zero-real-risk",
        allowed_modes: ["survey", "paper", "demo"],
        capital_goal: "No real capital.",
        deployment_rules: "Never broker-connected; never real-money; no public proof leakage.",
        tower_clearance: "required",
        current_status: "demo-only",
        next_action: "Use for safe demo/proof snapshots only."
      }
    ];
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_001_safe_fallback",
      tower_sources: {
        shared_foundation: "Packs 396-450 Tower ecosystem foundation",
        capital_safety: "Packs 451-500 Tower capital safety controls",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        mode_permission_controller: "/tower/tower-mode-permission-controller-index-v461.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      tower_flags: {
        mission_account_enabled: true,
        optional_goal_accounts: false,
        manual_live_enabled: true,
        manual_live_owner_only: true,
        beta_user: false,
        owner_user: true,
        proof_demo_access: true,
        hybrid_locked: true,
        automated_locked: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      },
      active_profile: "owner_user",
      profiles: {
        owner_user: {
          label: "Owner / Solice",
          account_model: "mission_accounts",
          mission_account_enabled: true,
          manual_live_enabled: true,
          manual_live_owner_only: true,
          sees_capital_goals: true,
          sees_deployment_rules: true,
          sees_tower_clearance: true
        },
        beta_user: {
          label: "Standard Beta User",
          account_model: "simple_survey_paper",
          mission_account_enabled: false,
          manual_live_enabled: false,
          manual_live_owner_only: false,
          sees_capital_goals: false,
          sees_deployment_rules: false,
          sees_tower_clearance: false
        },
        advanced_user: {
          label: "Future Advanced User",
          account_model: "optional_goal_accounts_placeholder",
          mission_account_enabled: false,
          optional_goal_accounts: true,
          manual_live_enabled: false,
          sees_capital_goals: false,
          placeholder_only: true
        },
        proof_demo: {
          label: "Proof/Demo",
          account_model: "safe_demo_only",
          real_capital_allowed: false,
          broker_connection_allowed: false,
          public_proof_allowed: false
        }
      },
      owner_mission_accounts: ownerMissionAccounts(),
      beta_user_account: {
        account_id: "ob_acct_standard_beta",
        label: "My OB Account",
        display_label: "Paper Trading Account",
        modes: ["survey", "paper"],
        portfolio: ["watchlist", "paper_positions"],
        risk_level: "basic / standard",
        goal: "Learn, observe, paper trade, review, and give feedback.",
        hidden_language: ["trust", "ATM capital", "apartment reserves", "mission deployment", "business funding"]
      },
      advanced_user_placeholder: {
        account_id: "ob_acct_advanced_placeholder",
        label: "Optional Goal Accounts",
        status: "placeholder_only",
        future_options: ["goal accounts", "portfolio accounts", "risk profiles", "long-term vs short-term paper portfolios"]
      },
      mode_ladder: [
        "survey",
        "paper",
        "manual_live_owner_level_1",
        "manual_live_owner_level_2",
        "hybrid_monitor_locked",
        "hybrid_assisted_locked",
        "automated_limited_locked",
        "automated_expanded_locked"
      ],
      product_rules: [
        "Mission accounts are owner-side by default.",
        "Normal beta users get a simple Survey/Paper account.",
        "Advanced users may later get optional goal accounts.",
        "Manual Live is owner-only first.",
        "Hybrid is designed as a locked framework first.",
        "Automated remains locked.",
        "Tower decides the account experience.",
        "OB displays the account experience and follows Tower policy."
      ],
      boundaries: {
        private_beta_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        tower_owns_permissions: true,
        ob_owns_capital_trading_mission_accounts: true
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
      tower_flags: { ...(fallback.tower_flags || {}), ...(safe.tower_flags || {}) },
      active_profile: safe.active_profile || fallback.active_profile,
      profiles: { ...(fallback.profiles || {}), ...(safe.profiles || {}) },
      owner_mission_accounts: Array.isArray(safe.owner_mission_accounts) ? safe.owner_mission_accounts : fallback.owner_mission_accounts,
      beta_user_account: safe.beta_user_account || fallback.beta_user_account,
      advanced_user_placeholder: safe.advanced_user_placeholder || fallback.advanced_user_placeholder,
      mode_ladder: Array.isArray(safe.mode_ladder) ? safe.mode_ladder : fallback.mode_ladder,
      product_rules: Array.isArray(safe.product_rules) ? safe.product_rules : fallback.product_rules,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        tower_owns_permissions: true,
        ob_owns_capital_trading_mission_accounts: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_ACCOUNT_EXPERIENCE_GP001 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      account_experience_gp001: normalized,
      mission_account_enabled: normalized.tower_flags.mission_account_enabled,
      manual_live_owner_only: normalized.tower_flags.manual_live_owner_only,
      hybrid_locked: normalized.tower_flags.hybrid_locked,
      automated_locked: normalized.tower_flags.automated_locked
    };

    window.dispatchEvent(new CustomEvent("obAccountExperienceUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchAccountExperience() {
    accountState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      accountState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        accountState.status = "ready";
        accountState.source = normalized.source || "server";
        accountState.payload = normalized;
        accountState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        accountState.status = "guarded_fallback";
        accountState.source = "guarded_fallback";
        accountState.payload = fallback;
        accountState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      accountState.status = "error_fallback";
      accountState.source = "error_fallback";
      accountState.payload = fallback;
      accountState.fallbackActive = true;
      accountState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return accountState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("required")) return "red";
    if (text.includes("owner") || text.includes("policy") || text.includes("manual")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-account-experience-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function accountRow(item, index) {
    return `
      <div class="ob-account-experience-row">
        <div class="ob-account-experience-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Mission Account")}</strong>
          <span>${safeText(item.lane, "lane")} · ${safeText(item.risk_profile, "risk")}</span>
        </div>
        <span>${safeText(item.purpose, "Purpose not set.")}<br>${safeText(item.capital_goal, "")}<br>${safeText(item.next_action, "")}</span>
        <div class="ob-account-experience-status ${statusClass(item.current_status)}">${safeText(item.current_status, "review")}</div>
      </div>
    `;
  }

  function modePill(mode) {
    const cls = mode.includes("locked") || mode.includes("automated") || mode.includes("hybrid") ? "red" : mode.includes("manual") ? "gold" : "green";
    return `<span class="ob-account-experience-mode ${cls}">${mode.replaceAll("_", " ")}</span>`;
  }

  function ruleRow(item, index) {
    return `
      <div class="ob-account-experience-row">
        <div class="ob-account-experience-dot">✓</div>
        <div><strong>Rule ${index + 1}</strong><span>Tower-aligned</span></div>
        <span>${safeText(item, "Rule")}</span>
        <div class="ob-account-experience-status gold">active</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = accountState.payload || buildFallbackPayload();
    const flags = payload.tower_flags || {};
    const ownerAccounts = Array.isArray(payload.owner_mission_accounts) ? payload.owner_mission_accounts : [];
    const beta = payload.beta_user_account || {};
    const advanced = payload.advanced_user_placeholder || {};
    const modes = Array.isArray(payload.mode_ladder) ? payload.mode_ladder : [];
    const rules = Array.isArray(payload.product_rules) ? payload.product_rules : [];

    return `
      <div class="ob-account-experience-panel" id="obAccountExperiencePanel" data-ob-giant-pack-001="true">
        <div class="ob-account-experience-head">
          <div>
            <div class="ob-label">OB Giant Pack 001 · Account Experience</div>
            <div class="ob-account-experience-title">Owner + User Account Experience</div>
            <div class="ob-account-experience-subtitle">
              ${safeText(payload.active_profile, "owner_user")} · ${safeText(accountState.status, "booting")} · Tower decides which account model a user sees.
            </div>
          </div>
          <div class="ob-account-experience-chip-row">
            <span class="ob-account-experience-chip ${flags.mission_account_enabled ? "green" : "red"}">mission account ${flags.mission_account_enabled ? "enabled" : "hidden"}</span>
            <span class="ob-account-experience-chip gold">Manual Live owner-only</span>
            <span class="ob-account-experience-chip red">Hybrid locked</span>
            <span class="ob-account-experience-chip red">Automated locked</span>
          </div>
        </div>

        <div class="ob-account-experience-stat-grid">
          ${card("Owner model", "Mission accounts")}
          ${card("Beta model", "Survey / Paper")}
          ${card("Advanced model", "Placeholder")}
          ${card("Tower", "Experience gate")}
        </div>

        <div class="ob-account-experience-grid">
          <div>
            <div class="ob-account-experience-card">
              <span>Standard user experience</span>
              <strong>${safeText(beta.display_label || beta.label, "Paper Trading Account")}</strong>
              <div class="ob-account-experience-callout">
                <strong>Beta user sees:</strong><br>
                ${safeText(beta.goal, "Learn, observe, paper trade, review, and give feedback.")}
              </div>
              <div class="ob-account-experience-boundary">
                <strong>Hidden from normal users:</strong><br>
                Mission capital, trust language, ATM deployment, apartment reserves, owner governance, and Manual Live authority.
              </div>
            </div>

            <div class="ob-account-experience-card" style="margin-top: 11px;">
              <span>Future advanced placeholder</span>
              <strong>${safeText(advanced.label, "Optional Goal Accounts")}</strong>
              <div class="ob-account-experience-callout">
                <strong>Later only:</strong><br>
                ${(advanced.future_options || []).join("<br>")}
              </div>
            </div>

            <div class="ob-account-experience-card" style="margin-top: 11px;">
              <span>Mode ladder</span>
              <div class="ob-account-experience-mode-row">${modes.map(modePill).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-account-experience-section">
              <div class="ob-account-experience-section-title">Owner mission accounts</div>
              <div class="ob-account-experience-list">${ownerAccounts.map(accountRow).join("")}</div>
            </div>

            <div class="ob-account-experience-section">
              <div class="ob-account-experience-section-title">Product rules</div>
              <div class="ob-account-experience-list">${rules.map(ruleRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-account-experience-callout">
          <strong>Source:</strong><br>
          OB is using Tower foundation + Tower capital safety contracts as the authority layer. OB displays account experience; Tower controls permissions, mode gates, kill switches, and capital safety.
        </div>

        <div class="ob-account-experience-boundary">
          <strong>Boundary:</strong><br>
          No public signup. No public proof. No broker API. No auto execution. Live Auto Locked. Hybrid and Automated remain locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obAccountExperiencePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const dashboardFocus = document.querySelector("[data-ob-dashboard-focus]");
    const nextTesterGate = document.getElementById("obPrivateBetaNextTesterGatePanel");
    const launchControl = document.getElementById("obPrivateBetaLaunchControlPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (dashboardFocus && dashboardFocus.parentNode) dashboardFocus.insertAdjacentElement("afterend", panel);
    else if (nextTesterGate && nextTesterGate.parentNode) nextTesterGate.insertAdjacentElement("afterend", panel);
    else if (launchControl && launchControl.parentNode) launchControl.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = accountState.payload || buildFallbackPayload();
    const flags = payload.tower_flags || {};

    document.body.setAttribute("data-ob-giant-pack-001-account-experience", "ready");
    document.body.setAttribute("data-ob-mission-account-enabled", flags.mission_account_enabled ? "true" : "false");
    document.body.setAttribute("data-ob-manual-live-owner-only", "true");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");

    window.OB_GIANT_PACK_001_ACCOUNT_EXPERIENCE_STATE = {
      version: VERSION,
      status: accountState.status,
      fallbackActive: accountState.fallbackActive,
      activeProfile: payload.active_profile,
      missionAccountEnabled: !!flags.mission_account_enabled,
      manualLiveOwnerOnly: true,
      hybridLocked: true,
      automatedLocked: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchAccountExperience();
    }, 2880);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_ACCOUNT_EXPERIENCE_GP001_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return accountState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchAccountExperience,
    renderPanel,
    setFlags
  };
})();
