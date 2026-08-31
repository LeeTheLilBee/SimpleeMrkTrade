// OBUX086–090 — SOULAANA OWNER CAPITAL-LANE BRIEFING
(() => {
  "use strict";

  const VERSION =
    "OBUX086_090_SOULAANA_OWNER_CAPITAL_LANES";


  const safeText = (
    value,
    fallback = ""
  ) => {
    if (
      value === undefined
      || value === null
      || value === ""
    ) {
      return fallback;
    }

    return String(
      value
    );
  };


  const buildBriefing = (
    contract
  ) => {
    const safe =
      contract
      || {};

    const lanes =
      Array.isArray(
        safe.capital_lanes
      )
        ? safe.capital_lanes
        : [];

    const attention =
      Array.isArray(
        safe.owner_attention
      )
        ? safe.owner_attention
        : [];

    const trust =
      safe.trust
      || {};

    const readiness =
      safe.readiness
      || {};

    const beta =
      safe.beta
      || {};

    const interpretation =
      safe.interpretation_state
      || {};

    const guarded = [
      !trust.verified
        ? "engine trust"
        : null,

      !readiness.verified
        ? "Manual Live readiness"
        : null,

      !beta.verified
        ? "private beta"
        : null
    ].filter(
      Boolean
    );

    const high =
      attention.filter(
        function (
          item
        ) {
          return (
            item.priority
            === "high"
          );
        }
      );

    const verifiedCapital =
      lanes.filter(
        function (
          lane
        ) {
          return (
            lane.actual_capital_known
            || lane.capital_progress_known
          );
        }
      );

    let headline;
    let whatISee;

    if (
      high.length
    ) {
      headline =
        "I found something that actually needs you.";

      whatISee =
        (
          `${high.length} owner-level item(s) `
          + "deserve attention. Start there."
        );

    } else if (
      guarded.length
    ) {
      headline =
        "Your lanes are organized. Some truth is still guarded.";

      whatISee =
        (
          `I can see ${lanes.length} Capital Lanes. `
          + `${guarded.join(", ")} ${
              guarded.length === 1
                ? "is"
                : "are"
            } still unverified.`
        );

    } else {
      headline =
        "The Observatory is calm at owner altitude.";

      whatISee =
        (
          "Nothing verified is forcing an owner decision. "
          + "You can stay focused."
        );
    }

    const capitalRead =
      verifiedCapital.length
        ? (
            `${verifiedCapital.length} Capital Lane(s) `
            + "have verified capital or progress truth."
          )
        : (
            "Capital policy is visible. "
            + "Unverified balances stay unverified."
          );

    const nextMove =
      high.length
        ? (
            "Start with: "
            + safeText(
                high[0].title,
                "the highest-priority owner item"
              )
          )
        : guarded.length
          ? (
              "Next: verify "
              + guarded[0]
              + "."
            )
          : (
              "No forced move. Pick a Capital Lane "
              + "only when you need that context."
            );

    return {
      version:
        VERSION,

      eyebrow:
        "SOULAANA · OWNER BRIEFING",

      headline,

      what_i_see:
        whatISee,

      capital_read:
        capitalRead,

      what_needs_you:
        attention.length
          ? attention
              .map(
                function (
                  item
                ) {
                  return (
                    safeText(
                      item.title,
                      "Owner item"
                    )
                  );
                }
              )
              .join(
                " · "
              )
          : (
              "Nothing verified "
              + "is asking for you."
            ),

      next_best_move:
        nextMove,

      no_action_needed:
        interpretation
          .no_action_needed
          === true,

      owner_altitude:
        (
          "Normal Dashboard watches the Observatory. "
          + "Owner Dashboard organizes your capital context."
        ),

      evidence_rule:
        (
          "Short answer first. "
          + "Deeper evidence stays collapsed until you ask."
        )
    };
  };


  window
    .OB_OWNER_DASHBOARD_SOULAANA_V22 =
      Object.freeze({
        version:
          VERSION,

        buildBriefing
      });

})();
