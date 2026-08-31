// OBUX086–090 — OWNER CAPITAL LANES CONTRACT
(() => {
  "use strict";

  const VERSION =
    "OBUX086_090_OWNER_CAPITAL_LANES_CONTRACT";

  /*
    Capital Lanes are OWNER-ONLY.

    Normal OB user surfaces do not load this contract and do not
    receive these lane definitions.

    This contract is read-only intelligence.
    It cannot move capital or place a broker order.
  */

  const ENDPOINTS = Object.freeze({
    engine_trust:
      "/ob/engine-feed-trust-labels.json",

    manual_live_readiness:
      "/ob/manual-live-operator-confidence-readiness-checkpoint.json",

    private_beta:
      "/ob/private-beta-launch-control.json"
  });


  const BOUNDARIES = Object.freeze({
    owner_only:
      true,

    capital_lanes_owner_dashboard_only:
      true,

    non_owner_capital_lane_delivery:
      false,

    read_only_intelligence:
      true,

    lane_selection_changes_context_only:
      true,

    broker_api_enabled:
      false,

    broker_order_submission_enabled:
      false,

    real_capital_movement_enabled:
      false,

    automatic_contract_selection_enabled:
      false,

    auto_execution_enabled:
      false,

    live_auto_locked:
      true
  });


  const POLICY_CAPITAL_LANES = Object.freeze([
    {
      lane_id:
        "trust",

      account_id:
        "ob_acct_trust",

      label:
        "Trust",

      display_label:
        "Trust",

      purpose:
        "Protect and grow trust capital without treating protected money like ordinary trading capital.",

      risk_profile:
        "Protected / conservative",

      allowed_modes: [
        "Survey",
        "Paper",
        "Manual Live Level 1 · owner only"
      ],

      capital_goal:
        "Protected family capital and future mission dispersal.",

      current_status:
        "Policy defined",

      next_action:
        "Protect the floor first. Use verified capital truth only."
    },

    {
      lane_id:
        "personal",

      account_id:
        "ob_acct_personal",

      label:
        "Personal",

      display_label:
        "Personal",

      purpose:
        "Owner learning, personal capital growth, and controlled owner trading review.",

      risk_profile:
        "Moderate / capped",

      allowed_modes: [
        "Survey",
        "Paper",
        "Manual Live Level 1 · owner only"
      ],

      capital_goal:
        "Owner liquidity and skill-building without borrowing from protected lanes.",

      current_status:
        "Policy defined",

      next_action:
        "Keep personal capital separate from protected and business capital."
    },

    {
      lane_id:
        "simplee_world",

      account_id:
        "ob_acct_simplee_world",

      label:
        "Simplee World",

      display_label:
        "Simplee World",

      purpose:
        "Build parent-company capital for the wider Simplee ecosystem.",

      risk_profile:
        "Growth / controlled",

      allowed_modes: [
        "Survey",
        "Paper",
        "Manual Live Level 1 · owner only"
      ],

      capital_goal:
        "Business operating and expansion capital.",

      current_status:
        "Policy defined",

      next_action:
        "Keep business purpose and receipts explicit."
    },

    {
      lane_id:
        "atm",

      account_id:
        "ob_acct_atm",

      label:
        "ATM",

      display_label:
        "SimpleeOnTheGo / ATM",

      purpose:
        "Build capital for ATM route acquisition, vault cash, repair, and expansion.",

      risk_profile:
        "Moderate → conservative near deployment",

      allowed_modes: [
        "Survey",
        "Paper",
        "Manual Live Level 1 · owner only"
      ],

      capital_goal:
        "ATM acquisition and operating reserve.",

      current_status:
        "Policy defined",

      next_action:
        "Do not call a milestone reached until verified capital says it is."
    },

    {
      lane_id:
        "apartment",

      account_id:
        "ob_acct_apartment",

      label:
        "The Grounds",

      display_label:
        "The Grounds / Apartment",

      purpose:
        "Build and protect future property acquisition reserves.",

      risk_profile:
        "Protected / conservative",

      allowed_modes: [
        "Survey",
        "Paper",
        "Manual Live Level 1 · owner only when intentionally enabled"
      ],

      capital_goal:
        "Acquisition, inspection, closing, repair, and reserve readiness.",

      current_status:
        "Policy defined",

      next_action:
        "Keep preservation ahead of aggressive growth."
    },

    {
      lane_id:
        "proof_demo",

      account_id:
        "ob_acct_proof_demo",

      label:
        "Proof / Demo",

      display_label:
        "Proof / Demo",

      purpose:
        "Demonstrate OB safely without exposing private capital or identities.",

      risk_profile:
        "Zero real-capital risk",

      allowed_modes: [
        "Survey",
        "Paper",
        "Demo"
      ],

      capital_goal:
        "No real capital.",

      current_status:
        "Demo only",

      next_action:
        "Use only for safe private proof and beta demonstration."
    }
  ]);


  const state = {
    status:
      "guarded_local_policy",

    hydrated:
      false,

    hydrated_at:
      null,

    sources:
      {},

    errors:
      [],

    contract:
      null
  };


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


  const safeArray = (
    value
  ) => (
    Array.isArray(
      value
    )
      ? value
      : []
  );


  const sourceLooksVerified = (
    payload
  ) => {
    if (
      !payload
      || typeof payload !== "object"
    ) {
      return false;
    }

    const source =
      safeText(
        payload.source,
        ""
      ).toLowerCase();

    if (
      source.includes(
        "fallback"
      )
      || source.includes(
        "preview"
      )
      || source.includes(
        "demo"
      )
    ) {
      return false;
    }

    if (
      payload.verified
      === false
    ) {
      return false;
    }

    return true;
  };


  const fetchSource = async (
    name,
    url
  ) => {
    try {
      const response =
        await fetch(
          url,
          {
            credentials:
              "same-origin",

            headers: {
              "Accept":
                "application/json"
            }
          }
        );

      let payload = {};

      try {
        payload =
          await response.json();
      } catch (_) {
        payload = {};
      }

      if (
        !response.ok
      ) {
        return {
          name,
          url,
          status:
            "guarded",

          http_status:
            response.status,

          verified:
            false,

          payload:
            null,

          error:
            `HTTP ${response.status}`
        };
      }

      return {
        name,
        url,

        status:
          "available",

        http_status:
          response.status,

        verified:
          sourceLooksVerified(
            payload
          ),

        payload,

        error:
          null
      };

    } catch (
      error
    ) {
      return {
        name,
        url,

        status:
          "unavailable",

        http_status:
          null,

        verified:
          false,

        payload:
          null,

        error:
          (
            error
            && error.message
              ? error.message
              : "fetch failed"
          )
      };
    }
  };


  const normalizeLane = (
    lane
  ) => ({
    ...lane,

    allowed_modes:
      safeArray(
        lane.allowed_modes
      ),

    actual_capital_known:
      false,

    actual_capital_value:
      null,

    capital_progress_known:
      false,

    capital_progress_percent:
      null,

    verified_snapshot:
      false,

    needs_attention:
      false
  });


  const capitalLaneSnapshot = () => {
    /*
      A future verified owner-only source may populate:

      window.OB_OWNER_CAPITAL_LANE_SNAPSHOT = {
        verified: true,
        lanes: [...]
      }

      No generic user account endpoint is consumed here.
    */

    const snapshot =
      window
        .OB_OWNER_CAPITAL_LANE_SNAPSHOT;

    if (
      !snapshot
      || snapshot.verified
        !== true
      || !Array.isArray(
        snapshot.lanes
      )
    ) {
      return {
        verified:
          false,

        lanes:
          []
      };
    }

    return {
      verified:
        true,

      lanes:
        snapshot.lanes
    };
  };


  const capitalLanes = () => {
    const base =
      POLICY_CAPITAL_LANES
        .map(
          normalizeLane
        );

    const snapshot =
      capitalLaneSnapshot();

    if (
      !snapshot.verified
    ) {
      return base;
    }

    const verifiedById =
      new Map(
        snapshot
          .lanes
          .map(
            function (
              item
            ) {
              return [
                safeText(
                  item.lane_id,
                  ""
                ),
                item
              ];
            }
          )
      );

    return base.map(
      function (
        lane
      ) {
        const live =
          verifiedById.get(
            lane.lane_id
          );

        if (
          !live
        ) {
          return lane;
        }

        const capitalKnown =
          live.actual_capital_known
            === true
          && Number.isFinite(
            Number(
              live.actual_capital_value
            )
          );

        const progressKnown =
          live.capital_progress_known
            === true
          && Number.isFinite(
            Number(
              live.capital_progress_percent
            )
          );

        return {
          ...lane,

          verified_snapshot:
            true,

          actual_capital_known:
            capitalKnown,

          actual_capital_value:
            capitalKnown
              ? Number(
                  live.actual_capital_value
                )
              : null,

          capital_progress_known:
            progressKnown,

          capital_progress_percent:
            progressKnown
              ? Number(
                  live.capital_progress_percent
                )
              : null,

          current_status:
            safeText(
              live.current_status,
              lane.current_status
            ),

          next_action:
            safeText(
              live.next_action,
              lane.next_action
            ),

          needs_attention:
            live.needs_attention
              === true
        };
      }
    );
  };


  const trustSummary = () => {
    const source =
      state.sources.engine_trust
      || {};

    const payload =
      source.payload
      || {};

    const trust =
      payload.trust
      || {};

    const verified =
      source.verified
      === true;

    const freshness =
      (
        verified
        && Number.isFinite(
          Number(
            payload.freshness_score
          )
        )
      )
        ? Number(
            payload.freshness_score
          )
        : null;

    const level =
      verified
        ? safeText(
            trust.level,
            "unknown"
          ).toLowerCase()
        : "guarded";

    return {
      verified,

      label:
        verified
          ? safeText(
              trust.label
              || payload.display_label,
              "Verified source"
            )
          : "Guarded · verify source",

      level,

      freshness_score:
        freshness,

      needs_attention:
        (
          !verified
          || [
            "fallback",
            "missing",
            "stale",
            "guarded"
          ].includes(
            level
          )
        ),

      explanation:
        verified
          ? (
              "The engine-trust layer supplied "
              + "a verified owner-wide trust state."
            )
          : (
              "Owner Dashboard does not have "
              + "verified engine-trust truth yet."
            )
    };
  };


  const readinessSummary = () => {
    const source =
      state
        .sources
        .manual_live_readiness
      || {};

    const payload =
      source.payload
      || {};

    const scorecard =
      payload.readiness_scorecard
      || {};

    const verified =
      source.verified
      === true;

    const blockers =
      verified
        ? safeArray(
            payload
              .remaining_live_blockers
          ).map(
            function (
              item
            ) {
              return {
                id:
                  safeText(
                    item.blocker_id,
                    "blocker"
                  ),

                label:
                  safeText(
                    item.label,
                    "Readiness blocker"
                  ),

                reason:
                  safeText(
                    item.reason,
                    "Readiness work remains."
                  ),

                status:
                  safeText(
                    item.status,
                    "blocking"
                  )
              };
            }
          )
        : [];

    return {
      verified,

      label:
        verified
          ? safeText(
              scorecard.readiness_label,
              "Owner confidence evidence available"
            )
          : "Guarded · readiness not verified",

      score:
        (
          verified
          && Number.isFinite(
            Number(
              scorecard.readiness_score
            )
          )
        )
          ? Number(
              scorecard.readiness_score
            )
          : null,

      blockers,

      needs_attention:
        (
          !verified
          || blockers.length > 0
        ),

      real_manual_live_ready:
        false,

      broker_order_submission_enabled:
        false,

      automatic_contract_selection_enabled:
        false,

      auto_execution_enabled:
        false,

      live_auto_locked:
        true
    };
  };


  const betaSummary = () => {
    const source =
      state.sources.private_beta
      || {};

    const payload =
      source.payload
      || {};

    const verified =
      source.verified
      === true;

    const raw =
      payload.owner_go_no_go_status
      || payload.owner_decision
      || payload.launch_status
      || payload.status;

    return {
      verified,

      label:
        verified
          ? safeText(
              raw,
              "Verified private-beta evidence available"
            )
          : "Guarded · beta evidence not verified",

      private_only:
        true,

      public_launch_enabled:
        false
    };
  };


  const historySummary = () => {
    const snapshot =
      window
        .OB_OWNER_CHANGE_HISTORY;

    if (
      snapshot
      && snapshot.verified
        === true
      && Array.isArray(
        snapshot.items
      )
    ) {
      return {
        verified:
          true,

        items:
          snapshot
            .items
            .slice(
              0,
              6
            )
      };
    }

    return {
      verified:
        false,

      items: [
        {
          title:
            "No verified owner-change history yet",

          detail:
            (
              "I will not invent a "
              + "'since you were here' story."
            )
        }
      ]
    };
  };


  const patternSummary = (
    lanes
  ) => {
    const verified =
      lanes.filter(
        function (
          lane
        ) {
          return (
            lane.verified_snapshot
          );
        }
      );

    if (
      !verified.length
    ) {
      return {
        verified:
          false,

        items: [
          {
            title:
              "No verified cross-lane pattern yet",

            detail:
              (
                "Policy definitions are not "
                + "performance evidence."
              )
          }
        ]
      };
    }

    const attention =
      verified.filter(
        function (
          lane
        ) {
          return (
            lane.needs_attention
          );
        }
      ).length;

    return {
      verified:
        true,

      items: [
        {
          title:
            attention
              ? (
                  `${attention} verified Capital Lane(s) `
                  + "need owner attention"
                )
              : (
                  "No verified Capital Lane "
                  + "is flagging owner attention"
                ),

          detail:
            (
              "This statement comes only "
              + "from verified owner lane truth."
            )
        }
      ]
    };
  };


  const ownerAttention = (
    lanes,
    trust,
    readiness,
    beta
  ) => {
    const items = [];

    lanes
      .filter(
        function (
          lane
        ) {
          return (
            lane.verified_snapshot
            && lane.needs_attention
          );
        }
      )
      .forEach(
        function (
          lane
        ) {
          items.push({
            priority:
              "high",

            source:
              "verified Capital Lane",

            title:
              `${lane.display_label} needs you`,

            detail:
              lane.next_action
          });
        }
      );

    if (
      trust.needs_attention
    ) {
      items.push({
        priority:
          "high",

        source:
          "engine trust",

        title:
          "Verify the picture Soulaana is using",

        detail:
          trust.explanation
      });
    }

    if (
      readiness.needs_attention
    ) {
      items.push({
        priority:
          "medium",

        source:
          "Manual Live readiness",

        title:
          "Manual Live remains guarded",

        detail:
          readiness.verified
            ? (
                readiness.blockers.length
                  ? (
                      `${readiness.blockers.length} `
                      + "verified blocker(s) remain."
                    )
                  : (
                      "Confidence evidence exists, "
                      + "but it is not trading permission."
                    )
              )
            : (
                "Readiness evidence is not verified "
                + "on this surface."
              )
      });
    }

    if (
      !beta.verified
    ) {
      items.push({
        priority:
          "medium",

        source:
          "private beta",

        title:
          "Do not infer beta expansion readiness",

        detail:
          (
            "Private-beta launch evidence "
            + "is not verified here yet."
          )
      });
    }

    if (
      !items.length
    ) {
      items.push({
        priority:
          "calm",

        source:
          "owner intelligence",

        title:
          "Nothing verified needs you right now",

        detail:
          (
            "Soulaana can keep watching "
            + "without manufacturing urgency."
          )
      });
    }

    /*
      ADHD-friendly owner surface:
      show at most three things up front.
    */
    return items.slice(
      0,
      3
    );
  };


  const buildContract = () => {
    const lanes =
      capitalLanes();

    const trust =
      trustSummary();

    const readiness =
      readinessSummary();

    const beta =
      betaSummary();

    const history =
      historySummary();

    const patterns =
      patternSummary(
        lanes
      );

    const attention =
      ownerAttention(
        lanes,
        trust,
        readiness,
        beta
      );

    const criticalVerified =
      (
        trust.verified
        && readiness.verified
        && beta.verified
      );

    return {
      version:
        VERSION,

      role:
        "owner_dashboard",

      owner_only:
        true,

      capital_lanes:
        lanes,

      owner_attention:
        attention,

      trust,

      readiness,

      beta,

      patterns,

      since_you_were_here:
        history,

      source_state: {
        engine_trust:
          state.sources.engine_trust
          || null,

        manual_live_readiness:
          state
            .sources
            .manual_live_readiness
          || null,

        private_beta:
          state.sources.private_beta
          || null
      },

      interpretation_state: {
        all_critical_sources_verified:
          criticalVerified,

        may_claim_cross_lane_performance_patterns:
          patterns.verified,

        may_claim_change_history:
          history.verified,

        may_claim_capital_progress:
          lanes.some(
            function (
              lane
            ) {
              return (
                lane
                  .capital_progress_known
              );
            }
          ),

        no_action_needed:
          (
            criticalVerified
            && attention.every(
              function (
                item
              ) {
                return (
                  item.priority
                    !== "high"
                  && item.priority
                    !== "medium"
                );
              }
            )
          )
      },

      boundaries:
        BOUNDARIES
    };
  };


  const hydrate = async () => {
    state.status =
      "hydrating";

    state.errors =
      [];

    const [
      engineTrust,
      manualLiveReadiness,
      privateBeta
    ] = await Promise.all([
      fetchSource(
        "engine_trust",
        ENDPOINTS.engine_trust
      ),

      fetchSource(
        "manual_live_readiness",
        ENDPOINTS.manual_live_readiness
      ),

      fetchSource(
        "private_beta",
        ENDPOINTS.private_beta
      )
    ]);

    state.sources = {
      engine_trust:
        engineTrust,

      manual_live_readiness:
        manualLiveReadiness,

      private_beta:
        privateBeta
    };

    Object
      .values(
        state.sources
      )
      .forEach(
        function (
          source
        ) {
          if (
            source
            && source.error
          ) {
            state.errors.push(
              `${source.name}: ${source.error}`
            );
          }
        }
      );

    state.hydrated =
      true;

    state.hydrated_at =
      new Date()
        .toISOString();

    state.status =
      state.errors.length
        ? "hydrated_guarded"
        : "hydrated";

    state.contract =
      buildContract();

    window.dispatchEvent(
      new CustomEvent(
        "ob:owner-capital-lanes-ready",
        {
          detail:
            state.contract
        }
      )
    );

    return state.contract;
  };


  state.contract =
    buildContract();


  window
    .OB_OWNER_DASHBOARD_CONTRACT_V21 =
      Object.freeze({
        version:
          VERSION,

        endpoints:
          ENDPOINTS,

        boundaries:
          BOUNDARIES,

        getState:
          () => state,

        getContract:
          () => (
            state.contract
            || buildContract()
          ),

        buildContract,

        hydrate
      });

})();
