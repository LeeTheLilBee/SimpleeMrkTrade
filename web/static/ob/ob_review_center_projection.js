(function () {
  "use strict";

  const VERSION = "OBUX047_CANONICAL_REVIEW_PROJECTION";

  const TRUTH_MODES = Object.freeze([
    "manual_live",
    "paper",
    "rehearsal",
    "proof",
    "quarantined",
  ]);

  const OFFICIAL_MODES = Object.freeze([
    "manual_live",
    "paper",
  ]);

  const state = {
    loading: false,
    loaded: false,
    errors: [],
    records: [],
    sources: {},
  };


  // ================================================================================================
  // BASIC NORMALIZATION
  // ================================================================================================

  function obj(value) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    ) ? value : {};
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


  function txt(value, fallback = "") {
    const found = first(value);

    return found === null
      ? fallback
      : String(found);
  }


  function lower(value) {
    return txt(value).trim().toLowerCase();
  }


  function normalizeMode(record) {
    const safe = obj(record);

    const raw = lower(
      first(
        safe.truth_mode,
        safe.record_mode,
        safe.mode,
        safe.execution_mode,
        safe.trade_mode,
        safe.environment,
        safe.account_mode
      )
    );

    if (
      raw.includes("quarant")
      || raw.includes("exclude")
    ) {
      return "quarantined";
    }

    if (
      raw.includes("proof")
      || raw.includes("demo")
    ) {
      return "proof";
    }

    if (
      raw.includes("rehears")
      || raw.includes("dry_run")
      || raw.includes("dry-run")
      || raw.includes("fake")
      || safe.is_real_market_execution === false
    ) {
      return "rehearsal";
    }

    if (raw.includes("paper")) {
      return "paper";
    }

    if (
      raw.includes("manual")
      || raw.includes("live")
    ) {
      return "manual_live";
    }

    /*
     * IMPORTANT:
     * Unknown is NOT silently promoted to Manual Live.
     *
     * We keep uncertain data outside official performance.
     */
    return "proof";
  }


  function symbolOf(record) {
    const safe = obj(record);

    return txt(
      first(
        safe.symbol,
        safe.underlying,
        safe.underlying_symbol,
        safe.ticker,
        obj(safe.contract).underlying
      ),
      ""
    ).toUpperCase();
  }


  function contractSymbolOf(record) {
    const safe = obj(record);

    return txt(
      first(
        safe.contract_symbol,
        safe.option_symbol,
        safe.occ_symbol,
        obj(safe.contract).contract_symbol,
        obj(safe.contract).symbol
      ),
      ""
    );
  }


  function normalizeRight(value) {
    const raw = txt(value).trim().toUpperCase();

    if (
      raw === "C"
      || raw === "CALL"
    ) {
      return "CALL";
    }

    if (
      raw === "P"
      || raw === "PUT"
    ) {
      return "PUT";
    }

    return raw;
  }


  function optionIdentity(record) {
    const safe = obj(record);
    const contract = obj(safe.contract);

    return {
      contract_symbol: first(
        safe.contract_symbol,
        safe.option_symbol,
        contract.contract_symbol,
        contract.symbol
      ),

      right: normalizeRight(
        first(
          safe.right,
          safe.option_type,
          contract.right,
          contract.option_type
        )
      ),

      strike: num(
        first(
          safe.strike,
          safe.strike_price,
          contract.strike,
          contract.strike_price
        )
      ),

      expiration: first(
        safe.expiration,
        safe.expiry,
        safe.expiration_date,
        contract.expiration,
        contract.expiry
      ),

      multiplier: num(
        first(
          safe.multiplier,
          contract.multiplier,
          100
        )
      ) || 100,
    };
  }


  // ================================================================================================
  // DATE / DURATION
  // ================================================================================================

  function timestamp(value) {
    if (!value) {
      return null;
    }

    const ms = Date.parse(value);

    return Number.isFinite(ms)
      ? ms
      : null;
  }


  function minutesBetween(start, end) {
    const a = timestamp(start);
    const b = timestamp(end);

    if (
      a === null
      || b === null
      || b < a
    ) {
      return null;
    }

    return Math.round(
      (b - a) / 60000
    );
  }


  function intendedHoldMinutes(record) {
    const safe = obj(record);

    const direct = num(
      first(
        safe.intended_hold_minutes,
        safe.planned_hold_minutes,
        safe.expected_hold_minutes,
        safe.max_hold_minutes
      )
    );

    if (direct !== null) {
      return direct;
    }

    const hours = num(
      first(
        safe.intended_hold_hours,
        safe.planned_hold_hours,
        safe.expected_hold_hours
      )
    );

    if (hours !== null) {
      return hours * 60;
    }

    const plannedExit = first(
      safe.planned_exit_time,
      safe.expected_exit_time,
      safe.hold_window_end
    );

    const plannedEntry = first(
      safe.planned_entry_time,
      safe.entry_time,
      safe.actual_entry_time
    );

    return minutesBetween(
      plannedEntry,
      plannedExit
    );
  }


  function actualHoldMinutes(record) {
    const safe = obj(record);

    const direct = num(
      first(
        safe.actual_hold_minutes,
        safe.hold_duration_minutes
      )
    );

    if (direct !== null) {
      return direct;
    }

    return minutesBetween(
      first(
        safe.actual_entry_time,
        safe.entry_time,
        safe.fill_time,
        safe.opened_at
      ),
      first(
        safe.actual_exit_time,
        safe.close_time,
        safe.exit_time,
        safe.closed_at
      )
    );
  }


  // ================================================================================================
  // P&L / OPTION PREMIUM
  // ================================================================================================

  function premiumResult(record) {
    const safe = obj(record);
    const identity = optionIdentity(safe);

    const entry = num(
      first(
        safe.entry_premium,
        safe.actual_entry_premium,
        safe.fill_price,
        safe.entry_price,
        obj(safe.entry).premium
      )
    );

    const exit = num(
      first(
        safe.exit_premium,
        safe.actual_exit_premium,
        safe.close_price,
        safe.exit_price,
        obj(safe.exit).premium
      )
    );

    const quantity = num(
      first(
        safe.contracts,
        safe.contract_quantity,
        safe.quantity,
        safe.close_quantity,
        1
      )
    );

    if (
      entry === null
      || exit === null
      || quantity === null
    ) {
      return {
        entry_premium: entry,
        exit_premium: exit,
        contracts: quantity,
        multiplier: identity.multiplier,
        premium_pnl: null,
        premium_return_pct: null,
      };
    }

    const pnl = (
      exit - entry
    ) * quantity * identity.multiplier;

    const basis = (
      entry
      * quantity
      * identity.multiplier
    );

    return {
      entry_premium: entry,
      exit_premium: exit,
      contracts: quantity,
      multiplier: identity.multiplier,
      premium_pnl: pnl,
      premium_return_pct:
        basis !== 0
          ? (pnl / basis) * 100
          : null,
    };
  }


  // ================================================================================================
  // NEGATIVE DIVE
  // ================================================================================================

  function excursionMetrics(record) {
    const safe = obj(record);

    const mae = num(
      first(
        safe.maximum_adverse_excursion_pct,
        safe.mae_pct,
        safe.maximum_adverse_excursion,
        obj(safe.excursions).mae_pct
      )
    );

    const mfe = num(
      first(
        safe.maximum_favorable_excursion_pct,
        safe.mfe_pct,
        safe.maximum_favorable_excursion,
        obj(safe.excursions).mfe_pct
      )
    );

    const deepest = num(
      first(
        safe.deepest_drawdown_pct,
        safe.max_drawdown_pct,
        safe.minimum_return_pct
      )
    );

    const negativeMinutes = num(
      first(
        safe.time_negative_minutes,
        safe.minutes_negative,
        safe.negative_duration_minutes
      )
    );

    const belowStopMinutes = num(
      first(
        safe.time_below_stop_minutes,
        safe.minutes_below_stop,
        safe.stop_breach_duration_minutes
      )
    );

    return {
      mae_pct: mae,
      mfe_pct: mfe,
      deepest_drawdown_pct: deepest,
      time_negative_minutes: negativeMinutes,
      time_below_stop_minutes: belowStopMinutes,
    };
  }


  function overtimeMetrics(record) {
    const planned = intendedHoldMinutes(record);
    const actual = actualHoldMinutes(record);

    let overtime = null;

    if (
      planned !== null
      && actual !== null
    ) {
      overtime = Math.max(
        0,
        actual - planned
      );
    }

    return {
      intended_hold_minutes: planned,
      actual_hold_minutes: actual,
      overtime_minutes: overtime,
      overtime:
        overtime !== null
        && overtime > 0,
    };
  }


  // ================================================================================================
  // OUTCOME VS PROCESS
  // ================================================================================================

  function outcomeClass(record, premium) {
    const safe = obj(record);

    const direct = lower(
      first(
        safe.result_class,
        safe.outcome_class,
        safe.final_outcome,
        safe.outcome,
        safe.result
      )
    );

    if (
      direct.includes("not_placed")
      || direct.includes("not placed")
    ) {
      return "NOT_PLACED";
    }

    if (
      direct.includes("flat")
      || direct.includes("scratch")
    ) {
      return "FLAT";
    }

    if (
      direct.includes("loss")
      || direct.includes("lose")
    ) {
      return "LOSS";
    }

    if (
      direct.includes("win")
      || direct.includes("profit")
    ) {
      return "WIN";
    }

    const pnl = num(
      first(
        safe.realized_pnl,
        safe.realized_result,
        safe.pnl,
        premium.premium_pnl
      )
    );

    if (pnl === null) {
      return "UNKNOWN";
    }

    if (pnl > 0) {
      return "WIN";
    }

    if (pnl < 0) {
      return "LOSS";
    }

    return "FLAT";
  }


  function processQuality(record, overtime, excursion) {
    const safe = obj(record);

    const direct = lower(
      first(
        safe.process_quality,
        safe.discipline_quality,
        safe.execution_quality
      )
    );

    if (
      direct === "clean"
      || direct === "good"
      || direct === "excellent"
    ) {
      return "CLEAN";
    }

    if (
      direct.includes("poor")
      || direct.includes("violation")
      || direct.includes("bad")
    ) {
      return "POOR";
    }

    if (
      direct.includes("review")
      || direct.includes("warning")
    ) {
      return "NEEDS_REVIEW";
    }

    const violations = arr(
      first(
        safe.rule_violations,
        safe.violations
      )
    );

    if (violations.length) {
      return "POOR";
    }

    if (
      overtime.overtime === true
      || (
        excursion.time_below_stop_minutes !== null
        && excursion.time_below_stop_minutes > 0
      )
    ) {
      return "NEEDS_REVIEW";
    }

    return "UNKNOWN";
  }


  // ================================================================================================
  // CAUSE TAXONOMY
  //
  // We only surface evidence-supported causes.
  // There is no hidden guess like "loss = owner hesitation".
  // ================================================================================================

  const CAUSES = Object.freeze({
    late_exit: "Late exit",
    stop_ignored: "Stop ignored",
    stale_candidate: "Stale candidate",
    fill_slippage: "Fill slippage",
    alert_delay: "Alert delay",
    owner_hesitation: "Owner hesitation",
    broker_confirmation_gap: "Broker confirmation gap",
    market_reversal: "Market reversal",
    contract_decay: "Contract decay",
    spread_liquidity_failure: "Spread / liquidity failure",
    mission_account_rule_stress: "Mission-account rule stress",
    thesis_deterioration: "Thesis deterioration",
    entry_chase: "Entry chase",
    oversized_position: "Oversized position",
    hold_time_violation: "Hold-time violation",
    source_data_problem: "Source / data problem",
  });


  function explicitCauses(record) {
    const safe = obj(record);

    const raw = [
      ...arr(safe.cause_codes),
      ...arr(safe.issue_codes),
      ...arr(safe.failure_codes),
      ...arr(safe.rule_violations),
    ];

    const normalized = new Set();

    for (const value of raw) {
      const code = lower(value)
        .replaceAll("-", "_")
        .replaceAll(" ", "_");

      if (CAUSES[code]) {
        normalized.add(code);
      }
    }

    /*
     * Quantitative evidence can support two classifications directly.
     * These are not subjective guesses.
     */
    const overtime = overtimeMetrics(safe);
    const excursion = excursionMetrics(safe);

    if (overtime.overtime === true) {
      normalized.add(
        "hold_time_violation"
      );
    }

    if (
      excursion.time_below_stop_minutes !== null
      && excursion.time_below_stop_minutes > 0
    ) {
      normalized.add(
        "stop_ignored"
      );
    }

    const slippage = num(
      first(
        safe.slippage,
        safe.slippage_pct,
        safe.fill_slippage
      )
    );

    if (
      slippage !== null
      && slippage !== 0
    ) {
      normalized.add(
        "fill_slippage"
      );
    }

    return [...normalized].map(
      code => ({
        code,
        label: CAUSES[code],
      })
    );
  }


  // ================================================================================================
  // LIFECYCLE
  // ================================================================================================

  function lifecycle(record) {
    const safe = obj(record);

    const provided = arr(
      first(
        safe.lifecycle,
        safe.lifecycle_events,
        safe.timeline,
        safe.receipt_timeline
      )
    );

    if (provided.length) {
      return provided;
    }

    const stages = [
      [
        "Signal",
        first(
          safe.signal_time,
          safe.candidate_time,
          safe.detected_at
        )
      ],
      [
        "Contract",
        first(
          safe.contract_selected_at,
          safe.contract_time
        )
      ],
      [
        "Preflight",
        first(
          safe.preflight_time,
          safe.preflight_at
        )
      ],
      [
        "Entry",
        first(
          safe.actual_entry_time,
          safe.entry_time,
          safe.fill_time
        )
      ],
      [
        "Exit alert",
        first(
          safe.exit_alert_time,
          safe.exit_review_time
        )
      ],
      [
        "Close",
        first(
          safe.actual_exit_time,
          safe.close_time,
          safe.closed_at
        )
      ],
      [
        "Review",
        first(
          safe.review_time,
          safe.reviewed_at,
          safe.created_at
        )
      ],
    ];

    return stages
      .filter(item => item[1])
      .map(item => ({
        label: item[0],
        timestamp: item[1],
      }));
  }


  // ================================================================================================
  // LESSON
  // ================================================================================================

  function lesson(record) {
    const safe = obj(record);
    const lessonRecord = obj(
      safe.lesson_record
    );

    return {
      what_worked: first(
        safe.what_worked,
        lessonRecord.what_worked
      ),

      what_failed: first(
        safe.what_failed,
        lessonRecord.what_failed
      ),

      missed_warning: first(
        safe.missed_warning,
        lessonRecord.missed_warning
      ),

      what_to_repeat: first(
        safe.what_to_repeat,
        lessonRecord.what_to_repeat
      ),

      what_to_avoid: first(
        safe.what_to_avoid,
        lessonRecord.what_to_avoid
      ),

      best_next_rule: first(
        safe.best_next_rule,
        lessonRecord.best_next_rule
      ),

      owner_notes: first(
        safe.owner_final_notes,
        safe.owner_notes,
        safe.notes,
        lessonRecord.owner_final_notes
      ),
    };
  }


  // ================================================================================================
  // ONE CANONICAL REVIEW RECORD
  // ================================================================================================

  function normalizeReviewRecord(record, sourceName = "unknown") {
    const safe = obj(record);

    const premium = premiumResult(safe);
    const overtime = overtimeMetrics(safe);
    const excursion = excursionMetrics(safe);
    const truthMode = normalizeMode(safe);

    return {
      review_id: txt(
        first(
          safe.review_id,
          safe.receipt_id,
          safe.finalization_id,
          safe.close_id,
          safe.trade_id,
          safe.position_id,
          safe.flow_id,
          safe.candidate_id
        ),
        `review-${sourceName}-${Math.random().toString(36).slice(2)}`
      ),

      source_name: sourceName,

      truth_mode: truthMode,

      official_performance:
        OFFICIAL_MODES.includes(
          truthMode
        ),

      mission_account: first(
        safe.mission_account,
        safe.account,
        safe.account_name,
        safe.mission
      ),

      symbol: symbolOf(safe),

      contract: optionIdentity(safe),

      strategy: first(
        safe.strategy,
        safe.setup,
        safe.trade_strategy
      ),

      created_at: first(
        safe.created_at,
        safe.updated_at,
        safe.timestamp
      ),

      entry: {
        planned_price: num(
          first(
            safe.planned_entry,
            safe.planned_entry_price
          )
        ),

        actual_price: num(
          first(
            safe.actual_entry,
            safe.actual_entry_price,
            safe.fill_price,
            safe.entry_price
          )
        ),

        planned_time: first(
          safe.planned_entry_time
        ),

        actual_time: first(
          safe.actual_entry_time,
          safe.entry_time,
          safe.fill_time
        ),
      },

      exit: {
        planned_price: num(
          first(
            safe.planned_exit,
            safe.planned_exit_price,
            safe.target_plan
          )
        ),

        actual_price: num(
          first(
            safe.actual_exit,
            safe.actual_exit_price,
            safe.close_price,
            safe.exit_price
          )
        ),

        stop: num(
          first(
            safe.stop_plan,
            safe.stop_price,
            safe.planned_stop
          )
        ),

        planned_time: first(
          safe.planned_exit_time,
          safe.expected_exit_time,
          safe.hold_window_end
        ),

        actual_time: first(
          safe.actual_exit_time,
          safe.close_time,
          safe.exit_time,
          safe.closed_at
        ),

        reason: first(
          safe.close_reason,
          safe.exit_reason,
          safe.reason
        ),
      },

      premium,

      realized_pnl: num(
        first(
          safe.realized_pnl,
          safe.pnl,
          safe.realized_result,
          premium.premium_pnl
        )
      ),

      realized_return_pct: num(
        first(
          safe.realized_return_pct,
          safe.result_pct,
          safe.return_pct,
          premium.premium_return_pct
        )
      ),

      outcome_class:
        outcomeClass(
          safe,
          premium
        ),

      process_quality:
        processQuality(
          safe,
          overtime,
          excursion
        ),

      overtime,

      negative_dive: excursion,

      causes:
        explicitCauses(safe),

      rule_violations: arr(
        first(
          safe.rule_violations,
          safe.violations
        )
      ),

      lesson:
        lesson(safe),

      lifecycle:
        lifecycle(safe),

      raw_source: safe,
    };
  }


  // ================================================================================================
  // DATA EXTRACTION
  // ================================================================================================

  function recordsFromPayload(payload) {
    if (Array.isArray(payload)) {
      return payload;
    }

    const safe = obj(payload);

    const candidates = [
      safe.records,
      safe.reviews,
      safe.receipts,
      safe.finalizations,
      safe.items,
      safe.results,
      safe.data,
    ];

    for (const candidate of candidates) {
      if (Array.isArray(candidate)) {
        return candidate;
      }
    }

    for (const key of [
      "receipt",
      "finalization",
      "review",
      "record",
    ]) {
      if (
        safe[key]
        && typeof safe[key] === "object"
      ) {
        return [safe[key]];
      }
    }

    return [];
  }


  async function safeLoad(name, loader) {
    try {
      const payload = await loader();

      state.sources[name] = {
        ok: true,
        payload,
      };

      return recordsFromPayload(
        payload
      );
    } catch (error) {
      state.errors.push({
        source: name,
        error:
          error
          && error.message
            ? error.message
            : String(error),
      });

      state.sources[name] = {
        ok: false,
      };

      return [];
    }
  }


  function globalRecords() {
    const records = [];

    const server = obj(
      window.OB_SERVER_DATA
    );

    for (const [key, value] of Object.entries(server)) {
      if (
        !key.toLowerCase().includes("review")
        && !key.toLowerCase().includes("receipt")
        && !key.toLowerCase().includes("close")
        && !key.toLowerCase().includes("outcome")
      ) {
        continue;
      }

      for (const record of recordsFromPayload(value)) {
        records.push({
          record,
          source: `OB_SERVER_DATA.${key}`,
        });
      }
    }

    return records;
  }


  function dedupe(records) {
    const seen = new Set();
    const output = [];

    for (const record of records) {
      const key = [
        record.review_id,
        record.truth_mode,
        record.symbol,
        record.contract.contract_symbol || "",
      ].join("|");

      if (seen.has(key)) {
        continue;
      }

      seen.add(key);
      output.push(record);
    }

    return output;
  }


  async function refresh() {
    state.loading = true;
    state.errors = [];
    state.sources = {};

    const collected = [];

    /*
     * Durable/newer sources.
     */
    if (
      window.OBOutcomeReceiptMaterialization
      && typeof window.OBOutcomeReceiptMaterialization.list === "function"
    ) {
      const rows = await safeLoad(
        "gp044_outcome_receipts",
        () =>
          window.OBOutcomeReceiptMaterialization.list()
      );

      rows.forEach(
        row => collected.push(
          normalizeReviewRecord(
            row,
            "gp044_outcome_receipts"
          )
        )
      );
    }

    if (
      window.OBDryRunOutcomeFinalization
      && typeof window.OBDryRunOutcomeFinalization.list === "function"
    ) {
      const rows = await safeLoad(
        "gp043_outcome_finalizations",
        () =>
          window.OBDryRunOutcomeFinalization.list()
      );

      rows.forEach(
        row => collected.push(
          normalizeReviewRecord(
            row,
            "gp043_outcome_finalizations"
          )
        )
      );
    }

    /*
     * Existing Review / close / receipt globals.
     */
    for (
      const item
      of globalRecords()
    ) {
      collected.push(
        normalizeReviewRecord(
          item.record,
          item.source
        )
      );
    }

    state.records = dedupe(
      collected
    );

    state.loaded = true;
    state.loading = false;

    window.dispatchEvent(
      new CustomEvent(
        "ob:review-center-projection-updated",
        {
          detail: {
            version: VERSION,
            records: state.records,
            errors: state.errors,
            sources: state.sources,
          },
        }
      )
    );

    return getSnapshot();
  }


  function getSnapshot() {
    return {
      version: VERSION,
      loaded: state.loaded,
      loading: state.loading,
      records: [...state.records],
      errors: [...state.errors],
      sources: {...state.sources},

      boundaries: {
        broker_execution_enabled: false,
        broker_read_enabled: false,
        auto_close_enabled: false,
        auto_execution_enabled: false,
        live_auto_locked: true,
        fake_performance_fallback_enabled: false,
      },
    };
  }


  window.OBReviewCenterProjection =
    Object.freeze({
      refresh,
      snapshot: getSnapshot,
      normalizeReviewRecord,
      truthModes: [...TRUTH_MODES],
      causes: {...CAUSES},
    });

  window.dispatchEvent(
    new CustomEvent(
      "ob:obux047-ready",
      {
        detail: {
          version: VERSION,
          fakePerformanceFallbackEnabled: false,
          liveAutoLocked: true,
        },
      }
    )
  );
})();
