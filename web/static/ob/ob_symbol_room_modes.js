// =================================================================================================
// THE OBSERVATORY — SYMBOL ROOM MODE CONTRACT
// OBUX037
// =================================================================================================

(function () {
  "use strict";

  const VERSION = "OBUX037_SYMBOL_ROOM_MODE_CONTRACT";

  const MODE = Object.freeze({
    SURVEY: "survey",
    PAPER: "paper",
    MANUAL_LIVE_1: "manual_live_1",
    HYBRID: "hybrid",
    AUTOMATED: "automated",
  });

  const CONTRACTS = Object.freeze({
    [MODE.SURVEY]: Object.freeze({
      key: MODE.SURVEY,
      label: "Survey",
      verb: "Observe",
      message:
        "Observe the star, inspect options facts, and compare evidence. Nothing here needs to become a trade.",
      owner_decision_required: false,
      user_chooses_contract: false,
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: false,
      scenario_test: false,
      live_signal_context: false,
      objective_option_set: false,
      contract_selection: false,
      trade_handoff: false,
      trade_handoff_kind: null,
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: false,
    }),

    [MODE.PAPER]: Object.freeze({
      key: MODE.PAPER,
      label: "Paper",
      verb: "Practice",
      message:
        "Build and test a hypothetical idea. Everything remains paper-only.",
      owner_decision_required: true,
      user_chooses_contract: true,
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: true,
      scenario_test: true,
      live_signal_context: false,
      objective_option_set: false,
      contract_selection: true,
      trade_handoff: true,
      trade_handoff_kind: "paper_only",
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: false,
    }),

    [MODE.MANUAL_LIVE_1]: Object.freeze({
      key: MODE.MANUAL_LIVE_1,
      label: "Manual Live 1",
      verb: "Review",
      message:
        "OB shows verified evidence. You independently decide what, if anything, deserves to move forward. You execute at the brokerage; OB does not.",
      owner_decision_required: true,
      user_chooses_contract: true,
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: false,
      scenario_test: false,
      live_signal_context: true,
      objective_option_set: false,
      contract_selection: true,
      trade_handoff: true,
      trade_handoff_kind: "owner_review",
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: false,
    }),

    [MODE.HYBRID]: Object.freeze({
      key: MODE.HYBRID,
      label: "Hybrid",
      verb: "Compare",
      message:
        "OB may surface contracts that match displayed objective filters. You compare them and you choose the option.",
      owner_decision_required: true,
      user_chooses_contract: true,
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: false,
      scenario_test: false,
      live_signal_context: true,
      objective_option_set: true,
      contract_selection: true,
      trade_handoff: true,
      trade_handoff_kind: "owner_selected",
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: false,
    }),

    [MODE.AUTOMATED]: Object.freeze({
      key: MODE.AUTOMATED,
      label: "Automated",
      verb: "Locked",
      message:
        "Automated decision and execution capability is intentionally locked in this Symbol Room layer.",
      owner_decision_required: true,
      user_chooses_contract: false,
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: false,
      scenario_test: false,
      live_signal_context: false,
      objective_option_set: false,
      contract_selection: false,
      trade_handoff: false,
      trade_handoff_kind: null,
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: true,
    }),
  });

  function normalizeMode(value) {
    const raw = String(value || "")
      .trim()
      .toLowerCase()
      .replaceAll("-", "_")
      .replaceAll(" ", "_");

    if (!raw) return null;

    if (
      raw === "survey" ||
      raw === "observe"
    ) {
      return MODE.SURVEY;
    }

    if (
      raw === "paper" ||
      raw === "paper_mode" ||
      raw === "practice"
    ) {
      return MODE.PAPER;
    }

    if (
      raw === "manual_live_1" ||
      raw === "manual_live_level_1" ||
      raw === "manual_live_owner_level_1" ||
      raw === "manual_live_owner_l1"
    ) {
      return MODE.MANUAL_LIVE_1;
    }

    if (
      raw.startsWith("hybrid")
    ) {
      return MODE.HYBRID;
    }

    if (
      raw.startsWith("automated") ||
      raw === "auto" ||
      raw === "live_auto"
    ) {
      return MODE.AUTOMATED;
    }

    return null;
  }

  function authorityCandidates() {
    const server =
      window.OB_SERVER_DATA &&
      typeof window.OB_SERVER_DATA === "object"
        ? window.OB_SERVER_DATA
        : {};

    const modeState =
      window.OB_MODE_STATE &&
      typeof window.OB_MODE_STATE === "object"
        ? window.OB_MODE_STATE
        : {};

    return [
      modeState.authorized_mode,
      modeState.active_mode,
      modeState.current_mode,
      server.authorized_mode,
      server.active_mode,
      server.current_mode,
      server.mode,
      document.body
        ? document.body.getAttribute("data-ob-authorized-mode")
        : null,
    ];
  }

  function requestedAuthorizedMode() {
    for (const candidate of authorityCandidates()) {
      const normalized = normalizeMode(candidate);
      if (normalized) return normalized;
    }

    // SAFE FAIL-CLOSED FALLBACK:
    // The Symbol Room never grants itself Paper/Live/Hybrid.
    return MODE.SURVEY;
  }

  function accountAuthority() {
    const experience =
      window.OB_ACCOUNT_EXPERIENCE_GP001 &&
      typeof window.OB_ACCOUNT_EXPERIENCE_GP001 === "object"
        ? window.OB_ACCOUNT_EXPERIENCE_GP001
        : {};

    const flags =
      experience.tower_flags &&
      typeof experience.tower_flags === "object"
        ? experience.tower_flags
        : {};

    const profile =
      String(
        experience.active_profile ||
        "unknown"
      ).toLowerCase();

    return {
      profile,
      owner:
        profile === "owner_user" ||
        profile === "owner" ||
        profile.includes("owner"),
      manualLiveEnabled:
        flags.manual_live_enabled === true,
      manualLiveOwnerOnly:
        flags.manual_live_owner_only !== false,
      hybridLocked:
        flags.hybrid_locked !== false,
      automatedLocked:
        flags.automated_locked !== false,
      liveAutoLocked:
        flags.live_auto_locked !== false,
      noBrokerApi:
        flags.no_broker_api !== false,
      noAutoExecution:
        flags.no_auto_execution !== false,
    };
  }

  function authorize(mode) {
    const normalized =
      normalizeMode(mode) ||
      MODE.SURVEY;

    const authority =
      accountAuthority();

    if (normalized === MODE.SURVEY) {
      return {
        requested: normalized,
        effective: MODE.SURVEY,
        permitted: true,
        locked: false,
        reason: null,
      };
    }

    if (normalized === MODE.PAPER) {
      return {
        requested: normalized,
        effective: MODE.PAPER,
        permitted: true,
        locked: false,
        reason: null,
      };
    }

    if (normalized === MODE.MANUAL_LIVE_1) {
      const permitted =
        authority.manualLiveEnabled &&
        (
          !authority.manualLiveOwnerOnly ||
          authority.owner
        );

      return {
        requested: normalized,
        effective:
          permitted
            ? MODE.MANUAL_LIVE_1
            : MODE.SURVEY,
        permitted,
        locked: !permitted,
        reason:
          permitted
            ? null
            : "Manual Live 1 is not authorized for this account/session.",
      };
    }

    if (normalized === MODE.HYBRID) {
      const permitted =
        authority.hybridLocked === false;

      return {
        requested: normalized,
        effective:
          permitted
            ? MODE.HYBRID
            : MODE.SURVEY,
        permitted,
        locked: !permitted,
        reason:
          permitted
            ? null
            : "Hybrid is currently locked by the existing account authority state.",
      };
    }

    // Automated stays locked in THIS layer even if some future external
    // flag changes. A later explicit build must unlock its contract.
    if (normalized === MODE.AUTOMATED) {
      return {
        requested: normalized,
        effective: MODE.AUTOMATED,
        permitted: false,
        locked: true,
        reason:
          "Automated remains intentionally locked in OBUX036–040.",
      };
    }

    return {
      requested: MODE.SURVEY,
      effective: MODE.SURVEY,
      permitted: true,
      locked: false,
      reason: null,
    };
  }

  function current() {
    const requested =
      requestedAuthorizedMode();

    const authorization =
      authorize(requested);

    const contract =
      CONTRACTS[authorization.effective] ||
      CONTRACTS[MODE.SURVEY];

    return Object.freeze({
      ...contract,
      authorization,
      authority: accountAuthority(),
    });
  }

  window.OB_SYMBOL_ROOM_MODES_OBUX037 = Object.freeze({
    VERSION,
    MODE,
    CONTRACTS,
    normalizeMode,
    requestedAuthorizedMode,
    accountAuthority,
    authorize,
    current,
  });

  window.dispatchEvent(
    new CustomEvent(
      "obSymbolRoomModeContractReady",
      {
        detail: {
          version: VERSION,
        },
      }
    )
  );
})();
