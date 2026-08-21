(function () {
  "use strict";

  const VERSION =
    "OBUX052_OWNER_CONSOLE_SYSTEM_TRUTH_PROJECTION";


  // ================================================================================================
  // BASIC HELPERS
  // ================================================================================================

  function obj(value) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    )
      ? value
      : {};
  }


  function arr(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function first(...values) {
    for (const value of values) {
      if (
        value !== undefined
        && value !== null
        && value !== ""
      ) {
        return value;
      }
    }

    return null;
  }


  function num(value) {
    if (
      value === undefined
      || value === null
      || value === ""
    ) {
      return null;
    }

    const parsed = Number(value);

    return Number.isFinite(parsed)
      ? parsed
      : null;
  }


  function txt(value, fallback = null) {
    const found = first(value);

    return found === null
      ? fallback
      : String(found);
  }


  function lower(value) {
    return String(value || "")
      .trim()
      .toLowerCase();
  }


  function bool(value) {
    return value === true;
  }


  function serverData() {
    return obj(
      window.OB_SERVER_DATA
    );
  }


  // ================================================================================================
  // STATUS LANGUAGE
  //
  // Owner Console never upgrades unknown/fallback into healthy.
  // ================================================================================================

  const STATUS = Object.freeze({
    HEALTHY: "HEALTHY",
    GUARDED: "GUARDED",
    DEGRADED: "DEGRADED",
    LOCKED: "LOCKED",
    UNKNOWN: "UNKNOWN",
    UNAVAILABLE: "UNAVAILABLE",
  });


  function statusRank(value) {
    const rank = {
      HEALTHY: 0,
      GUARDED: 1,
      UNKNOWN: 2,
      DEGRADED: 3,
      LOCKED: 4,
      UNAVAILABLE: 5,
    };

    return rank[value] ?? 2;
  }


  function worstStatus(values) {
    const filtered =
      values.filter(Boolean);

    if (!filtered.length) {
      return STATUS.UNKNOWN;
    }

    return filtered
      .slice()
      .sort(
        (a, b) =>
          statusRank(b)
          -
          statusRank(a)
      )[0];
  }


  function classifyDisplayTruth(value) {
    const raw =
      lower(value);

    if (
      raw.includes("locked")
      || raw.includes("blocked")
      || raw.includes("disabled")
    ) {
      return STATUS.LOCKED;
    }

    if (
      raw.includes("missing")
      || raw.includes("error")
      || raw.includes("failed")
      || raw.includes("unsafe")
    ) {
      return STATUS.DEGRADED;
    }

    if (
      raw.includes("fallback")
      || raw.includes("guard")
      || raw.includes("stale")
      || raw.includes("caution")
      || raw.includes("review")
    ) {
      return STATUS.GUARDED;
    }

    if (
      raw.includes("fresh")
      || raw.includes("safe")
      || raw.includes("healthy")
      || raw.includes("ready")
    ) {
      return STATUS.HEALTHY;
    }

    return STATUS.UNKNOWN;
  }


  // ================================================================================================
  // DIAGNOSTICS
  // ================================================================================================

  function diagnosticsState() {
    if (
      window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API
      &&
      typeof
      window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API.getState
      === "function"
    ) {
      return obj(
        window
          .OB_ENGINE_FEED_DIAGNOSTICS_V33_API
          .getState()
      );
    }

    return {};
  }


  function diagnosticsPayload() {
    const state =
      diagnosticsState();

    const payload =
      first(
        state.payload,
        window.OB_ENGINE_FEED_DIAGNOSTICS_V33,
        serverData().engine_feed_diagnostics_v33
      );

    return obj(payload);
  }


  function normalizeDiagnostics() {
    const state =
      diagnosticsState();

    const payload =
      diagnosticsPayload();

    const summary =
      obj(payload.summary);

    const files =
      arr(payload.files);

    const fallbackActive =
      state.fallbackActive === true
      ||
      lower(payload.source).includes(
        "fallback"
      )
      ||
      lower(
        payload.display_label
      ).includes(
        "fallback"
      );

    let status =
      classifyDisplayTruth(
        first(
          payload.display_label,
          payload.diagnostics_status,
          state.status
        )
      );

    if (fallbackActive) {
      status = STATUS.GUARDED;
    }

    if (
      num(summary.missing) > 0
    ) {
      status = worstStatus([
        status,
        STATUS.DEGRADED,
      ]);
    }

    return {
      status,

      source:
        txt(
          first(
            payload.source,
            state.source
          ),
          "unknown"
        ),

      display_label:
        txt(
          payload.display_label,
          "Unknown"
        ),

      freshness_score:
        num(
          first(
            payload.freshness_score,
            serverData().engine_freshness_score
          )
        ),

      fallback_active:
        fallbackActive,

      summary: {
        present:
          num(summary.present),

        fresh:
          num(summary.fresh),

        stale:
          num(summary.stale),

        missing:
          num(summary.missing),

        fallback_only:
          num(summary.fallback_only),

        caution:
          num(summary.caution),
      },

      files:
        files.map(
          file => ({
            name:
              txt(
                file.name,
                "unknown"
              ),

            exists:
              file.exists === true,

            status:
              txt(
                file.status,
                "unknown"
              ),

            age_minutes:
              num(
                file.age_minutes
              ),

            safe_to_display:
              txt(
                file.safe_to_display,
                "unknown"
              ),

            label:
              txt(
                file.label,
                "Unknown"
              ),
          })
        ),

      boundaries: {
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
      },
    };
  }


  // ================================================================================================
  // OWNER SOURCE AUDIT
  // ================================================================================================

  function sourceAuditState() {
    if (
      window.OB_OWNER_SOURCE_AUDIT_V36_API
      &&
      typeof
      window.OB_OWNER_SOURCE_AUDIT_V36_API.getState
      === "function"
    ) {
      return obj(
        window
          .OB_OWNER_SOURCE_AUDIT_V36_API
          .getState()
      );
    }

    return {};
  }


  function sourceAuditPayload() {
    const state =
      sourceAuditState();

    return obj(
      first(
        state.payload,
        window.OB_OWNER_SOURCE_AUDIT_V36,
        serverData().owner_source_audit_v36
      )
    );
  }


  function normalizeSourceAudit() {
    const state =
      sourceAuditState();

    const payload =
      sourceAuditPayload();

    const summary =
      obj(payload.summary);

    const fallbackActive =
      state.fallbackActive === true
      ||
      lower(payload.source).includes(
        "fallback"
      )
      ||
      lower(
        payload.safe_to_display
      ).includes(
        "fallback"
      );

    let status =
      classifyDisplayTruth(
        first(
          payload.safe_to_display,
          payload.trust_label,
          payload.audit_status,
          state.status
        )
      );

    if (fallbackActive) {
      status = STATUS.GUARDED;
    }

    if (
      num(summary.missing) > 0
    ) {
      status =
        worstStatus([
          status,
          STATUS.DEGRADED,
        ]);
    }

    return {
      status,

      source:
        txt(
          first(
            payload.source,
            state.source
          ),
          "unknown"
        ),

      trust_label:
        txt(
          payload.trust_label,
          "Unknown"
        ),

      safe_to_display:
        txt(
          payload.safe_to_display,
          "unknown"
        ),

      freshness_score:
        num(
          payload.freshness_score
        ),

      fallback_active:
        fallbackActive,

      summary: {
        total_files:
          num(
            summary.total_files
          ),

        present:
          num(
            summary.present
          ),

        fresh:
          num(
            summary.fresh
          ),

        stale:
          num(
            summary.stale
          ),

        missing:
          num(
            summary.missing
          ),

        fallback_only:
          num(
            summary.fallback_only
          ),

        actions:
          num(
            summary.actions
          ),
      },

      files:
        arr(payload.files),

      action_plan:
        arr(payload.action_plan),

      room_impact:
        obj(
          payload.room_impact
        ),

      boundaries: {
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        source_audit_does_not_create_permission:
          true,
        stale_data_cannot_create_permission:
          true,
      },
    };
  }


  // ================================================================================================
  // ENGINE TRUST LABELS
  // ================================================================================================

  function normalizeTrust() {
    let payload = {};

    if (
      window.OB_ENGINE_TRUST_LABELS_V34_API
      &&
      typeof
      window.OB_ENGINE_TRUST_LABELS_V34_API.getState
      === "function"
    ) {
      const state =
        obj(
          window
            .OB_ENGINE_TRUST_LABELS_V34_API
            .getState()
        );

      payload =
        obj(state.payload);
    }

    if (!Object.keys(payload).length) {
      payload =
        obj(
          first(
            window.OB_ENGINE_TRUST_LABELS_V34,
            serverData().engine_trust_labels_v34
          )
        );
    }

    const trust =
      obj(payload.trust);

    const raw =
      first(
        trust.safeToDisplay,
        trust.safe_to_display,
        trust.label,
        trust.level,
        payload.safe_to_display
      );

    return {
      status:
        classifyDisplayTruth(raw),

      label:
        txt(
          first(
            trust.label,
            trust.level
          ),
          "Unknown"
        ),

      safe_to_display:
        txt(
          first(
            trust.safeToDisplay,
            trust.safe_to_display,
            payload.safe_to_display
          ),
          "unknown"
        ),

      freshness_score:
        num(
          payload.freshness_score
        ),
    };
  }


  // ================================================================================================
  // ROOM MAPPING / CHAIN
  // ================================================================================================

  const CANONICAL_ROOMS =
    Object.freeze([
      {
        id: "market_map",
        label: "Market Map",
      },
      {
        id: "symbol_page",
        label: "Symbol Room",
      },
      {
        id: "trade_center",
        label: "Trade Center",
      },
      {
        id: "review_center",
        label: "Review Center",
      },
      {
        id: "owner_console",
        label: "Owner Console",
      },
    ]);


  function mappingPayload() {
    let payload = {};

    if (
      window.OB_ENGINE_ROOM_MAPPING_V35_API
      &&
      typeof
      window.OB_ENGINE_ROOM_MAPPING_V35_API.getState
      === "function"
    ) {
      const state =
        obj(
          window
            .OB_ENGINE_ROOM_MAPPING_V35_API
            .getState()
        );

      payload =
        obj(state.payload);
    }

    if (!Object.keys(payload).length) {
      payload =
        obj(
          first(
            window.OB_ENGINE_ROOM_MAPPING_V35,
            serverData().engine_room_mapping_v35
          )
        );
    }

    return payload;
  }


  function normalizeRooms() {
    const payload =
      mappingPayload();

    const rooms =
      obj(payload.rooms);

    return CANONICAL_ROOMS.map(
      room => {
        const candidate =
          obj(
            first(
              rooms[room.id],
              rooms[
                room.id.replace(
                  "_",
                  "-"
                )
              ]
            )
          );

        const rawStatus =
          first(
            candidate.status,
            candidate.safe_to_display,
            candidate.trust_label,
            candidate.source_status
          );

        return {
          id:
            room.id,

          label:
            room.label,

          status:
            Object.keys(candidate).length
              ? classifyDisplayTruth(
                  rawStatus
                )
              : STATUS.UNKNOWN,

          source:
            txt(
              first(
                candidate.source,
                candidate.source_name
              ),
              "Unknown"
            ),

          safe_to_display:
            txt(
              candidate.safe_to_display,
              "unknown"
            ),
        };
      }
    );
  }


  // ================================================================================================
  // REVIEW CENTER ATTENTION
  // ================================================================================================

  function normalizeReviewAttention() {
    if (
      !window.OBReviewCenterProjection
      ||
      typeof
      window.OBReviewCenterProjection.snapshot
      !== "function"
    ) {
      return {
        status:
          STATUS.UNKNOWN,

        total:
          null,

        attention:
          null,

        overtime:
          null,

        poor_process:
          null,

        source:
          "unavailable",
      };
    }

    const snapshot =
      obj(
        window
          .OBReviewCenterProjection
          .snapshot()
      );

    const records =
      arr(snapshot.records);

    if (!snapshot.loaded) {
      return {
        status:
          STATUS.GUARDED,

        total:
          records.length,

        attention:
          null,

        overtime:
          null,

        poor_process:
          null,

        source:
          "review_projection_not_loaded",
      };
    }

    const attention =
      records.filter(
        record =>
          record.process_quality
          === "POOR"
          ||
          record.process_quality
          === "NEEDS_REVIEW"
          ||
          obj(record.overtime).overtime
          === true
          ||
          arr(record.rule_violations)
            .length > 0
      );

    const overtime =
      records.filter(
        record =>
          obj(record.overtime).overtime
          === true
      );

    const poor =
      records.filter(
        record =>
          record.process_quality
          === "POOR"
      );

    return {
      status:
        attention.length
          ? STATUS.GUARDED
          : STATUS.HEALTHY,

      total:
        records.length,

      attention:
        attention.length,

      overtime:
        overtime.length,

      poor_process:
        poor.length,

      source:
        "OBReviewCenterProjection",
    };
  }


  // ================================================================================================
  // MISSION ACCOUNTS
  //
  // Mission metadata is policy/context, NOT balance truth.
  // We never invent balances, P&L, reserves, or available capital here.
  // ================================================================================================

  const MISSION_IDS =
    Object.freeze([
      "personal",
      "trust",
      "business",
      "atm",
      "apartment",
      "proof",
    ]);


  function selectedMissionId() {
    return (
      document.body
        .getAttribute(
          "data-ob-mission"
        )
      ||
      localStorage.getItem(
        "ob.selectedMissionAccount.v18"
      )
      ||
      null
    );
  }


  function missionStatus(id) {
    const selected =
      selectedMissionId();

    return {
      id,

      selected:
        selected === id,

      capital_balance:
        null,

      available_capital:
        null,

      realized_pnl:
        null,

      risk_utilization:
        null,

      status:
        STATUS.UNKNOWN,

      note:
        "Mission policy exists, but Owner Console does not fabricate live balance or capital-health truth.",
    };
  }


  function normalizeMissions() {
    return MISSION_IDS.map(
      missionStatus
    );
  }


  // ================================================================================================
  // READINESS
  // ================================================================================================

  function readinessValue() {
    const candidates = [
      window.OB_MANUAL_LIVE_L1_READINESS_CHECKPOINT,
      window.OB_MANUAL_LIVE_L1_READINESS_STATE,
      window.OB_MANUAL_LIVE_OWNER_FIRST_RUN_READINESS,
      window.OB_PRIVATE_BETA_LAUNCH_CONTROL,
      window.OB_BETA_READINESS_CHECKPOINT,
      serverData().manual_live_l1_readiness,
      serverData().private_beta_launch_control,
      serverData().beta_readiness,
    ];

    for (const candidate of candidates) {
      if (
        candidate
        &&
        typeof candidate
        === "object"
      ) {
        return obj(candidate);
      }
    }

    return {};
  }


  function normalizeReadiness() {
    const payload =
      readinessValue();

    if (!Object.keys(payload).length) {
      return {
        status:
          STATUS.UNKNOWN,

        label:
          "Unknown",

        blockers:
          [],

        source:
          "unavailable",
      };
    }

    const blockers =
      arr(
        first(
          payload.blockers,
          payload.blocking_items,
          payload.missing,
          payload.failures
        )
      );

    const raw =
      first(
        payload.status,
        payload.readiness,
        payload.state,
        payload.recommendation,
        payload.decision
      );

    let status =
      classifyDisplayTruth(raw);

    if (blockers.length) {
      status =
        worstStatus([
          status,
          STATUS.GUARDED,
        ]);
    }

    return {
      status,

      label:
        txt(
          raw,
          "Unknown"
        ),

      blockers,

      source:
        txt(
          first(
            payload.source,
            payload.version
          ),
          "readiness_layer"
        ),
    };
  }


  // ================================================================================================
  // HARD SAFETY TRUTH
  //
  // These are Owner Console PRODUCT boundaries, not inferred market data.
  // ================================================================================================

  function safetyTruth() {
    return {
      status:
        STATUS.LOCKED,

      read_only:
        true,

      broker_read:
        false,

      broker_execution:
        false,

      automatic_execution:
        false,

      automatic_contract_selection:
        false,

      auto_close:
        false,

      live_auto_locked:
        true,

      manual_live_owner_executes_externally:
        true,
    };
  }


  // ================================================================================================
  // OWNER ATTENTION
  // ================================================================================================

  function buildAttention({
    diagnostics,
    sourceAudit,
    review,
    readiness,
    rooms,
  }) {
    const attention = [];


    if (
      diagnostics.status
      === STATUS.DEGRADED
      ||
      diagnostics.status
      === STATUS.GUARDED
    ) {
      attention.push({
        id:
          "engine-feed",

        severity:
          diagnostics.status,

        title:
          "Engine feed needs review",

        detail:
          diagnostics.fallback_active
            ? "Diagnostics are operating on a guarded/fallback source."
            : "Engine source freshness or availability needs attention.",

        source:
          diagnostics.source,
      });
    }


    if (
      sourceAudit.status
      === STATUS.DEGRADED
      ||
      sourceAudit.status
      === STATUS.GUARDED
    ) {
      const missing =
        sourceAudit.summary.missing;

      const stale =
        sourceAudit.summary.stale;

      attention.push({
        id:
          "source-audit",

        severity:
          sourceAudit.status,

        title:
          "Source audit needs review",

        detail:
          [
            missing !== null
              ? `${missing} missing`
              : null,

            stale !== null
              ? `${stale} stale`
              : null,

            sourceAudit.fallback_active
              ? "fallback active"
              : null,
          ]
            .filter(Boolean)
            .join(" · ")
          ||
          "Source truth is guarded.",

        source:
          sourceAudit.source,
      });
    }


    if (
      review.attention !== null
      &&
      review.attention > 0
    ) {
      attention.push({
        id:
          "review-queue",

        severity:
          STATUS.GUARDED,

        title:
          "Review Center needs you",

        detail:
          `${review.attention} review record`
          +
          (
            review.attention === 1
              ? ""
              : "s"
          )
          +
          " need attention.",

        source:
          review.source,
      });
    }


    if (
      readiness.status
      !== STATUS.HEALTHY
    ) {
      attention.push({
        id:
          "readiness",

        severity:
          readiness.status,

        title:
          "Readiness is not confirmed healthy",

        detail:
          readiness.label,

        source:
          readiness.source,
      });
    }


    for (const room of rooms) {
      if (
        room.status
        === STATUS.DEGRADED
        ||
        room.status
        === STATUS.GUARDED
      ) {
        attention.push({
          id:
            `room-${room.id}`,

          severity:
            room.status,

          title:
            `${room.label} is ${room.status.toLowerCase()}`,

          detail:
            `Source: ${room.source}`,

          source:
            room.source,
        });
      }
    }


    return attention;
  }


  // ================================================================================================
  // SYSTEM HEALTH
  // ================================================================================================

  function buildSystemHealth(
    diagnostics,
    sourceAudit,
    trust,
    readiness,
    rooms,
    review
  ) {
    const roomStatus =
      worstStatus(
        rooms.map(
          room => room.status
        )
      );

    const overall =
      worstStatus([
        diagnostics.status,
        sourceAudit.status,
        trust.status,
        readiness.status,
        roomStatus,
        review.status,
      ]);

    return {
      overall,

      market_truth:
        worstStatus([
          diagnostics.status,
          trust.status,
        ]),

      source_truth:
        sourceAudit.status,

      room_chain:
        roomStatus,

      review_attention:
        review.status,

      readiness:
        readiness.status,

      safety:
        STATUS.LOCKED,
    };
  }


  // ================================================================================================
  // BUILD SNAPSHOT
  // ================================================================================================

  function buildSnapshot() {
    const diagnostics =
      normalizeDiagnostics();

    const sourceAudit =
      normalizeSourceAudit();

    const trust =
      normalizeTrust();

    const rooms =
      normalizeRooms();

    const review =
      normalizeReviewAttention();

    const missions =
      normalizeMissions();

    const readiness =
      normalizeReadiness();

    const safety =
      safetyTruth();

    const health =
      buildSystemHealth(
        diagnostics,
        sourceAudit,
        trust,
        readiness,
        rooms,
        review
      );

    const attention =
      buildAttention({
        diagnostics,
        sourceAudit,
        review,
        readiness,
        rooms,
      });

    return {
      version:
        VERSION,

      timestamp:
        new Date()
          .toISOString(),

      system_health:
        health,

      attention,

      diagnostics,

      source_audit:
        sourceAudit,

      trust,

      rooms,

      review,

      missions,

      readiness,

      safety,

      boundaries: {
        fake_health_fallback:
          false,

        fake_balance_fallback:
          false,

        hardcoded_room_count:
          false,

        broker_read:
          false,

        broker_execution:
          false,

        automatic_execution:
          false,

        auto_close:
          false,

        live_auto_locked:
          true,

        owner_console_read_only:
          true,

        tower_files_modified:
          false,
      },
    };
  }


  // ================================================================================================
  // API
  // ================================================================================================

  let current =
    buildSnapshot();


  function refresh() {
    current =
      buildSnapshot();

    window.dispatchEvent(
      new CustomEvent(
        "ob:owner-console-truth-updated",
        {
          detail:
            current,
        }
      )
    );

    return current;
  }


  function snapshot() {
    return current;
  }


  window.OBOwnerConsoleProjection =
    Object.freeze({
      VERSION,
      STATUS,
      refresh,
      snapshot,
    });


  const events = [
    "obEngineFeedDiagnosticsUpdated",
    "obOwnerSourceAuditUpdated",
    "ob:review-center-projection-updated",
  ];

  for (const name of events) {
    window.addEventListener(
      name,
      function () {
        refresh();
      }
    );
  }


  document.addEventListener(
    "DOMContentLoaded",
    function () {
      setTimeout(
        refresh,
        1500
      );

      setTimeout(
        refresh,
        3000
      );
    }
  );


  window.dispatchEvent(
    new CustomEvent(
      "ob:obux052-owner-console-projection-ready",
      {
        detail: {
          version:
            VERSION,

          fakeHealthFallback:
            false,

          fakeBalanceFallback:
            false,

          brokerExecution:
            false,

          liveAutoLocked:
            true,
        },
      }
    )
  );
})();
