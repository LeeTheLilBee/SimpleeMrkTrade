// OBSERVATORY_OBUX057_USER_DASHBOARD_PROJECTION

(function (global) {
  "use strict";

  const ACCOUNT_ENDPOINT =
    "/ob/account-experience.json";


  async function fetchJson(
    url
  ) {
    try {
      const response =
        await fetch(
          url,
          {
            credentials:
              "same-origin",

            headers: {
              Accept:
                "application/json",
            },
          }
        );

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (_) {
      return null;
    }
  }


  function serverData() {
    if (
      global.OB_SERVER_DATA
      && typeof global
        .OB_SERVER_DATA
        === "object"
    ) {
      return global
        .OB_SERVER_DATA;
    }

    return {};
  }


  function cleanArray(
    value
  ) {
    return Array.isArray(
      value
    )
      ? value.filter(
          Boolean
        )
      : [];
  }


  function browserNotificationState() {
    if (
      !(
        "Notification"
        in global
      )
    ) {
      return "unsupported";
    }

    return (
      global
        .Notification
        .permission
      || "default"
    );
  }


  function selectedMode(
    session
  ) {
    if (
      session
      && session.persistent
      && session
        .persistent
        .selectedMode
    ) {
      return session
        .persistent
        .selectedMode;
    }

    return "Survey";
  }


  function accountProfileFromPayload(
    payload
  ) {
    if (
      !payload
      || typeof payload
        !== "object"
    ) {
      return null;
    }

    /*
      NORMAL DASHBOARD BOUNDARY

      The old endpoint may also contain
      owner mission-account policy.

      This projection deliberately consumes
      ONLY the normal/beta user account view.
    */

    return (
      payload.beta_user_account
      || payload.user_account
      || payload.account
      || null
    );
  }


  function modePermissions(
    profile
  ) {
    const raw =
      profile
      && (
        profile.modes
        || profile.mode_permissions
        || profile.mode_chips
      )
        ? (
            profile.modes
            || profile.mode_permissions
            || profile.mode_chips
          )
        : [];

    if (
      !Array.isArray(
        raw
      )
    ) {
      return [];
    }

    return raw.map(
      function (
        item
      ) {
        if (
          typeof item
          === "string"
        ) {
          return {
            name: item,
            state:
              "unknown",
          };
        }

        return {
          name:
            item.name
            || item.label
            || item.mode
            || "Unknown",

          state:
            item.state
            || item.status
            || (
              item.locked
                ? "locked"
                : (
                    item.active
                      ? "active"
                      : "unknown"
                  )
            ),
        };
      }
    );
  }


  function sourceBackedCandidates(
    data
  ) {
    const possible = [
      data.dashboard_candidates,
      data.candidates,
      data.candidate_cards,
      data.market_candidates,
      data.market_map
        && data.market_map.candidates,
      data.options_projection
        && data.options_projection.candidates,
    ];

    for (
      const value
      of possible
    ) {
      if (
        Array.isArray(
          value
        )
        && value.length
      ) {
        return value;
      }
    }

    return [];
  }


  function sourceBackedReviews(
    data
  ) {
    const possible = [
      data.reviews,
      data.review_center,
      data.final_reviews,
      data.outcomes,
    ];

    for (
      const value
      of possible
    ) {
      if (
        Array.isArray(
          value
        )
        && value.length
      ) {
        return value;
      }

      if (
        value
        && Array.isArray(
          value.items
        )
        && value.items.length
      ) {
        return value.items;
      }
    }

    return [];
  }


  function sourceBackedPositions(
    data
  ) {
    const possible = [
      data.open_positions,
      data.positions,
      data.active_positions,
      data.position_monitor,
    ];

    for (
      const value
      of possible
    ) {
      if (
        Array.isArray(
          value
        )
        && value.length
      ) {
        return value;
      }

      if (
        value
        && Array.isArray(
          value.items
        )
        && value.items.length
      ) {
        return value.items;
      }
    }

    return [];
  }


  function candidateCard(
    candidate
  ) {
    const symbol =
      String(
        candidate.symbol
        || candidate.ticker
        || ""
      ).toUpperCase();

    const thesis =
      candidate.thesis
      || candidate.direction
      || candidate.bias
      || "Research available";

    let optionCount = null;

    if (
      Number.isFinite(
        Number(
          candidate
            .viable_option_count
        )
      )
    ) {
      optionCount =
        Number(
          candidate
            .viable_option_count
        );
    } else if (
      Array.isArray(
        candidate.options
      )
    ) {
      optionCount =
        candidate
          .options
          .length;
    } else if (
      Array.isArray(
        candidate.contracts
      )
    ) {
      optionCount =
        candidate
          .contracts
          .length;
    }

    const liquidity =
      candidate.liquidity_label
      || candidate.option_liquidity
      || candidate.liquidity
      || null;

    return {
      symbol:
        symbol
        || "Symbol unavailable",

      thesis:
        String(
          thesis
        ),

      options:
        optionCount === null
          ? null
          : (
              optionCount
              + " viable contract"
              + (
                  optionCount === 1
                    ? ""
                    : "s"
                )
            ),

      liquidity:
        liquidity
          ? String(
              liquidity
            )
          : null,

      href:
        symbol
          ? (
              "/ob/symbol/"
              + encodeURIComponent(
                  symbol
                )
            )
          : "/ob/market-map",

      source:
        candidate.source
        || candidate.provenance
        || "canonical candidate projection",
    };
  }


  function buildSince(
    session,
    data
  ) {
    const items = [];

    const recent =
      session
      && session.persistent
        ? cleanArray(
            session
              .persistent
              .recentSessions
          )
        : [];

    const feedback =
      session
      && session.persistent
        ? cleanArray(
            session
              .persistent
              .feedback
          )
        : [];

    const reviews =
      sourceBackedReviews(
        data
      );

    if (
      reviews.length
    ) {
      items.push(
        {
          kind:
            "review",

          title:
            reviews.length
            + " review item"
            + (
                reviews.length
                  === 1
                  ? ""
                  : "s"
              )
            + " available",

          detail:
            "Open Review Center for process and outcome truth.",

          href:
            "/review-center",

          source:
            "review projection",
        }
      );
    }

    if (
      feedback.length
    ) {
      items.push(
        {
          kind:
            "feedback",

          title:
            feedback.length
            + " beta feedback note"
            + (
                feedback.length
                  === 1
                  ? ""
                  : "s"
              )
            + " saved",

          detail:
            "Your local beta feedback queue is available in My OB.",

          href:
            null,

          source:
            "OB session state",
        }
      );
    }

    if (
      recent.length
    ) {
      const last =
        recent[0];

      items.push(
        {
          kind:
            "session",

          title:
            "Your last OB session has a closeout record",

          detail:
            [
              last.lastRoom,
              last.mode,
            ]
              .filter(
                Boolean
              )
              .join(
                " · "
              )
            || "Session record available",

          href:
            null,

          source:
            "OB session state",
        }
      );
    }

    if (
      !items.length
    ) {
      items.push(
        {
          kind:
            "empty",

          title:
            "No source-backed changes to report yet",

          detail:
            "Soulaana won’t invent activity just to fill the page.",

          href:
            null,

          source:
            "canonical empty state",
        }
      );
    }

    return items.slice(
      0,
      4
    );
  }


  function buildActivity(
    data
  ) {
    const positions =
      sourceBackedPositions(
        data
      );

    const reviews =
      sourceBackedReviews(
        data
      );

    const items = [];

    if (
      positions.length
    ) {
      items.push(
        {
          kind:
            "positions",

          count:
            positions.length,

          title:
            positions.length
            + " tracked position"
            + (
                positions.length
                  === 1
                  ? ""
                  : "s"
              ),

          detail:
            "Open Trade Center to manage the OB lifecycle. External brokerage state is not implied.",

          href:
            "/trade-center",

          source:
            "position projection",
        }
      );
    }

    if (
      reviews.length
    ) {
      items.push(
        {
          kind:
            "reviews",

          count:
            reviews.length,

          title:
            reviews.length
            + " review item"
            + (
                reviews.length
                  === 1
                  ? ""
                  : "s"
              ),

          detail:
            "Review process quality, outcome, and Negative Dive evidence.",

          href:
            "/review-center",

          source:
            "review projection",
        }
      );
    }

    if (
      !items.length
    ) {
      items.push(
        {
          kind:
            "empty",

          count: 0,

          title:
            "No open source-backed work",

          detail:
            "Research in Market Map or review saved activity when it exists.",

          href:
            "/ob/market-map",

          source:
            "canonical empty state",
        }
      );
    }

    return items;
  }


  function soulaanaSummary(
    mode,
    activity,
    market
  ) {
    if (
      mode === "Survey"
    ) {
      if (
        market.length
      ) {
        return (
          "Survey is open. "
          + "I found source-backed names worth studying; "
          + "nothing here asks you to trade."
        );
      }

      return (
        "Survey is open. "
        + "I’ll keep this observational until "
        + "canonical market candidates arrive."
      );
    }

    if (
      mode === "Paper"
    ) {
      return (
        "Paper mode is active. "
        + "Practice stays separate from official live performance."
      );
    }

    if (
      mode === "Manual Live"
    ) {
      return (
        "Manual Live is owner-supervised: "
        + "OB can prepare, alert, track, and review; "
        + "the owner chooses and places the trade externally."
      );
    }

    if (
      mode === "Hybrid"
    ) {
      return (
        "Hybrid may narrow objective options, "
        + "but the user still chooses the contract "
        + "and execution remains separately gated."
      );
    }

    return (
      "Automated mode is locked. "
      + "This Dashboard does not create an execution path."
    );
  }


  async function project() {
    const session =
      global.OBSessionState
        ? global
            .OBSessionState
            .snapshot()
        : null;

    const data =
      serverData();

    const payload =
      await fetchJson(
        ACCOUNT_ENDPOINT
      );

    const profile =
      accountProfileFromPayload(
        payload
      );

    const mode =
      selectedMode(
        session
      );

    const permissions =
      modePermissions(
        profile
      );

    const market =
      sourceBackedCandidates(
        data
      )
        .map(
          candidateCard
        )
        .slice(
          0,
          4
        );

    const activity =
      buildActivity(
        data
      );

    const notification =
      session
      && session.persistent
        ? (
            session
              .persistent
              .notificationReadiness
            || {}
          )
        : {};

    const browserPermission =
      browserNotificationState();

    const snapshotCards = [
      {
        label:
          "Access",

        value:
          profile
          && (
            profile.title
            || profile.subtitle
          )
            ? (
                profile.title
                || profile.subtitle
              )
            : "OB user",

        state:
          profile
            ? "source-backed"
            : "guarded",

        detail:
          profile
          && profile.subtitle
            ? profile.subtitle
            : (
                "Account detail source unavailable; "
                + "normal-user boundary remains enforced."
              ),

        source:
          profile
            ? ACCOUNT_ENDPOINT
            : "guarded projection",
      },

      {
        label:
          "Mode",

        value:
          mode,

        state:
          mode === "Automated"
            ? "locked"
            : "active",

        detail:
          permissions.length
            ? permissions
                .map(
                  function (
                    item
                  ) {
                    return (
                      item.name
                      + ": "
                      + item.state
                    );
                  }
                )
                .join(
                  " · "
                )
            : "Mode permission detail unavailable.",

        source:
          permissions.length
            ? ACCOUNT_ENDPOINT
            : "OB session state",
      },

      {
        label:
          "Alerts",

        value:
          browserPermission
            === "granted"
              ? "Browser allowed"
              : (
                  browserPermission
                    === "denied"
                      ? "Browser blocked"
                      : (
                          browserPermission
                            === "unsupported"
                              ? "Browser unsupported"
                              : "Browser not decided"
                        )
                ),

        state:
          browserPermission
            === "granted"
              ? "ready"
              : "attention",

        detail:
          notification.email
          && notification.email
            !== "unknown"
              ? (
                  "Email: "
                  + notification.email
                )
              : (
                  "Email delivery status unavailable "
                  + "until a canonical source says otherwise."
                ),

        source:
          "browser permission + OB notification state",
      },

      {
        label:
          "Private Beta",

        value:
          document.body
            ? (
                document.body
                  .dataset
                  .obBuild
                || "Build unavailable"
              )
            : "Build unavailable",

        state:
          "beta",

        detail:
          document.body
            ? (
                "Guide "
                + (
                    document.body
                      .dataset
                      .obSopVersion
                    || "version unavailable"
                  )
              )
            : "Guide version unavailable",

        source:
          "deployed UI build identity",
      },
    ];

    return {
      generatedAt:
        new Date()
          .toISOString(),

      profile,

      mode,

      permissions,

      snapshotCards,

      since:
        buildSince(
          session,
          data
        ),

      activity,

      market,

      summary:
        soulaanaSummary(
          mode,
          activity,
          market
        ),

      notification: {
        browser:
          browserPermission,

        inApp:
          notification.inApp
          || "unknown",

        email:
          notification.email
          || "unknown",

        lastDelivery:
          notification.lastDelivery
          || null,

        source:
          notification.source
          || "not_connected",
      },

      recentSessions:
        session
        && session.persistent
          ? cleanArray(
              session
                .persistent
                .recentSessions
            )
          : [],

      feedback:
        session
        && session.persistent
          ? cleanArray(
              session
                .persistent
                .feedback
            )
          : [],

      boundaries: {
        missionAccountsOnUserDashboard:
          false,

        brokerExecution:
          false,

        automaticContractSelection:
          false,

        automaticExecution:
          false,

        automatedModeLocked:
          true,

        checkInChangesMarketTruth:
          false,
      },
    };
  }


  global.OBDashboardProjection =
    Object.freeze(
      {
        project,

        fetchAccountContext:
          async function () {
            return accountProfileFromPayload(
              await fetchJson(
                ACCOUNT_ENDPOINT
              )
            );
          },
      }
    );

})(window);
