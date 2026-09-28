(function () {
  "use strict";

  const MODE_SURVEY = "survey";
  const MODE_PAPER = "paper";
  const MODE_MANUAL_LIVE_1 = "manual_live_1";
  const MODE_HYBRID = "hybrid";
  const MODE_AUTOMATED = "automated";

  const MODES = Object.freeze({
    [MODE_SURVEY]: Object.freeze({
      id: MODE_SURVEY,
      label: "Survey",
      eyebrow: "OBSERVE",
      capital: "NONE",
      contract_choice_authority: "NONE",
      ranked_contract_set_visible: true,
      simulated_execution: false,
      owner_external_execution: false,
      broker_execution: false,
      automatic_execution: false,
      automated_contract_selection: false,
      locked: false,

      copy: Object.freeze({
        title: "Observe the setup",
        instruction:
          "Inspect the trade, contract quality, risk, and lifecycle readiness without entering an execution workflow.",
      }),
    }),

    [MODE_PAPER]: Object.freeze({
      id: MODE_PAPER,
      label: "Paper",
      eyebrow: "PRACTICE",
      capital: "SIMULATED",
      contract_choice_authority: "USER",
      ranked_contract_set_visible: true,
      simulated_execution: true,
      owner_external_execution: false,
      broker_execution: false,
      automatic_execution: false,
      automated_contract_selection: false,
      locked: false,

      copy: Object.freeze({
        title: "Practice the complete trade",
        instruction:
          "Choose the paper contract, simulate entry, manage the position, close it, and send the result into review.",
      }),
    }),

    [MODE_MANUAL_LIVE_1]: Object.freeze({
      id: MODE_MANUAL_LIVE_1,
      label: "Manual Live 1",
      eyebrow: "OWNER DECISION",
      capital: "LIVE",
      contract_choice_authority: "OWNER",
      ranked_contract_set_visible: true,
      simulated_execution: false,
      owner_external_execution: true,
      broker_execution: false,
      automatic_execution: false,
      automated_contract_selection: false,
      locked: false,

      copy: Object.freeze({
        title: "Owner decision required",
        instruction:
          "You choose the contract. OB prepares the workflow. You place the trade outside OB and then report the actual result.",
      }),
    }),

    [MODE_HYBRID]: Object.freeze({
      id: MODE_HYBRID,
      label: "Hybrid",
      eyebrow: "RANKED SET · YOU CHOOSE",
      capital: "LIVE_GATED",
      contract_choice_authority: "USER",
      ranked_contract_set_visible: true,
      simulated_execution: false,
      owner_external_execution: true,
      broker_execution: false,
      automatic_execution: false,
      automated_contract_selection: false,
      locked: false,

      copy: Object.freeze({
        title: "Choose from the objective contract set",
        instruction:
          "OB may narrow and rank the option set. You choose the contract. Ranking is not selection authority.",
      }),
    }),

    [MODE_AUTOMATED]: Object.freeze({
      id: MODE_AUTOMATED,
      label: "Automated",
      eyebrow: "LOCKED",
      capital: "LOCKED",
      contract_choice_authority: "LOCKED",
      ranked_contract_set_visible: false,
      simulated_execution: false,
      owner_external_execution: false,
      broker_execution: false,
      automatic_execution: false,
      automated_contract_selection: false,
      locked: true,

      copy: Object.freeze({
        title: "Automated mode is locked",
        instruction:
          "No automated contract-selection or execution controls are exposed in this Observatory build.",
      }),
    }),
  });

  function normalizeMode(value) {
    const raw = String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, "_");

    const aliases = {
      survey: MODE_SURVEY,
      observe: MODE_SURVEY,

      paper: MODE_PAPER,
      practice: MODE_PAPER,

      manual: MODE_MANUAL_LIVE_1,
      manual_live: MODE_MANUAL_LIVE_1,
      manual_live_1: MODE_MANUAL_LIVE_1,
      live: MODE_MANUAL_LIVE_1,

      hybrid: MODE_HYBRID,

      auto: MODE_AUTOMATED,
      automated: MODE_AUTOMATED,
    };

    return aliases[raw] || MODE_SURVEY;
  }

  function getMode(value) {
    return MODES[normalizeMode(value)];
  }

  function resolveMode() {
    const candidates = [
      window.OB_MODE,
      window.OBMode,
      window.obMode,
      document.documentElement.dataset.obMode,
      document.body && document.body.dataset.obMode,
      sessionStorage.getItem("ob_mode"),
      localStorage.getItem("ob_mode"),
    ];

    for (const value of candidates) {
      if (value) {
        return getMode(value);
      }
    }

    return getMode(MODE_SURVEY);
  }

  window.OBTradeCenterModes = Object.freeze({
    MODE_SURVEY,
    MODE_PAPER,
    MODE_MANUAL_LIVE_1,
    MODE_HYBRID,
    MODE_AUTOMATED,
    MODES,
    normalizeMode,
    getMode,
    resolveMode,

    safety: Object.freeze({
      manual_live_ob_selects_contract: false,
      hybrid_ob_selects_contract: false,
      broker_execution: false,
      automatic_execution: false,
      automated_locked: true,
    }),
  });
})();
