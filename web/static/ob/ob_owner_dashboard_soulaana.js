
// OBUX091–095 — SOULAANA OWNER INTELLIGENCE BRIEFING
(() => {
  "use strict";

  const VERSION =
    "OBUX091_095_SOULAANA_OWNER_INTELLIGENCE";


  const safeArray = (
    value
  ) => (
    Array.isArray(
      value
    )
      ? value
      : []
  );


  const safeText = (
    value,
    fallback = ""
  ) => (
    value === undefined
    || value === null
    || value === ""
      ? fallback
      : String(value)
  );


  const buildBriefing = (
    contract
  ) => {
    const safe =
      contract
      || {};

    const edge =
      safe.today_edge
      || {};

    const now =
      safeArray(
        edge.now
      );

    const watch =
      safeArray(
        edge.watch
      );

    const notYet =
      safeArray(
        edge.not_yet
      );

    const attention =
      safeArray(
        safe.owner_attention
      );

    const trust =
      safe.trust
      || {};

    const readiness =
      safe.readiness
      || {};

    const lanes =
      safeArray(
        safe.capital_lanes
      );

    const guarded =
      !(
        edge.source_state
        && edge
          .source_state
          .verified_current_market
      );


    let headline;
    let whatISee;
    let nextMove;


    if (
      now.length
    ) {
      headline =
        "I found verified research that deserves your eyes.";

      whatISee =
        (
          `${now.length} setup${now.length === 1 ? "" : "s"} `
          + "made it into NOW from current source-backed engine truth."
        );

      nextMove =
        (
          "Open the first NOW setup, "
          + "read why it surfaced, "
          + "then decide whether you want to study the stock or its option contracts."
        );

    } else if (
      watch.length
    ) {
      headline =
        "Nothing is screaming. I do have things worth watching.";

      whatISee =
        (
          `${watch.length} current setup${watch.length === 1 ? "" : "s"} `
          + "made WATCH, but the source did not prove a NOW state."
        );

      nextMove =
        "Open WATCH only if you want more context.";

    } else if (
      guarded
    ) {
      headline =
        "Some truth is still guarded.";

      whatISee =
        (
          "I do not have enough current verified candidate truth "
          + "to manufacture a trade idea."
        );

      nextMove =
        "No forced move. Verify the market source first.";

    } else {
      headline =
        "Nothing verified is forcing an owner decision.";

      whatISee =
        "The Observatory is quiet at owner altitude.";

      nextMove =
        "No forced move. Pick a Capital Lane only when you need that context.";
    }


    const verifiedCapital =
      lanes.filter(
        lane =>
          lane.actual_capital_known
          || lane.capital_progress_known
      );


    return {
      version:
        VERSION,

      eyebrow:
        "SOULAANA · OWNER BRIEFING",

      headline,

      what_i_see:
        whatISee,

      why_it_matters:
        (
          now.length
            ? (
                "NOW means the current source supplied enough candidate state "
                + "to surface it here. It does not mean guaranteed profit."
              )
            : (
                "I would rather show you less than invent certainty."
              )
        ),

      capital_read:
        verifiedCapital.length
          ? (
              `${verifiedCapital.length} Capital Lane`
              + (
                  verifiedCapital.length === 1
                    ? ""
                    : "s"
                )
              + " has verified capital or progress truth."
            )
          : (
              "Capital policy is visible. "
              + "Unverified balances stay unverified."
            ),

      what_needs_you:
        attention.length
          ? attention
              .map(
                item =>
                  safeText(
                    item.title,
                    "Owner item"
                  )
              )
              .join(
                " · "
              )
          : (
              "Nothing verified "
              + "is asking for you."
            ),

      watch_count:
        watch.length,

      not_yet_count:
        notYet.length,

      readiness:
        safeText(
          readiness.label,
          "Readiness unavailable"
        ),

      system_trust:
        safeText(
          trust.label,
          "Trust unavailable"
        ),

      beta_state:
        safeText(
          safe.beta
          && safe.beta.label,
          "Beta state unavailable"
        ),

      what_changed:
        "No verified owner-change history yet",

      what_im_learning:
        "No verified cross-lane pattern yet",

      what_can_wait:
        (
          "Anything outside NOW, "
          + "your top-three attention items, "
          + "or an explicit drawer can wait."
        ),

      next_best_move:
        nextMove,

      no_action_needed:
        (
          safe.interpretation_state
          && safe
            .interpretation_state
            .no_action_needed
          === true
        ),

      owner_altitude:
        (
          "Normal Dashboard watches the Observatory. "
          + "Owner Dashboard organizes your capital context "
          + "and your private research intelligence."
        ),

      evidence_rule:
        (
          "Short answer first. "
          + "Deeper evidence stays collapsed until you ask."
        )
    };
  };


  window.OB_OWNER_DASHBOARD_SOULAANA_V22 =
    Object.freeze({
      version:
        VERSION,

      buildBriefing
    });

})();
