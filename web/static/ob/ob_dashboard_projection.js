
// OBUX091–095 — CALM SELF-DIRECTED USER DASHBOARD PROJECTION
//
// The normal Dashboard receives ONLY:
//   - broad market state
//   - neutral symbol-study prompts
//   - Paper / Survey context
//   - review/session summaries
//
// It deliberately does NOT project:
//   - owner Capital Lanes
//   - ranked owner candidates
//   - entry / stop / target
//   - option contract recommendations
//   - individualized live recommendations
//
(function (global) {
  "use strict";

  const VERSION =
    "OBUX091_095_USER_DASHBOARD_PROJECTION";

  const BOUNDARIES =
    Object.freeze({
      owner_capital_lanes:
        false,

      owner_candidate_payloads:
        false,

      personalized_security_recommendations:
        false,

      option_contract_recommendations:
        false,

      manual_live_recommendations:
        false,

      broker_submission:
        false,

      capital_movement:
        false,

      automatic_contract_selection:
        false,

      automatic_execution:
        false,

      live_auto_locked:
        true,

      survey_and_paper_first:
        true
    });


  function safeArray(
    value
  ) {
    return Array.isArray(
      value
    )
      ? value
      : [];
  }


  function safeObject(
    value
  ) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    )
      ? value
      : {};
  }


  function safeText(
    value,
    fallback
  ) {
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
  }


  function canonicalProjection() {
    const server =
      safeObject(
        global.OB_SERVER_DATA
      );

    return safeObject(
      server.canonical_web_projection
      || server.engine_feed_v25
      || global.OB_ENGINE_FEED_SNAPSHOT_V25
    );
  }


  function selectedMode() {
    try {
      const session =
        global.OBSessionState
          ? global
              .OBSessionState
              .snapshot()
          : null;

      return (
        session
        && session.persistent
        && session.persistent.selectedMode
      )
        ? String(
            session.persistent.selectedMode
          )
        : "Survey";

    } catch (_) {
      return "Survey";
    }
  }


  function neutralSymbolFacts(
    projection
  ) {
    const sourceSymbols =
      safeArray(
        projection.symbols
      );

    const sourceCandidates =
      safeArray(
        projection.candidates_preview
      );

    const seen =
      new Set();

    const facts = [];


    function addFact(
      symbol,
      sourceLabel
    ) {
      const clean =
        safeText(
          symbol,
          ""
        )
          .trim()
          .toUpperCase();

      if (
        !clean
        || seen.has(clean)
      ) {
        return;
      }

      seen.add(
        clean
      );

      facts.push({
        symbol:
          clean,

        title:
          clean,

        detail:
          "Source-backed market activity is available to study.",

        source:
          sourceLabel,

        href:
          (
            "/ob/symbol/"
            + encodeURIComponent(
                clean
              )
          )
      });
    }


    sourceSymbols.forEach(
      function (
        item
      ) {
        if (
          facts.length >= 3
        ) {
          return;
        }

        if (
          typeof item === "string"
        ) {
          addFact(
            item,
            "canonical market projection"
          );
          return;
        }

        const obj =
          safeObject(
            item
          );

        addFact(
          (
            obj.symbol
            || obj.ticker
          ),
          (
            obj.source
            || projection.source
            || "canonical market projection"
          )
        );
      }
    );


    sourceCandidates.forEach(
      function (
        item
      ) {
        if (
          facts.length >= 3
        ) {
          return;
        }

        const obj =
          safeObject(
            item
          );

        addFact(
          (
            obj.symbol
            || obj.ticker
          ),
          (
            obj.source
            || projection.source
            || "canonical candidate projection"
          )
        );
      }
    );


    return facts.slice(
      0,
      3
    );
  }


  function marketState(
    projection
  ) {
    const health =
      safeObject(
        projection.market_health
      );

    const projectionStatus =
      safeText(
        projection.projection_status,
        "unavailable"
      );

    if (
      projectionStatus === "fresh"
    ) {
      return {
        label:
          safeText(
            health.label
            || health.state
            || health.status,
            "Fresh market projection"
          ),

        detail:
          "Current source-backed market data is available.",

        tone:
          "ready"
      };
    }

    if (
      projectionStatus === "stale"
    ) {
      return {
        label:
          "Market data is stale",

        detail:
          "You can inspect it, but OB will not call it current.",

        tone:
          "watch"
      };
    }

    return {
      label:
        "Current market truth is guarded",

      detail:
        safeText(
          projection.reason,
          "OB is waiting for verified market provenance."
        ),

      tone:
        "guarded"
    };
  }


  function paperState(
    mode
  ) {
    const normalized =
      String(
        mode
      ).toLowerCase();

    if (
      normalized.includes(
        "paper"
      )
    ) {
      return {
        label:
          "Paper mode",

        detail:
          "Practice is active and remains separate from live performance."
      };
    }

    return {
      label:
        "Survey mode",

      detail:
        "Observe first. Move into Paper when you want to practice."
    };
  }


  function recentReview() {
    const server =
      safeObject(
        global.OB_SERVER_DATA
      );

    const projection =
      canonicalProjection();

    const summary =
      safeObject(
        projection.review_summary
        || server.review_summary
      );

    const count =
      Number(
        summary.count
        || summary.total
        || summary.items_count
        || 0
      );

    if (
      Number.isFinite(count)
      && count > 0
    ) {
      return {
        label:
          `${count} review item${count === 1 ? "" : "s"}`,

        detail:
          "Review Center has process evidence available.",

        href:
          "/review-center"
      };
    }

    return {
      label:
        "No review item needs the front page",

      detail:
        "Review history stays quiet until something useful exists.",

      href:
        "/review-center"
    };
  }


  function accountHealth(projection) {
    const account = safeObject(projection.account_snapshot);
    const keys = Object.keys(account);

    if (!keys.length) {
      return {
        tone: "guarded",
        label: "Account truth unavailable",
        summary: "No verified account snapshot is attached.",
        facts: []
      };
    }

    const label = safeText(
      account.health || account.status || account.state,
      "Account snapshot available"
    );

    const facts = [];
    [
      ["Equity", account.equity || account.net_liquidation || account.net_liquidation_value],
      ["Cash", account.cash || account.cash_balance || account.available_cash],
      ["Buying power", account.buying_power || account.available_buying_power],
      ["Reserve", account.reserve || account.reserve_cash || account.protected_reserve]
    ].forEach(function (pair) {
      if (pair[1] !== undefined && pair[1] !== null && pair[1] !== "") {
        facts.push({label: pair[0], value: String(pair[1])});
      }
    });

    return {
      tone: "ready",
      label,
      summary: "Verified account snapshot attached.",
      facts: facts.slice(0, 3)
    };
  }


  function riskSummary(projection) {
    const warnings = safeArray(projection.warnings);
    const status = safeText(projection.projection_status, "unavailable");

    if (status !== "fresh") {
      return {
        tone: "watch",
        label: "Guarded",
        summary: "Market truth is not fully current.",
        count: warnings.length
      };
    }

    if (warnings.length) {
      return {
        tone: "watch",
        label: "Watch",
        summary: warnings[0],
        count: warnings.length
      };
    }

    return {
      tone: "ready",
      label: "Calm",
      summary: "No projection warning is demanding attention.",
      count: 0
    };
  }


  function positionSummary(projection) {
    const positions = safeArray(projection.positions_preview);
    return {
      count: positions.length,
      label: positions.length
        ? `${positions.length} active position${positions.length === 1 ? "" : "s"}`
        : "No active position needs the front page",
      items: positions.slice(0, 3).map(function (item) {
        const obj = safeObject(item);
        return {
          symbol: safeText(obj.symbol || obj.ticker, "Position"),
          state: safeText(
            obj.status || obj.state || obj.direction,
            "Open"
          )
        };
      })
    };
  }


  function attentionSummary(projection) {
    const warnings = safeArray(projection.warnings);
    const queue = safeArray(projection.manual_live_queue);
    const review = safeObject(projection.review_summary);
    const count = Number(review.count || review.total || review.items_count || 0);
    const items = [];

    warnings.slice(0, 2).forEach(function (warning) {
      items.push(safeText(warning, ""));
    });

    if (queue.length) {
      items.push(`${queue.length} Manual Live review item${queue.length === 1 ? "" : "s"} waiting.`);
    }

    if (Number.isFinite(count) && count > 0) {
      items.push(`${count} Review Center item${count === 1 ? "" : "s"} available.`);
    }

    return {
      count: items.length,
      items: items.filter(Boolean).slice(0, 3)
    };
  }


  function nextAction(projection, risk, positions, attention) {
    if (risk.tone === "watch") {
      return {
        label: "Review the hold",
        detail: risk.summary,
        href: "/ob/review-center"
      };
    }

    if (attention.count) {
      return {
        label: "Review what changed",
        detail: attention.items[0],
        href: "/ob/review-center"
      };
    }

    if (positions.count) {
      return {
        label: "Check active positions",
        detail: "Nothing is being auto-managed. Review what is already open.",
        href: "/ob/trade-center"
      };
    }

    return {
      label: "Scan the market",
      detail: "Nothing urgent is demanding you.",
      href: "/ob/market-map"
    };
  }


  function briefing(
    projection,
    mode,
    glance
  ) {
    const status =
      safeText(
        projection.projection_status,
        "unavailable"
      );

    if (
      status === "fresh"
      && glance.length
    ) {
      const soulaana = safeObject(projection.soulaana);
      return {
        title:
          safeText(
            soulaana.headline,
            "I found source-backed market activity worth a closer look."
          ),

        summary:
          safeText(
            soulaana.meaning,
            (
              `I checked the research lanes and surfaced ${glance.length} symbol`
              + (glance.length === 1 ? "" : "s")
              + " for investigation. Attention is not a buy or sell instruction."
            )
          )
      };
    }

    if (
      mode.toLowerCase().includes(
        "paper"
      )
    ) {
      return {
        title:
          "Paper is ready when you are.",

        summary:
          (
            "Practice the process without turning "
            + "this Dashboard into a live recommendation screen."
          )
      };
    }

    return {
      title:
        "Nothing needs to be forced.",

      summary:
        (
          "Current market truth is guarded or quiet. "
          + "Open Market Map when you want to explore."
        )
    };
  }


  function project() {
    const projection =
      canonicalProjection();

    const mode =
      selectedMode();

    const glance =
      neutralSymbolFacts(
        projection
      );

    const brief =
      briefing(
        projection,
        mode,
        glance
      );

    const account =
      accountHealth(
        projection
      );

    const risk =
      riskSummary(
        projection
      );

    const positions =
      positionSummary(
        projection
      );

    const attention =
      attentionSummary(
        projection
      );

    return {
      version:
        VERSION,

      role:
        "normal_user",

      mode,

      briefing:
        brief,

      market_glance:
        glance,

      account_health:
        account,

      risk:
        risk,

      positions:
        positions,

      attention:
        attention,

      mode_state:
        paperState(
          mode
        ),

      review:
        recentReview(),

      next_action:
        nextAction(
          projection,
          risk,
          positions,
          attention
        ),

      market_state:
        marketState(
          projection
        ),

      source_state: {
        projection_status:
          safeText(
            projection.projection_status,
            "unavailable"
          ),

        source:
          safeText(
            projection.source,
            "unavailable"
          ),

        as_of:
          safeText(
            projection.as_of,
            "unavailable"
          )
      },

      boundaries:
        BOUNDARIES
    };
  }


  global.OB_USER_DASHBOARD_PROJECTION =
    Object.freeze({
      version:
        VERSION,

      boundaries:
        BOUNDARIES,

      project
    });

})(window);
