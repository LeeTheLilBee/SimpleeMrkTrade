
// OBUX091–095 — OWNER INTELLIGENCE COCKPIT CONTRACT
//
// OWNER ONLY.
//
// Existing canonical engine projection is the market-truth authority.
// This contract interprets; it does not create a second engine.
//
// Critical:
//   ranking evidence may be displayed.
//   source-provided candidate status may be displayed.
//   OB does NOT silently select an option contract for execution.
//
(() => {
  "use strict";

  const VERSION =
    "OBUX091_095_OWNER_INTELLIGENCE_CONTRACT";

  const ENDPOINTS =
    Object.freeze({
      engine_trust:
        "/ob/engine-feed-trust-labels.json",

      manual_live_readiness:
        "/ob/manual-live-operator-confidence-readiness-checkpoint.json",

      private_beta:
        "/ob/private-beta-launch-control.json"
    });


  const BOUNDARIES =
    Object.freeze({
      owner_only:
        true,

      owner_research_only:
        true,

      capital_lanes_owner_dashboard_only:
        true,

      non_owner_capital_lane_delivery:
        false,

      non_owner_candidate_delivery:
        false,

      read_only_intelligence:
        true,

      lane_selection_changes_context_only:
        true,

      candidate_display_does_not_authorize_trade:
        true,

      ranked_contract_is_not_selected_contract:
        true,

      selection_authority:
        "OWNER",

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


  const POLICY_CAPITAL_LANES =
    Object.freeze([
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
    sources:
      {},

    errors:
      [],

    contract:
      null
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


  const safeObject = (
    value
  ) => (
    value
    && typeof value === "object"
    && !Array.isArray(value)
      ? value
      : {}
  );


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


  const num = (
    value
  ) => {
    const parsed =
      Number(
        value
      );

    return Number.isFinite(
      parsed
    )
      ? parsed
      : null;
  };


  const sourceLooksVerified = (
    payload
  ) => {
    // HTTP success and self-reported verification do not authenticate source
    // provenance. No trusted server-side proof is consumed by this browser
    // contract; labels must remain independently unverified.
    void payload;
    return false;
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

      const usable =
        (
          response.ok
          && payload
          && typeof payload === "object"
          && !Array.isArray(payload)
          && Object.keys(payload).length > 0
        );

      return {
        name,
        url,

        status:
          usable
            ? "available"
            : "guarded",

        source_observed:
          usable,

        verified:
          (
            usable
            && sourceLooksVerified(
              payload
            )
          ),

        independent_provenance_authenticated:
          false,

        payload:
          usable
            ? payload
            : null
      };

    } catch (
      error
    ) {
      return {
        name,
        url,

        status:
          "unavailable",

        verified:
          false,

        source_observed:
          false,

        independent_provenance_authenticated:
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


  const canonicalProjection = () => {
    const server =
      safeObject(
        window.OB_SERVER_DATA
      );

    return safeObject(
      server.canonical_web_projection
      || server.engine_feed_v25
      || window.OB_ENGINE_FEED_SNAPSHOT_V25
    );
  };


  const currentMarketVerified = (
    projection
  ) => (
    projection.current_eligible === true
    && projection.display_eligible === true
    && projection.projection_status === "fresh"
  );


  const candidateSourceArray = (
    projection
  ) => {
    const candidates = [
      projection.candidates_preview,
      projection.candidates,
      projection.watched_candidates
    ];

    for (
      const value
      of candidates
    ) {
      if (
        Array.isArray(value)
        && value.length
      ) {
        return value;
      }
    }

    return [];
  };


  const optionSourceArray = (
    projection
  ) => {
    const optionsProjection =
      safeObject(
        projection.options_projection
      );

    const ranked =
      safeArray(
        optionsProjection.ranked_contracts
        || projection.ranked_contracts
      );

    if (
      ranked.length
    ) {
      return ranked;
    }

    return safeArray(
      optionsProjection.research_contracts
      || projection.research_contracts
      || projection.options
    );
  };


  const normalizeOption = (
    raw,
    sourceVerified,
    index
  ) => {
    const item =
      safeObject(
        raw
      );

    return {
      source_order:
        index + 1,

      symbol:
        safeText(
          item.symbol
          || item.underlying
          || item.ticker,
          ""
        ).toUpperCase(),

      contract_symbol:
        safeText(
          item.contract_symbol
          || item.option_symbol
          || item.occ_symbol,
          ""
        ),

      option_type:
        safeText(
          item.option_type
          || item.type
          || item.right,
          "Unavailable"
        ),

      strike:
        num(
          item.strike
        ),

      expiration:
        safeText(
          item.expiration
          || item.expiry
          || item.expiration_date,
          "Unavailable"
        ),

      bid:
        num(
          item.bid
        ),

      ask:
        num(
          item.ask
        ),

      spread:
        num(
          item.spread
        ),

      volume:
        num(
          item.volume
        ),

      open_interest:
        num(
          item.open_interest
          || item.oi
        ),

      implied_volatility:
        num(
          item.implied_volatility
          || item.iv
        ),

      delta:
        num(
          item.delta
        ),

      gamma:
        num(
          item.gamma
        ),

      theta:
        num(
          item.theta
        ),

      vega:
        num(
          item.vega
        ),

      source_rank:
        num(
          item.rank
          || item.score_rank
        ),

      source_verified:
        sourceVerified === true,

      selection_authority:
        "OWNER",

      automatically_selected:
        false
    };
  };


  const optionContractsBySymbol = (
    projection
  ) => {
    const verified =
      currentMarketVerified(
        projection
      );

    const map =
      new Map();

    optionSourceArray(
      projection
    )
      .forEach(
        function (
          raw,
          index
        ) {
          const contract =
            normalizeOption(
              raw,
              verified,
              index
            );

          if (
            !contract.symbol
          ) {
            return;
          }

          const current =
            map.get(
              contract.symbol
            )
            || [];

          current.push(
            contract
          );

          map.set(
            contract.symbol,
            current
          );
        }
      );

    return map;
  };


  const candidateBucket = (
    raw,
    verified
  ) => {
    const item =
      safeObject(
        raw
      );

    const stateText =
      [
        item.status,
        item.state,
        item.priority,
        item.decision,
        item.recommendation_state,
        item.candidate_state
      ]
        .filter(
          Boolean
        )
        .join(
          " "
        )
        .toLowerCase();

    if (
      !verified
      || /(reject|blocked|invalid|guarded|stale|hold|not[_ -]?yet)/i
        .test(
          stateText
        )
    ) {
      return "not_yet";
    }

    if (
      item.actionable === true
      || /(approved|ready|qualified|high|top|now)/i
        .test(
          stateText
        )
    ) {
      return "now";
    }

    return "watch";
  };


  const normalizeCandidate = (
    raw,
    projection,
    optionsMap,
    index
  ) => {
    const item =
      safeObject(
        raw
      );

    const verified =
      currentMarketVerified(
        projection
      );

    const symbol =
      safeText(
        item.symbol
        || item.ticker
        || item.underlying,
        ""
      ).toUpperCase();

    const contracts =
      symbol
        ? (
            optionsMap.get(
              symbol
            )
            || []
          )
        : [];

    return {
      source_order:
        index + 1,

      symbol:
        symbol
        || "Unavailable",

      verified,

      freshness:
        safeText(
          projection.freshness,
          "unavailable"
        ),

      source:
        safeText(
          item.source
          || item.provenance
          || projection.source,
          "unavailable"
        ),

      bucket:
        candidateBucket(
          item,
          verified
        ),

      direction:
        safeText(
          item.direction
          || item.bias
          || item.side,
          "Direction unavailable"
        ),

      thesis:
        safeText(
          item.thesis
          || item.reason
          || item.summary
          || item.setup,
          "Source did not provide a thesis."
        ),

      setup:
        safeText(
          item.setup
          || item.pattern
          || item.signal,
          "Setup unavailable"
        ),

      catalyst:
        safeText(
          item.catalyst
          || item.context
          || item.event,
          "No verified catalyst supplied."
        ),

      entry_zone:
        safeText(
          item.entry_zone
          || item.entry
          || item.entry_range,
          "Unavailable"
        ),

      invalidation:
        safeText(
          item.invalidation
          || item.stop
          || item.stop_loss,
          "Unavailable"
        ),

      hold_window:
        safeText(
          item.hold_window
          || item.time_horizon
          || item.duration,
          "Unavailable"
        ),

      risk:
        safeText(
          item.risk
          || item.risk_note
          || item.risk_summary,
          "No verified risk note supplied."
        ),

      score:
        num(
          item.score
          || item.confidence
          || item.quality_score
        ),

      option_contracts:
        contracts.slice(
          0,
          3
        ),

      option_contract_count:
        contracts.length,

      automatic_contract_selection:
        false,

      selection_authority:
        "OWNER"
    };
  };


  const todayEdge = () => {
    const projection =
      canonicalProjection();

    const optionsMap =
      optionContractsBySymbol(
        projection
      );

    const normalized =
      candidateSourceArray(
        projection
      )
        .map(
          function (
            item,
            index
          ) {
            return normalizeCandidate(
              item,
              projection,
              optionsMap,
              index
            );
          }
        );

    return {
      now:
        normalized
          .filter(
            item =>
              item.bucket
              === "now"
          )
          .slice(
            0,
            3
          ),

      watch:
        normalized
          .filter(
            item =>
              item.bucket
              === "watch"
          )
          .slice(
            0,
            3
          ),

      not_yet:
        normalized
          .filter(
            item =>
              item.bucket
              === "not_yet"
          )
          .slice(
            0,
            3
          ),

      source_state: {
        verified_current_market:
          currentMarketVerified(
            projection
          ),

        projection_status:
          safeText(
            projection.projection_status,
            "unavailable"
          ),

        freshness:
          safeText(
            projection.freshness,
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
      }
    };
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
    // A window-supplied "verified: true" flag cannot authenticate capital.
    // Until the protected server provides an independently verified capital
    // receipt/contract, source-projected account figures must stay UNKNOWN.
    // This includes OB_OWNER_CAPITAL_LANE_SNAPSHOT and all self-claimed totals.
    return {
      verified: false,
      lanes: []
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
        snapshot.lanes.map(
          item => [
            safeText(
              item.lane_id,
              ""
            ),
            safeObject(
              item
            )
          ]
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
          (
            live.actual_capital_known === true
            && num(
              live.actual_capital_value
            ) !== null
          );

        const progressKnown =
          (
            live.capital_progress_known === true
            && num(
              live.capital_progress_percent
            ) !== null
          );

        return {
          ...lane,

          verified_snapshot:
            true,

          actual_capital_known:
            capitalKnown,

          actual_capital_value:
            capitalKnown
              ? num(
                  live.actual_capital_value
                )
              : null,

          capital_progress_known:
            progressKnown,

          capital_progress_percent:
            progressKnown
              ? num(
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
            live.needs_attention === true
        };
      }
    );
  };


  const trustSummary = () => {
    const source =
      state.sources.engine_trust
      || {};

    const observed =
      source.status === "available";

    return {
      verified:
        false,

      source_observed:
        observed,

      independent_provenance_authenticated:
        false,

      label:
        observed
          ? "Source trust labels received · independently unverified"
          : "Guarded · trust source unavailable",

      needs_attention:
        true
    };
  };


  const readinessSummary = () => {
    const source =
      state
        .sources
        .manual_live_readiness
      || {};

    const payload =
      safeObject(
        source.payload
      );

    const scorecard =
      safeObject(
        payload.readiness_scorecard
      );

    const blockers =
      source.status === "available"
        ? safeArray(
            payload.remaining_live_blockers
          )
        : [];

    return {
      verified:
        source.verified === true,

      label:
        "Owner rehearsal evidence · Real Manual Live HOLD",

      evidence_class:
        "operator_practice_only_not_tower_or_provider",

      operator_practice_source_observed:
        source.status === "available",

      score_is_practice_only:
        true,

      tower_owner_clearance_verified:
        false,

      authenticated_broker_source_verified:
        false,

      production_manual_live_permission:
        false,

      score:
        source.status === "available"
          ? num(
              scorecard.readiness_score
            )
          : null,

      blockers,

      needs_attention:
        (
          source.status !== "available"
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

    const observed =
      source.status === "available";

    return {
      verified:
        false,

      source_observed:
        observed,

      actual_hosted_beta_access_verified:
        false,

      label:
        observed
          ? "Private beta checklist received · hosted clearance unverified"
          : "Guarded · beta evidence unavailable",

      private_only:
        true,

      public_launch_enabled:
        false
    };
  };


  const ownerAttention = (
    edge,
    trust,
    readiness
  ) => {
    const items = [];

    if (
      edge.now.length
    ) {
      items.push({
        priority:
          "high",

        title:
          `${edge.now.length} verified NOW research setup${edge.now.length === 1 ? "" : "s"}`,

        detail:
          "Open Today’s Edge. Review the evidence before making any owner decision.",

        source:
          "canonical engine projection"
      });
    }

    if (
      readiness.needs_attention
    ) {
      items.push({
        priority:
          "medium",

        title:
          "Owner rehearsal checklist needs review",

        detail:
          readiness.label,

        source:
          "operator practice checkpoint, not live authorization"
      });
    }

    if (
      trust.needs_attention
    ) {
      items.push({
        priority:
          "medium",

        title:
          "Engine trust is guarded",

        detail:
          trust.label,

        source:
          "engine trust"
      });
    }

    return items.slice(
      0,
      3
    );
  };


  const ownerContext = () => {
    const projection =
      canonicalProjection();

    const positions =
      safeArray(
        projection.positions_preview
        || projection.positions
      );

    const queue =
      safeArray(
        projection.manual_live_queue
      );

    const review =
      safeObject(
        projection.review_summary
      );

    return {
      market: {
        label:
          safeText(
            safeObject(
              projection.market_health
            ).label
            || safeObject(
              projection.market_health
            ).state
            || projection.projection_status,
            "Unavailable"
          ),

        verified:
          currentMarketVerified(
            projection
          )
      },

      positions: {
        count:
          positions.length,

        items:
          positions.slice(
            0,
            3
          )
      },

      alerts: {
        count:
          queue.length,

        items:
          queue.slice(
            0,
            3
          )
      },

      review: {
        label:
          safeText(
            review.label
            || review.summary
            || review.status,
            "No verified review summary"
          )
      }
    };
  };


  const historySummary = () => ({
    label:
      "No verified owner-change history yet",

    pattern_label:
      "No verified cross-lane pattern yet",

    may_claim_change_history:
      false,

    may_claim_cross_lane_performance_patterns:
      false
  });


  const buildContract = () => {
    const edge =
      todayEdge();

    const trust =
      trustSummary();

    const readiness =
      readinessSummary();

    const beta =
      betaSummary();

    const lanes =
      capitalLanes();

    const attention =
      ownerAttention(
        edge,
        trust,
        readiness
      );

    return {
      version:
        VERSION,

      status:
        (
          edge
            .source_state
            .verified_current_market
            ? "verified_owner_research"
            : "guarded_owner_research"
        ),

      today_edge:
        edge,

      owner_attention:
        attention,

      owner_context:
        ownerContext(),

      capital_lanes:
        lanes,

      trust,

      readiness,

      beta,

      history:
        historySummary(),

      source_state: {
        engine:
          edge.source_state,

        trust:
          state.sources.engine_trust
          || null,

        readiness:
          state.sources.manual_live_readiness
          || null,

        private_beta:
          state.sources.private_beta
          || null
      },

      interpretation_state: {
        no_action_needed:
          (
            !attention.length
            && !edge.now.length
          )
      },

      policy_notes: {
        capital_truth:
          "Policy text is not a balance.",

        option_truth:
          (
            "A ranked contract is research evidence, "
            + "not an automatically selected contract."
          )
      },

      boundaries:
        BOUNDARIES
    };
  };


  const hydrate = async () => {
    const results =
      await Promise.all([
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

    results.forEach(
      function (
        result
      ) {
        state.sources[
          result.name
        ] =
          result;
      }
    );

    state.contract =
      buildContract();

    return state.contract;
  };


  window.OB_OWNER_DASHBOARD_CONTRACT_V21 =
    Object.freeze({
      version:
        VERSION,

      endpoints:
        ENDPOINTS,

      boundaries:
        BOUNDARIES,

      buildContract,

      hydrate
    });

})();
