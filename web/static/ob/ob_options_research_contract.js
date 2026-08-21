// ==============================================================================================
// 🔭 THE OBSERVATORY — OBDATA006
// CANONICAL OPTIONS RESEARCH PROJECTION CONTRACT
// ==============================================================================================
//
// This module DOES NOT select an option contract for the user.
//
// It translates existing source-backed engine option intelligence into a stable research shape
// for Observatory web rooms.
//
// Authority boundary:
//
//   engine scoring/ranking  -> may be projected
//   engine notes            -> may be projected
//   executable diagnostics  -> may be projected as factual diagnostics
//
//   automatic selection     -> NOT web/user authority in Manual Live 1 or Hybrid
//   brokerage execution     -> NEVER performed here
//   fake option fallback    -> NEVER created here
// ==============================================================================================

(function () {
  "use strict";

  const CONTRACT_VERSION = "OB_OPTIONS_RESEARCH_V1";

  const ARRAY_KEYS = Object.freeze([
    "ranked_contracts",
    "top_ranked_contracts",
    "research_contracts",
    "option_chain",
    "options_chain",
    "options",
    "contracts"
  ]);

  const CONTAINER_KEYS = Object.freeze([
    "options",
    "option",
    "option_result",
    "options_result",
    "options_intelligence",
    "option_intelligence",
    "vehicle",
    "vehicle_result",
    "vehicle_diagnostics",
    "lifecycle",
    "execution",
    "candidate",
    "candidates",
    "symbols",
    "data",
    "payload"
  ]);

  function isObject(value) {
    return Boolean(
      value &&
      typeof value === "object" &&
      !Array.isArray(value)
    );
  }

  function safeArray(value) {
    return Array.isArray(value)
      ? value
      : [];
  }

  function safeText(value, fallback = "") {
    if (
      value === null ||
      value === undefined
    ) {
      return fallback;
    }

    const text = String(value).trim();

    return text || fallback;
  }

  function safeNumber(value, fallback = null) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return fallback;
    }

    const number = Number(value);

    return Number.isFinite(number)
      ? number
      : fallback;
  }

  function safeBoolean(value, fallback = false) {
    if (
      value === true ||
      value === false
    ) {
      return value;
    }

    return fallback;
  }

  function firstText(source, keys, fallback = "") {
    for (const key of keys) {
      const value = safeText(
        source?.[key],
        ""
      );

      if (value) {
        return value;
      }
    }

    return fallback;
  }

  function firstNumber(source, keys, fallback = null) {
    for (const key of keys) {
      const value = safeNumber(
        source?.[key],
        null
      );

      if (value !== null) {
        return value;
      }
    }

    return fallback;
  }

  function normalizeRight(value) {
    const raw = safeText(
      value,
      ""
    ).toUpperCase();

    if (
      raw === "C" ||
      raw === "CALL" ||
      raw === "CALLS" ||
      raw === "LONG_CALL"
    ) {
      return "CALL";
    }

    if (
      raw === "P" ||
      raw === "PUT" ||
      raw === "PUTS" ||
      raw === "LONG_PUT"
    ) {
      return "PUT";
    }

    return raw;
  }

  function deriveMark(source) {
    const bid = firstNumber(
      source,
      ["bid"],
      null
    );

    const ask = firstNumber(
      source,
      ["ask"],
      null
    );

    if (
      bid !== null &&
      ask !== null &&
      bid > 0 &&
      ask > 0 &&
      ask >= bid
    ) {
      return Number(
        ((bid + ask) / 2).toFixed(4)
      );
    }

    return firstNumber(
      source,
      [
        "mark",
        "selected_price_reference",
        "price_reference",
        "last",
        "lastPrice",
        "last_price",
        "price"
      ],
      null
    );
  }

  function deriveSpread(source, mark) {
    const explicit = firstNumber(
      source,
      [
        "spread",
        "bidAskSpread"
      ],
      null
    );

    if (explicit !== null) {
      return explicit;
    }

    const bid = firstNumber(
      source,
      ["bid"],
      null
    );

    const ask = firstNumber(
      source,
      ["ask"],
      null
    );

    if (
      bid !== null &&
      ask !== null &&
      ask >= bid
    ) {
      return Number(
        (ask - bid).toFixed(4)
      );
    }

    return null;
  }

  function deriveSpreadPct(source, spread, mark) {
    const explicit = firstNumber(
      source,
      [
        "spread_pct",
        "spreadPercent",
        "spread_percent"
      ],
      null
    );

    if (explicit !== null) {
      return explicit;
    }

    const ask = firstNumber(
      source,
      ["ask"],
      null
    );

    if (
      spread !== null &&
      ask !== null &&
      ask > 0
    ) {
      return Number(
        (spread / ask).toFixed(6)
      );
    }

    if (
      spread !== null &&
      mark !== null &&
      mark > 0
    ) {
      return Number(
        (spread / mark).toFixed(6)
      );
    }

    return null;
  }

  function normalizeContract(raw, context = {}) {
    if (!isObject(raw)) {
      return null;
    }

    const symbol = firstText(
      raw,
      [
        "symbol",
        "underlying_symbol",
        "ticker"
      ],
      safeText(
        context.symbol,
        ""
      )
    ).toUpperCase();

    const contractSymbol = firstText(
      raw,
      [
        "contractSymbol",
        "contract_symbol",
        "option_symbol",
        "occ_symbol",
        "selected_contract_symbol"
      ],
      ""
    );

    const right = normalizeRight(
      firstText(
        raw,
        [
          "right",
          "option_type",
          "type",
          "side",
          "strategy"
        ],
        context.right || ""
      )
    );

    const strike = firstNumber(
      raw,
      [
        "strike",
        "strike_price",
        "option_strike"
      ],
      null
    );

    const expiration = firstText(
      raw,
      [
        "expiration",
        "expiry",
        "expiration_date",
        "expiry_date",
        "option_expiration"
      ],
      ""
    );

    const dte = firstNumber(
      raw,
      [
        "dte",
        "days_to_expiration",
        "daysToExpiration"
      ],
      null
    );

    const bid = firstNumber(
      raw,
      ["bid"],
      null
    );

    const ask = firstNumber(
      raw,
      ["ask"],
      null
    );

    const last = firstNumber(
      raw,
      [
        "last",
        "lastPrice",
        "last_price"
      ],
      null
    );

    const mark = deriveMark(raw);

    const spread = deriveSpread(
      raw,
      mark
    );

    const spreadPct = deriveSpreadPct(
      raw,
      spread,
      mark
    );

    const volume = firstNumber(
      raw,
      ["volume"],
      null
    );

    const openInterest = firstNumber(
      raw,
      [
        "open_interest",
        "openInterest"
      ],
      null
    );

    const impliedVolatility = firstNumber(
      raw,
      [
        "implied_volatility",
        "impliedVolatility",
        "iv"
      ],
      null
    );

    const contractScore = firstNumber(
      raw,
      [
        "contract_score",
        "option_score",
        "score"
      ],
      null
    );

    const contractNotes = safeArray(
      raw.contract_notes ||
      raw.option_notes ||
      raw.notes
    )
      .map(
        item => safeText(
          item,
          ""
        )
      )
      .filter(Boolean);

    const quoteFlags = isObject(
      raw.quote_flags
    )
      ? { ...raw.quote_flags }
      : {};

    const executionReason = firstText(
      raw,
      [
        "execution_reason",
        "option_reason",
        "reason"
      ],
      ""
    );

    const executionCategory = firstText(
      raw,
      [
        "execution_category",
        "category"
      ],
      ""
    );

    const quoteQuality = firstText(
      raw,
      [
        "quote_quality",
        "quoteQuality"
      ],
      ""
    );

    const isExecutable =
      typeof raw.is_executable === "boolean"
        ? raw.is_executable
        : null;

    const source = firstText(
      raw,
      [
        "source",
        "data_source",
        "quote_source"
      ],
      safeText(
        context.source,
        "ENGINE_OPTIONS_INTELLIGENCE"
      )
    );

    const hasIdentity = Boolean(
      contractSymbol ||
      (
        symbol &&
        right &&
        strike !== null &&
        expiration
      )
    );

    const hasMarketEvidence = Boolean(
      bid !== null ||
      ask !== null ||
      last !== null ||
      mark !== null ||
      volume !== null ||
      openInterest !== null
    );

    const hasResearchEvidence = Boolean(
      contractScore !== null ||
      contractNotes.length ||
      executionReason ||
      Object.keys(
        quoteFlags
      ).length
    );

    if (
      !hasIdentity &&
      !hasMarketEvidence &&
      !hasResearchEvidence
    ) {
      return null;
    }

    return Object.freeze({
      schema_version:
        CONTRACT_VERSION,

      authority:
        "ENGINE_RESEARCH_PROJECTION",

      current_market_truth:
        hasMarketEvidence,

      source_backed:
        true,

      symbol,

      contract_symbol:
        contractSymbol,

      contractSymbol,

      right,

      option_type:
        right,

      strike,

      expiration,

      expiry:
        expiration,

      dte,

      bid,

      ask,

      last,

      mark,

      spread,

      spread_pct:
        spreadPct,

      volume,

      open_interest:
        openInterest,

      openInterest,

      implied_volatility:
        impliedVolatility,

      contract_score:
        contractScore,

      contract_notes:
        Object.freeze(
          contractNotes
        ),

      quote_quality:
        quoteQuality,

      quote_flags:
        Object.freeze(
          quoteFlags
        ),

      is_executable:
        isExecutable,

      execution_reason:
        executionReason,

      execution_category:
        executionCategory,

      source,

      // ------------------------------------------------------------------
      // HARD USER-AUTHORITY BOUNDARY
      // ------------------------------------------------------------------

      research_only:
        true,

      ob_selected_contract:
        false,

      user_selected_contract:
        false,

      owner_selected_contract:
        false,

      automatic_contract_selection:
        false,

      brokerage_execution:
        false,

      automatic_execution:
        false
    });
  }

  function looksLikeContract(value) {
    if (!isObject(value)) {
      return false;
    }

    return Boolean(
      value.contractSymbol ||
      value.contract_symbol ||
      value.strike ||
      value.expiration ||
      value.expiry ||
      value.option_type ||
      value.right
    );
  }

  function pushUnique(
    bucket,
    seen,
    raw,
    context
  ) {
    const normalized = normalizeContract(
      raw,
      context
    );

    if (!normalized) {
      return;
    }

    const key = [
      normalized.symbol,
      normalized.contract_symbol,
      normalized.right,
      normalized.strike,
      normalized.expiration,
      normalized.mark,
      normalized.contract_score
    ].join("|");

    if (seen.has(key)) {
      return;
    }

    seen.add(key);
    bucket.push(normalized);
  }

  function collectContracts(
    root,
    context = {}
  ) {
    const contracts = [];
    const seen = new Set();
    const visited = new WeakSet();

    function walk(value, depth = 0, inherited = {}) {
      if (
        depth > 12 ||
        value === null ||
        value === undefined
      ) {
        return;
      }

      if (Array.isArray(value)) {
        for (const item of value) {
          if (looksLikeContract(item)) {
            pushUnique(
              contracts,
              seen,
              item,
              inherited
            );
          } else {
            walk(
              item,
              depth + 1,
              inherited
            );
          }
        }

        return;
      }

      if (!isObject(value)) {
        return;
      }

      if (visited.has(value)) {
        return;
      }

      visited.add(value);

      const nextContext = {
        symbol:
          firstText(
            value,
            [
              "symbol",
              "underlying_symbol",
              "ticker"
            ],
            inherited.symbol ||
            context.symbol ||
            ""
          ),

        right:
          firstText(
            value,
            [
              "right",
              "option_type",
              "strategy"
            ],
            inherited.right ||
            context.right ||
            ""
          ),

        source:
          firstText(
            value,
            [
              "source",
              "data_source"
            ],
            inherited.source ||
            context.source ||
            "ENGINE_OPTIONS_INTELLIGENCE"
          )
      };

      // ----------------------------------------------------------------
      // Do NOT treat engine "best" fields as web selection authority.
      //
      // We may mine the contract as research evidence ONLY when the same
      // container exposes ranked/research information. The object itself
      // is normalized with ob_selected_contract:false.
      // ----------------------------------------------------------------

      for (const key of ARRAY_KEYS) {
        const rows = value[key];

        if (!Array.isArray(rows)) {
          continue;
        }

        for (const row of rows) {
          if (looksLikeContract(row)) {
            pushUnique(
              contracts,
              seen,
              row,
              nextContext
            );
          }
        }
      }

      // Preserve a single option/contract payload if it is source-backed
      // lifecycle data, but never convert it into "selected by OB".
      for (const key of [
        "contract",
        "option"
      ]) {
        const row = value[key];

        if (looksLikeContract(row)) {
          pushUnique(
            contracts,
            seen,
            row,
            nextContext
          );
        }
      }

      for (const key of CONTAINER_KEYS) {
        const nested = value[key];

        if (
          nested !== undefined &&
          nested !== value
        ) {
          walk(
            nested,
            depth + 1,
            nextContext
          );
        }
      }
    }

    walk(
      root,
      0,
      context
    );

    return contracts;
  }

  function rankResearchContracts(contracts) {
    return [...safeArray(contracts)]
      .sort(
        (a, b) => {
          const scoreA = safeNumber(
            a.contract_score,
            -999999
          );

          const scoreB = safeNumber(
            b.contract_score,
            -999999
          );

          if (scoreB !== scoreA) {
            return scoreB - scoreA;
          }

          const execA =
            a.is_executable === true
              ? 1
              : 0;

          const execB =
            b.is_executable === true
              ? 1
              : 0;

          if (execB !== execA) {
            return execB - execA;
          }

          const spreadA = safeNumber(
            a.spread_pct,
            999999
          );

          const spreadB = safeNumber(
            b.spread_pct,
            999999
          );

          if (spreadA !== spreadB) {
            return spreadA - spreadB;
          }

          const volumeA = safeNumber(
            a.volume,
            -1
          );

          const volumeB = safeNumber(
            b.volume,
            -1
          );

          if (volumeB !== volumeA) {
            return volumeB - volumeA;
          }

          const oiA = safeNumber(
            a.open_interest,
            -1
          );

          const oiB = safeNumber(
            b.open_interest,
            -1
          );

          return oiB - oiA;
        }
      );
  }

  function groupBySymbol(contracts) {
    const grouped = {};

    for (
      const contract
      of safeArray(contracts)
    ) {
      const symbol = safeText(
        contract.symbol,
        ""
      ).toUpperCase();

      if (!symbol) {
        continue;
      }

      if (!grouped[symbol]) {
        grouped[symbol] = [];
      }

      grouped[symbol].push(
        contract
      );
    }

    for (
      const symbol
      of Object.keys(grouped)
    ) {
      grouped[symbol] =
        Object.freeze(
          rankResearchContracts(
            grouped[symbol]
          )
        );
    }

    return Object.freeze(
      grouped
    );
  }

  function buildProjection(raw) {
    const contracts =
      rankResearchContracts(
        collectContracts(
          raw,
          {
            source:
              "ENGINE_OPTIONS_INTELLIGENCE"
          }
        )
      );

    const bySymbol =
      groupBySymbol(
        contracts
      );

    return Object.freeze({
      schema_version:
        CONTRACT_VERSION,

      authority:
        "ENGINE_OPTIONS_INTELLIGENCE",

      selection_authority:
        "USER",

      engine_ranking_visible:
        true,

      engine_selection_visible_as_authority:
        false,

      research_contracts:
        Object.freeze(
          contracts
        ),

      ranked_contracts:
        Object.freeze(
          contracts
        ),

      options_by_symbol:
        bySymbol,

      option_chains:
        bySymbol,

      diagnostics:
        Object.freeze({
          contract_count:
            contracts.length,

          symbols_with_contracts:
            Object.keys(
              bySymbol
            ).length,

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
            false
        })
    });
  }

  window.OBOptionsResearchContract = Object.freeze({
    CONTRACT_VERSION,
    normalizeContract,
    collectContracts,
    rankResearchContracts,
    groupBySymbol,
    buildProjection
  });
})();
