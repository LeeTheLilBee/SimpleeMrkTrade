
// OBSERVATORY_V25_SAFE_ENGINE_FEED_ADAPTER_JS
// OBDATA003_CANONICAL_WEB_PROJECTION
//
// Existing engine endpoint → read-only canonical web projection.
//
// IMPORTANT:
// This is NOT another engine.
// This layer does not calculate market scores, positions, candidates,
// signals, P/L, confidence, or market regime.
//
// It projects only fields the existing engine snapshot actually supplies.

(function () {
  "use strict";

  const ADAPTER_VERSION =
    "OB_V25_CANONICAL_WEB_PROJECTION_OBDATA003";

  const DEFAULT_ENDPOINT =
    "/ob/engine-feed-snapshot.json";


  // OBFIX006–010
  //
  // Protected rooms may provide a SAME-ORIGIN relative endpoint that
  // travels through an already-approved room corridor.
  //
  // The default remains unchanged for compatibility.
  // Absolute / protocol-relative URLs are rejected.
  const REQUESTED_ENDPOINT =
    (
      typeof window.OB_ENGINE_FEED_ENDPOINT === "string"
    )
      ? window.OB_ENGINE_FEED_ENDPOINT.trim()
      : "";


  const ENDPOINT =
    (
      REQUESTED_ENDPOINT.startsWith("/")
      &&
      !REQUESTED_ENDPOINT.startsWith("//")
    )
      ? REQUESTED_ENDPOINT
      : DEFAULT_ENDPOINT;

  const POLL_MS =
    60 * 1000;

  const DEFAULT_CURRENT_MAX_AGE_MS =
    15 * 60 * 1000;

  const NON_CURRENT_SOURCE_PATTERN =
    /(preview|fallback|demo|sample|mock|fixture|synthetic|seed|bootstrap)/i;

  const REHEARSAL_SOURCE_PATTERN =
    /(rehearsal|dry[_ -]?run|practice)/i;


  let adapterState = {
    status:
      "booting",

    source:
      null,

    httpStatus:
      null,

    payload:
      null,

    error:
      null,

    fallbackActive:
      false,

    loadedAt:
      null,
  };


  let currentProjection =
    null;


  let pollHandle =
    null;


  function safeObject(value) {
    return (
      value
      &&
      typeof value === "object"
      &&
      !Array.isArray(value)
    )
      ? value
      : {};
  }


  function safeArray(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function safeText(
    value,
    fallback
  ) {
    if (
      value === undefined
      ||
      value === null
      ||
      value === ""
    ) {
      return fallback;
    }

    return String(value);
  }


  function clone(value) {
    try {
      return JSON.parse(
        JSON.stringify(value)
      );
    } catch (error) {
      return value;
    }
  }


  function firstString(values) {
    for (const value of values) {
      if (
        typeof value === "string"
        &&
        value.trim()
      ) {
        return value.trim();
      }
    }

    return null;
  }


  function firstArray(values) {
    for (const value of values) {
      if (Array.isArray(value)) {
        return value;
      }
    }

    return [];
  }


  function firstObject(values) {
    for (const value of values) {
      if (
        value
        &&
        typeof value === "object"
        &&
        !Array.isArray(value)
      ) {
        return value;
      }
    }

    return {};
  }


  function parseTimestamp(value) {
    if (
      value === null
      ||
      value === undefined
      ||
      value === ""
    ) {
      return null;
    }


    const date =
      new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return null;
    }


    return date.toISOString();
  }


  const TIMESTAMP_KEYS = [
    "as_of",
    "timestamp",
    "generated_at",
    "updated_at",
    "saved_at",
    "snapshot_at",
    "run_at",
    "market_universe_run_at",
    "loaded_at",
    "created_at",
  ];


  function findTimestamp(
    value,
    depth
  ) {
    const level =
      Number(
        depth
        ||
        0
      );


    if (
      level
      >
      5
    ) {
      return null;
    }


    if (
      !value
      ||
      typeof value !== "object"
    ) {
      return null;
    }


    if (
      !Array.isArray(value)
    ) {
      for (
        const key of
        TIMESTAMP_KEYS
      ) {
        if (
          Object.prototype.hasOwnProperty.call(
            value,
            key
          )
        ) {
          const parsed =
            parseTimestamp(
              value[
                key
              ]
            );


          if (parsed) {
            return parsed;
          }
        }
      }


      for (
        const nested of
        Object.values(value)
      ) {
        const parsed =
          findTimestamp(
            nested,
            level + 1
          );


        if (parsed) {
          return parsed;
        }
      }


      return null;
    }


    for (
      const item of
      value.slice(
        0,
        5
      )
    ) {
      const parsed =
        findTimestamp(
          item,
          level + 1
        );


      if (parsed) {
        return parsed;
      }
    }


    return null;
  }


  function sourceName(payload) {
    const rawMeta =
      safeObject(
        payload.raw_meta
      );

    const provenance =
      safeObject(
        payload.provenance
      );

    const marketHealth =
      safeObject(
        payload.market_health
      );


    return firstString([
      payload.provider,
      payload.source,
      payload.data_source,
      payload.source_name,

      provenance.provider,
      provenance.source,

      rawMeta.provider,
      rawMeta.source,
      rawMeta.data_source,

      marketHealth.provider,
      marketHealth.source,
    ]);
  }


  function sourceClass(source) {
    if (!source) {
      return "unknown";
    }


    if (
      REHEARSAL_SOURCE_PATTERN.test(
        source
      )
    ) {
      return "rehearsal";
    }


    if (
      NON_CURRENT_SOURCE_PATTERN.test(
        source
      )
    ) {
      return "quarantined";
    }


    return "candidate_current_source";
  }


  function emptyProjection(
    reason,
    options
  ) {
    const extras =
      safeObject(
        options
      );


    return {
      version:
        ADAPTER_VERSION,

      projection_version:
        "OBDATA003",

      endpoint:
        ENDPOINT,

      projection_status:
        extras.projection_status
        ||
        "unavailable",

      freshness:
        extras.freshness
        ||
        "unavailable",

      source:
        extras.source
        ||
        null,

      source_class:
        extras.source_class
        ||
        "unknown",

      source_identified:
        false,

      as_of:
        null,

      timestamp_identified:
        false,

      age_ms:
        null,

      current_eligible:
        false,

      display_eligible:
        false,

      route_data_received:
        false,

      reason:
        reason
        ||
        "Canonical engine projection is unavailable.",
      options:
        [],

      research_contracts:
        [],

      ranked_contracts:
        [],

      options_by_symbol:
        {},

      option_chains:
        {},

      options_chains:
        {},

      options_projection: {
        schema_version:
          "OB_OPTIONS_RESEARCH_V1",

        authority:
          "UNAVAILABLE",

        selection_authority:
          "USER",

        research_contracts:
          [],

        ranked_contracts:
          [],

        options_by_symbol:
          {},

        option_chains:
          {},

        diagnostics: {
          contract_count:
            0,

          symbols_with_contracts:
            0,

          no_fake_fallback:
            true,

          ob_selected_contract:
            false,

          brokerage_execution:
            false,

          automatic_execution:
            false,

          automatic_contract_selection:
            false,
        },
      },


      market_health:
        {},

      sectors:
        [],

      symbols:
        [],

      signals:
        [],

      watchlist:
        [],

      positions_preview:
        [],

      candidates_preview:
        [],

      manual_live_queue:
        [],

      review_summary:
        {},

      account_snapshot:
        null,

      data_files:
        {},

      raw_meta:
        {},

      warnings:
        [],

      tower_boundaries: {
        no_broker_api:
          true,

        no_order_submission:
          true,

        no_capital_movement:
          true,

        no_auto_execution:
          true,

        live_auto_locked:
          true,

        gp066_advanced:
          false,
      },
    };
  }


  function projectPayload(payload) {
    const safe =
      safeObject(
        payload
      );

    // ----------------------------------------------------------------------------------------------
    // OBDATA007_OPTIONS_RESEARCH_PROJECTION
    //
    // Reuses existing engine option intelligence.
    //
    // Ranking evidence may be projected.
    // Engine selection does NOT become user selection.
    // ----------------------------------------------------------------------------------------------

    const optionsResearchContract =
      window.OBOptionsResearchContract;

    const optionsProjection =
      (
        optionsResearchContract
        &&
        typeof optionsResearchContract.buildProjection
          === "function"
      )
        ? optionsResearchContract.buildProjection(
            safe
          )
        : {
            schema_version:
              "OB_OPTIONS_RESEARCH_V1",

            authority:
              "UNAVAILABLE",

            selection_authority:
              "USER",

            research_contracts:
              [],

            ranked_contracts:
              [],

            options_by_symbol:
              {},

            option_chains:
              {},

            diagnostics: {
              contract_count:
                0,

              symbols_with_contracts:
                0,

              no_fake_fallback:
                true,

              direct_market_fetch:
                false,

              browser_yfinance:
                false,

              ob_selected_contract:
                false,

              brokerage_execution:
                false,

              automatic_execution:
                false,

              automatic_contract_selection:
                false,

              reason:
                "options_research_contract_not_loaded",
            },
          };




    const source =
      sourceName(
        safe
      );


    const sourceType =
      sourceClass(
        source
      );


    const asOf =
      findTimestamp(
        safe,
        0
      );


    const sourceIdentified =
      Boolean(
        source
      );


    const timestampIdentified =
      Boolean(
        asOf
      );


    let freshness =
      "provenance_required";


    let projectionStatus =
      "provenance_required";


    let ageMs =
      null;


    if (
      sourceType === "quarantined"
    ) {
      freshness =
        "quarantined";

      projectionStatus =
        "quarantined";
    }


    else if (
      sourceType === "rehearsal"
    ) {
      freshness =
        "rehearsal";

      projectionStatus =
        "rehearsal";
    }


    else if (
      !sourceIdentified
      ||
      !timestampIdentified
    ) {
      freshness =
        "provenance_required";

      projectionStatus =
        "provenance_required";
    }


    else {
      ageMs =
        Math.max(
          0,
          Date.now()
          -
          new Date(
            asOf
          ).getTime()
        );


      const rawMeta =
        safeObject(
          safe.raw_meta
        );


      const suppliedMaxAgeSeconds =
        Number(
          safe.max_age_seconds
          ||
          rawMeta.max_age_seconds
          ||
          0
        );


      const maxAgeMs =
        (
          Number.isFinite(
            suppliedMaxAgeSeconds
          )
          &&
          suppliedMaxAgeSeconds
          >
          0
        )
          ? suppliedMaxAgeSeconds * 1000
          : DEFAULT_CURRENT_MAX_AGE_MS;


      if (
        ageMs
        <=
        maxAgeMs
      ) {
        freshness =
          "fresh";

        projectionStatus =
          "fresh";
      }

      else {
        freshness =
          "stale";

        projectionStatus =
          "stale";
      }
    }


    const displayEligible =
      (
        projectionStatus === "fresh"
        ||
        projectionStatus === "stale"
      );


    const currentEligible =
      (
        projectionStatus === "fresh"
      );


    const marketMap =
      firstObject([
        safe.market_map,
        safe.marketMap,
      ]);


    const serverData =
      firstObject([
        safe.server_data,
        safe.data,
      ]);


    const sectors =
      firstArray([
        safe.sectors,
        marketMap.sectors,
        serverData.sectors,
      ]);


    const symbols =
      firstArray([
        safe.symbols,
        marketMap.symbols,
        serverData.symbols,
      ]);


    const signals =
      firstArray([
        safe.signals,
        safe.paper_signals,
        serverData.signals,
      ]);


    const watchlist =
      firstArray([
        safe.watchlist,
        serverData.watchlist,
      ]);


    const positions =
      firstArray([
        safe.positions_preview,
        safe.open_positions,
        safe.positions,
        serverData.positions_preview,
        serverData.open_positions,
      ]);


    const candidates =
      firstArray([
        safe.candidates_preview,
        safe.candidates,
        safe.watched_candidates,
        serverData.candidates_preview,
        serverData.candidates,
      ]);


    const manualQueue =
      firstArray([
        safe.manual_live_queue,
        serverData.manual_live_queue,
      ]);


    const reviewSummary =
      firstObject([
        safe.review_summary,
        serverData.review_summary,
      ]);


    const warnings =
      safeArray(
        safe.warnings
      ).map(
        item =>
          String(
            item
          )
      );


    if (
      projectionStatus === "provenance_required"
    ) {
      warnings.push(
        "Engine data was received, but source and/or as-of provenance is incomplete. "
        +
        "OB will not call it current market truth."
      );
    }


    if (
      projectionStatus === "quarantined"
    ) {
      warnings.push(
        "Preview/demo/seed/fallback provenance is quarantined from current market truth."
      );
    }


    if (
      projectionStatus === "rehearsal"
    ) {
      warnings.push(
        "Rehearsal/practice provenance is not eligible for current market truth."
      );
    }


    return {
      version:
        safe.version
        ||
        ADAPTER_VERSION,

      projection_version:
        "OBDATA003",

      endpoint:
        ENDPOINT,

      projection_status:
        projectionStatus,

      freshness,

      source,

      source_class:
        sourceType,

      source_identified:
        sourceIdentified,

      as_of:
        asOf,

      timestamp_identified:
        timestampIdentified,

      age_ms:
        ageMs,

      current_eligible:
        currentEligible,

      display_eligible:
        displayEligible,

      route_data_received:
        true,

      reason:
        (
          projectionStatus === "fresh"
            ? "Source-backed engine snapshot is within its freshness window."
            :
          projectionStatus === "stale"
            ? "Source-backed engine snapshot exists but is older than its freshness window."
            :
          projectionStatus === "quarantined"
            ? "Snapshot provenance identifies preview/demo/seed/fallback material."
            :
          projectionStatus === "rehearsal"
            ? "Snapshot provenance identifies rehearsal/practice material."
            :
            "Source and/or as-of provenance is incomplete."
        ),


      // --------------------------------------------------------------------------------------------
      // OBDATA007 — SOURCE-BACKED OPTIONS RESEARCH
      //
      // The SAME displayEligible gate used for market truth also controls option intelligence.
      //
      // No provenance bypass.
      // No rehearsal leakage.
      // No demo/fallback leakage.
      // --------------------------------------------------------------------------------------------

      options:
        displayEligible
          ? clone(
              optionsProjection.research_contracts
              ||
              []
            )
          : [],

      research_contracts:
        displayEligible
          ? clone(
              optionsProjection.research_contracts
              ||
              []
            )
          : [],

      ranked_contracts:
        displayEligible
          ? clone(
              optionsProjection.ranked_contracts
              ||
              []
            )
          : [],

      options_by_symbol:
        displayEligible
          ? clone(
              optionsProjection.options_by_symbol
              ||
              {}
            )
          : {},

      option_chains:
        displayEligible
          ? clone(
              optionsProjection.option_chains
              ||
              {}
            )
          : {},

      options_chains:
        displayEligible
          ? clone(
              optionsProjection.option_chains
              ||
              {}
            )
          : {},

      options_projection:
        displayEligible
          ? clone(
              optionsProjection
            )
          : {
              schema_version:
                "OB_OPTIONS_RESEARCH_V1",

              authority:
                optionsProjection.authority
                ||
                "UNAVAILABLE",

              selection_authority:
                "USER",

              research_contracts:
                [],

              ranked_contracts:
                [],

              options_by_symbol:
                {},

              option_chains:
                {},

              diagnostics: {
                contract_count:
                  0,

                symbols_with_contracts:
                  0,

                no_fake_fallback:
                  true,

                ob_selected_contract:
                  false,

                brokerage_execution:
                  false,

                automatic_execution:
                  false,

                automatic_contract_selection:
                  false,

                projection_blocked_by_market_truth_gate:
                  true,
              },
            },

// NO generated numbers below.
      market_health:
        displayEligible
          ? clone(
              firstObject([
                safe.market_health,
                serverData.market_health,
              ])
            )
          : {},

      sectors:
        displayEligible
          ? clone(
              sectors
            )
          : [],

      symbols:
        displayEligible
          ? clone(
              symbols
            )
          : [],

      signals:
        displayEligible
          ? clone(
              signals
            )
          : [],

      watchlist:
        displayEligible
          ? clone(
              watchlist
            )
          : [],

      positions_preview:
        displayEligible
          ? clone(
              positions
            )
          : [],

      candidates_preview:
        displayEligible
          ? clone(
              candidates
            )
          : [],

      manual_live_queue:
        displayEligible
          ? clone(
              manualQueue
            )
          : [],

      review_summary:
        displayEligible
          ? clone(
              reviewSummary
            )
          : {},

      account_snapshot:
        displayEligible
          ? clone(
              safe.account_snapshot
              ||
              null
            )
          : null,


      // OBENG001-005_ACCOUNT_AUTHORITY_PROJECTION
      //
      // Authority metadata is supplied by the protected backend.
      // This client does not calculate or reconcile account truth.
      authority_registry:
        clone(
          safeObject(
            safe.authority_registry
            ||
            serverData.authority_registry
          )
        ),

      account_authority:
        clone(
          safeObject(
            safe.account_authority
            ||
            serverData.account_authority
          )
        ),

      position_authority:
        clone(
          safeObject(
            safe.position_authority
            ||
            serverData.position_authority
          )
        ),

      reporting_authority:
        clone(
          safeObject(
            safe.reporting_authority
            ||
            serverData.reporting_authority
          )
        ),

      authority_source_registry:
        clone(
          safeObject(
            safe.authority_source_registry
            ||
            serverData.authority_source_registry
          )
        ),

      authority_boundaries:
        clone(
          safeObject(
            safe.authority_boundaries
            ||
            serverData.authority_boundaries
          )
        ),

      data_files:
        clone(
          safeObject(
            safe.data_files
          )
        ),

      raw_meta:
        clone(
          safeObject(
            safe.raw_meta
          )
        ),

      warnings,

      tower_boundaries: {
        ...clone(
          safeObject(
            safe.tower_boundaries
          )
        ),

        no_broker_api:
          true,

        no_order_submission:
          true,

        no_capital_movement:
          true,

        no_auto_execution:
          true,

        live_auto_locked:
          true,

        gp066_advanced:
          false,
      },
    };
  }


  // -----------------------------------------------------------------------------------------------
  // Compatibility name retained.
  //
  // It now returns EMPTY unavailable state.
  // It never constructs preview market data.
  // -----------------------------------------------------------------------------------------------

  function fallbackSnapshot() {
    return emptyProjection(
      "Preview fallback is disabled. Missing engine truth stays missing.",
      {
        projection_status:
          "unavailable",

        freshness:
          "unavailable",
      }
    );
  }


  function normalizePayload(payload) {
    return projectPayload(
      payload
    );
  }


  function exposeServerData(payload) {
    const projected =
      (
        payload
        &&
        payload.projection_version === "OBDATA003"
      )
        ? payload
        : projectPayload(
            payload
          );


    currentProjection =
      projected;


    window.OB_ENGINE_FEED_SNAPSHOT_V25 =
      projected;


    window.OB_SERVER_DATA = {
      engine_feed_v25:
        projected,

      canonical_web_projection:
        projected,

      source:
        projected.source,

      as_of:
        projected.as_of,

      freshness:
        projected.freshness,

      projection_status:
        projected.projection_status,

      current_eligible:
        projected.current_eligible,

      display_eligible:
        projected.display_eligible,

      market_health:
        clone(
          projected.market_health
        ),

      sectors:
        clone(
          projected.sectors
        ),

      symbols:
        clone(
          projected.symbols
        ),

      signals:
        clone(
          projected.signals
        ),

      watchlist:
        clone(
          projected.watchlist
        ),

      positions_preview:
        clone(
          projected.positions_preview
        ),

      candidates_preview:
        clone(
          projected.candidates_preview
        ),

      manual_live_queue:
        clone(
          projected.manual_live_queue
        ),

      review_summary:
        clone(
          projected.review_summary
        ),

      account_snapshot:
        clone(
          projected.account_snapshot
        ),

      authority_registry:
        clone(
          projected.authority_registry
          ||
          {}
        ),

      account_authority:
        clone(
          projected.account_authority
          ||
          {}
        ),

      position_authority:
        clone(
          projected.position_authority
          ||
          {}
        ),

      reporting_authority:
        clone(
          projected.reporting_authority
          ||
          {}
        ),

      authority_source_registry:
        clone(
          projected.authority_source_registry
          ||
          {}
        ),

      authority_boundaries:
        clone(
          projected.authority_boundaries
          ||
          {}
        ),
    };


    window.dispatchEvent(
      new CustomEvent(
        "obEngineFeedAdapterUpdated",
        {
          detail:
            clone(
              projected
            ),
        }
      )
    );


    return projected;
  }


  function unavailableFromHttp(
    status,
    reason
  ) {
    const projected =
      emptyProjection(
        reason,
        {
          projection_status:
            (
              status === 401
              ||
              status === 403
            )
              ? "guarded"
              : "unavailable",

          freshness:
            (
              status === 401
              ||
              status === 403
            )
              ? "guarded"
              : "unavailable",
        }
      );


    return exposeServerData(
      projected
    );
  }


  async function fetchEngineSnapshot() {
    adapterState.status =
      "loading";

    adapterState.loadedAt =
      new Date().toISOString();

    adapterState.fallbackActive =
      false;


    try {
      const response =
        await fetch(
          ENDPOINT,
          {
            credentials:
              "same-origin",

            cache:
              "no-store",

            headers: {
              Accept:
                "application/json",
            },
          }
        );


      adapterState.httpStatus =
        response.status;


      if (response.ok) {
        const payload =
          await response.json();


        const projected =
          exposeServerData(
            projectPayload(
              payload
            )
          );


        adapterState.status =
          projected.projection_status;

        adapterState.source =
          projected.source;

        adapterState.payload =
          projected;

        adapterState.error =
          (
            projected.current_eligible
            ? null
            : projected.reason
          );

        adapterState.fallbackActive =
          false;
      }


      else {
        const reason =
          (
            response.status === 401
            ||
            response.status === 403
          )
            ? (
                "Engine snapshot is protected for this session. "
                +
                "No preview data was substituted."
              )
            : (
                "Engine snapshot returned HTTP "
                +
                response.status
                +
                ". No preview data was substituted."
              );


        const projected =
          unavailableFromHttp(
            response.status,
            reason
          );


        adapterState.status =
          projected.projection_status;

        adapterState.source =
          null;

        adapterState.payload =
          projected;

        adapterState.error =
          reason;

        adapterState.fallbackActive =
          false;
      }
    }


    catch (error) {
      const message =
        (
          error
          &&
          error.message
        )
          ? error.message
          : "Unknown fetch error";


      const projected =
        exposeServerData(
          emptyProjection(
            "Engine snapshot could not be reached. "
            +
            "No preview data was substituted.",
            {
              projection_status:
                "unavailable",

              freshness:
                "unavailable",
            }
          )
        );


      adapterState.status =
        "unavailable";

      adapterState.source =
        null;

      adapterState.payload =
        projected;

      adapterState.error =
        message;

      adapterState.fallbackActive =
        false;
    }


    updateEngineBar();


    return {
      ...adapterState,
    };
  }


  function getProjection() {
    return clone(
      currentProjection
      ||
      fallbackSnapshot()
    );
  }


  function count(value) {
    return Array.isArray(value)
      ? value.length
      : 0;
  }


  function closeDrawer() {
    const existing =
      document.getElementById(
        "obEngineFeedBackdrop"
      );


    if (existing) {
      existing.remove();
    }
  }


  function boundaryValue(value) {
    return value
      ? "Yes"
      : "No";
  }


  function row(
    title,
    detail,
    index
  ) {
    return `
      <div class="ob-engine-feed-row">
        <div class="ob-engine-feed-dot">
          ${index + 1}
        </div>

        <div class="ob-engine-feed-copy">
          <strong>${title}</strong>
          <span>${detail}</span>
        </div>
      </div>
    `;
  }


  function openEngineDrawer() {
    closeDrawer();


    const payload =
      getProjection();


    const boundaries =
      payload.tower_boundaries
      ||
      {};


    const backdrop =
      document.createElement(
        "div"
      );


    backdrop.id =
      "obEngineFeedBackdrop";

    backdrop.className =
      "ob-engine-feed-backdrop open";


    const drawer =
      document.createElement(
        "div"
      );


    drawer.className =
      "ob-engine-feed-drawer";


    drawer.innerHTML = `
      <div class="ob-engine-feed-head">
        <div>
          <strong>
            Canonical Engine → Web Projection
          </strong>

          <span>
            Read-only projection of the existing OB engine snapshot.
            Missing provenance is never replaced with preview market state.
          </span>
        </div>

        <button
          class="ob-engine-feed-close"
          id="obEngineFeedClose"
        >
          ×
        </button>
      </div>

      <div class="ob-engine-feed-grid">
        <div class="ob-engine-feed-card">
          <span>Projection</span>
          <strong>${safeText(payload.projection_status, "unavailable")}</strong>
        </div>

        <div class="ob-engine-feed-card">
          <span>Freshness</span>
          <strong>${safeText(payload.freshness, "unavailable")}</strong>
        </div>

        <div class="ob-engine-feed-card">
          <span>Source</span>
          <strong>${safeText(payload.source, "not identified")}</strong>
        </div>

        <div class="ob-engine-feed-card">
          <span>As of</span>
          <strong>${safeText(payload.as_of, "not identified")}</strong>
        </div>

        <div class="ob-engine-feed-card">
          <span>Positions</span>
          <strong>${count(payload.positions_preview)}</strong>
        </div>

        <div class="ob-engine-feed-card">
          <span>Candidates</span>
          <strong>${count(payload.candidates_preview)}</strong>
        </div>
      </div>

      <div class="ob-engine-feed-note">
        <strong style="color: var(--ob-gold);">
          Soulaana:
        </strong>
        <br>

        Canonical means the engine shaped the information consistently.
        It does not automatically mean the input was live.
        I check provenance and freshness before I call anything current.
      </div>

      <div class="ob-engine-feed-warning">
        <strong>Read-only boundary:</strong>
        <br>

        Broker API:
        ${boundaryValue(!boundaries.no_broker_api)}
        ·

        Order submission:
        ${boundaryValue(!boundaries.no_order_submission)}
        ·

        Capital movement:
        ${boundaryValue(!boundaries.no_capital_movement)}
        ·

        Live Auto Locked:
        ${boundaryValue(boundaries.live_auto_locked)}
      </div>

      <div class="ob-engine-feed-list">
        ${row(
          "Authority",
          safeText(
            payload.reason,
            "No authority explanation supplied."
          ),
          0
        )}

        ${row(
          "Current eligible",
          payload.current_eligible
            ? "Yes"
            : "No",
          1
        )}

        ${row(
          "Static fallback",
          "DISABLED",
          2
        )}

        ${row(
          "Warnings",
          (
            payload.warnings
            ||
            []
          ).join(" · ")
          ||
          "No warnings.",
          3
        )}
      </div>

      <div class="ob-engine-feed-actions-row">
        <button
          class="ob-engine-feed-button"
          id="obEngineFeedRefresh"
        >
          Refresh projection
        </button>

        <button
          class="ob-engine-feed-button gold"
          id="obEngineFeedContracts"
        >
          Open room contracts
        </button>

        <button
          class="ob-engine-feed-button red"
          id="obEngineFeedCloseFooter"
        >
          Close
        </button>
      </div>
    `;


    backdrop.appendChild(
      drawer
    );


    document.body.appendChild(
      backdrop
    );


    document.getElementById(
      "obEngineFeedClose"
    ).addEventListener(
      "click",
      closeDrawer
    );


    document.getElementById(
      "obEngineFeedCloseFooter"
    ).addEventListener(
      "click",
      closeDrawer
    );


    const refresh =
      document.getElementById(
        "obEngineFeedRefresh"
      );


    if (refresh) {
      refresh.addEventListener(
        "click",
        async function () {
          await fetchEngineSnapshot();

          openEngineDrawer();
        }
      );
    }


    const contracts =
      document.getElementById(
        "obEngineFeedContracts"
      );


    if (contracts) {
      contracts.addEventListener(
        "click",
        function () {
          if (
            window.OB_DATA_CONTRACTS_V22
            &&
            window.OB_DATA_CONTRACTS_V22.openDataDrawer
          ) {
            window.OB_DATA_CONTRACTS_V22.openDataDrawer();
          }
        }
      );
    }


    backdrop.addEventListener(
      "click",
      function (event) {
        if (
          event.target === backdrop
        ) {
          closeDrawer();
        }
      }
    );
  }


  function updateEngineBar() {
    const bar =
      document.getElementById(
        "obEngineFeedBar"
      );


    if (!bar) {
      return;
    }


    const payload =
      getProjection();


    const chip =
      bar.querySelector(
        "[data-engine-feed-source-chip]"
      );


    let chipClass =
      "red";


    if (
      payload.projection_status === "fresh"
    ) {
      chipClass =
        "green";
    }


    else if (
      payload.projection_status === "stale"
      ||
      payload.projection_status === "provenance_required"
    ) {
      chipClass =
        "gold";
    }


    bar.querySelector(
      ".ob-engine-feed-title"
    ).textContent =
      "Canonical Web Projection · "
      +
      safeText(
        payload.projection_status,
        "unavailable"
      );


    bar.querySelector(
      ".ob-engine-feed-subtitle"
    ).textContent =
      (
        safeText(
          payload.source,
          "source not identified"
        )
        +
        " · "
        +
        safeText(
          payload.as_of,
          "as-of not identified"
        )
        +
        " · static fallback disabled"
      );


    if (chip) {
      chip.className =
        "ob-engine-feed-chip "
        +
        chipClass;

      chip.textContent =
        safeText(
          payload.freshness,
          "unavailable"
        );
    }
  }


  function buildEngineBar() {
    if (
      document.getElementById(
        "obEngineFeedBar"
      )
    ) {
      return;
    }


    const layer =
      document.querySelector(
        ".ob-layer"
      );


    if (!layer) {
      return;
    }


    const bar =
      document.createElement(
        "div"
      );


    bar.className =
      "ob-engine-feed-bar";

    bar.id =
      "obEngineFeedBar";


    bar.innerHTML = `
      <div class="ob-engine-feed-main">
        <div class="ob-engine-feed-title">
          Canonical Web Projection · booting
        </div>

        <div class="ob-engine-feed-subtitle">
          Checking source + as-of provenance.
        </div>
      </div>

      <div class="ob-engine-feed-actions">
        <span
          class="ob-engine-feed-chip gold"
          data-engine-feed-source-chip
        >
          checking
        </span>

        <span class="ob-engine-feed-chip red">
          No broker API
        </span>

        <span class="ob-engine-feed-chip red">
          Live Auto Locked
        </span>

        <button
          class="ob-engine-feed-chip clickable"
          id="obEngineFeedOpen"
        >
          Data Truth
        </button>
      </div>
    `;


    const dataBar =
      document.getElementById(
        "obDataStatusBar"
      );

    const missionBar =
      document.getElementById(
        "obMissionBar"
      );

    const routeBar =
      document.getElementById(
        "obRouteBar"
      );


    if (
      dataBar
      &&
      dataBar.parentNode
    ) {
      dataBar.insertAdjacentElement(
        "afterend",
        bar
      );
    }


    else if (
      missionBar
      &&
      missionBar.parentNode
    ) {
      missionBar.insertAdjacentElement(
        "afterend",
        bar
      );
    }


    else if (
      routeBar
      &&
      routeBar.parentNode
    ) {
      routeBar.insertAdjacentElement(
        "afterend",
        bar
      );
    }


    else {
      layer.prepend(
        bar
      );
    }


    document.getElementById(
      "obEngineFeedOpen"
    ).addEventListener(
      "click",
      openEngineDrawer
    );
  }


  function startPolling() {
    if (pollHandle) {
      return;
    }


    pollHandle =
      window.setInterval(
        function () {
          if (
            document.visibilityState
            ===
            "visible"
          ) {
            fetchEngineSnapshot();
          }
        },
        POLL_MS
      );
  }


  function boot() {
    exposeServerData(
      fallbackSnapshot()
    );


    buildEngineBar();

    updateEngineBar();

    fetchEngineSnapshot();

    startPolling();


    document.addEventListener(
      "visibilitychange",
      function () {
        if (
          document.visibilityState
          ===
          "visible"
        ) {
          fetchEngineSnapshot();
        }
      }
    );


    window.addEventListener(
      "focus",
      function () {
        fetchEngineSnapshot();
      }
    );
  }


  if (
    document.readyState
    ===
    "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot,
      {
        once:
          true,
      }
    );
  }

  else {
    boot();
  }


  const API = {
    version:
      ADAPTER_VERSION,

    endpoint:
      ENDPOINT,

    poll_ms:
      POLL_MS,

    getState:
      function () {
        return {
          ...adapterState,
        };
      },

    getProjection,

    emptyProjection,

    fallbackSnapshot,

    normalizePayload,

    projectPayload,

    exposeServerData,

    fetchEngineSnapshot,

    openEngineDrawer,

    preview_fallback_enabled:
      false,

    synthetic_market_state_enabled:
      false,

    safety: {
      read_only:
        true,

      broker_api_enabled:
        false,

      order_submission_enabled:
        false,

      capital_movement_enabled:
        false,

      auto_execution_enabled:
        false,

      live_auto_locked:
        true,

      gp066_advanced:
        false,
    },
  };


  window.OB_ENGINE_FEED_ADAPTER_V25 =
    API;


  window.OB_CANONICAL_WEB_PROJECTION_OBDATA003_API =
    API;
})();
