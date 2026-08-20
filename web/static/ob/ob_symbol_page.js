// =================================================================================================
// THE OBSERVATORY — SYMBOL ROOM
// OBUX036–OBUX040
//
// CANONICAL DATA ONLY.
// NO independent fetch.
// NO static market fixture.
// NO fabricated market values.
// NO broker execution.
// =================================================================================================

(function () {
  "use strict";

  const VERSION = "OBUX036_OBUX040_SYMBOL_ROOM";
  const HANDOFF_KEY = "ob_symbol_room_trade_center_handoff_v1";

  let selectedExpiration = null;
  let selectedContract = null;
  let latestState = null;
  let latestFeedEventAt = null;

  function byId(id) {
    return document.getElementById(id);
  }

  function safeObject(value) {
    return (
      value &&
      typeof value === "object" &&
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

  function firstDefined(...values) {
    for (const value of values) {
      if (
        value !== undefined &&
        value !== null &&
        value !== ""
      ) {
        return value;
      }
    }

    return null;
  }

  function text(value, fallback = "—") {
    return (
      value === null ||
      value === undefined ||
      value === ""
    )
      ? fallback
      : String(value);
  }

  function number(value) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return null;
    }

    const parsed = Number(value);
    return Number.isFinite(parsed)
      ? parsed
      : null;
  }

  function formatNumber(value, digits = 2) {
    const parsed = number(value);
    if (parsed === null) return "—";

    return parsed.toLocaleString(
      undefined,
      {
        maximumFractionDigits: digits,
      }
    );
  }

  function formatPercent(value) {
    const parsed = number(value);
    if (parsed === null) return "—";

    const sign = parsed > 0 ? "+" : "";
    return sign + parsed.toFixed(2) + "%";
  }

  function formatMoney(value) {
    const parsed = number(value);
    if (parsed === null) return "—";

    return parsed.toLocaleString(
      undefined,
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
      }
    );
  }

  function formatDate(value) {
    if (!value) return "Unavailable";

    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
      return String(value);
    }

    return parsed.toLocaleString();
  }

  function routeSymbol() {
    const room =
      byId("obSymbolRoom");

    return String(
      (
        room &&
        room.getAttribute("data-symbol")
      ) ||
      (
        document.body &&
        document.body.getAttribute("data-ob-symbol")
      ) ||
      ""
    )
      .trim()
      .toUpperCase();
  }

  function canonicalProjection() {
    const api =
      window.OB_ENGINE_FEED_ADAPTER_V25 ||
      window.OB_CANONICAL_WEB_PROJECTION_OBDATA003_API;

    if (
      api &&
      typeof api.getProjection === "function"
    ) {
      return safeObject(
        api.getProjection()
      );
    }

    return safeObject(
      window.OB_ENGINE_FEED_SNAPSHOT_V25
    );
  }

  function symbolContract(symbol) {
    const contracts =
      window.OB_DATA_CONTRACTS_V22;

    if (
      contracts &&
      typeof contracts.symbolPageContract === "function"
    ) {
      return safeObject(
        contracts.symbolPageContract(symbol)
      );
    }

    return {
      symbol_header: {
        symbol,
        unavailable: true,
      },
      star_state: {},
      star_facts: null,
      soulaana_read: {},
      risk_permission: {},
      movement_field: {},
      trade_context: {},
      source: null,
      as_of: null,
      freshness: "unavailable",
    };
  }

  function modeState() {
    const modes =
      window.OB_SYMBOL_ROOM_MODES_OBUX037;

    if (
      modes &&
      typeof modes.current === "function"
    ) {
      return modes.current();
    }

    return {
      key: "survey",
      label: "Survey",
      verb: "Observe",
      message:
        "Mode authority is unavailable, so the Symbol Room failed closed to Survey.",
      observation: true,
      inspect_options: true,
      compare_facts: true,
      paper_build: false,
      scenario_test: false,
      live_signal_context: false,
      objective_option_set: false,
      contract_selection: false,
      trade_handoff: false,
      trade_handoff_kind: null,
      broker_api: false,
      brokerage_execution: false,
      automatic_contract_selection: false,
      automatic_execution: false,
      locked: false,
      authorization: {
        requested: "survey",
        effective: "survey",
        permitted: true,
        locked: false,
      },
    };
  }

  function symbolMatches(value, symbol) {
    const raw =
      typeof value === "string"
        ? value
        : firstDefined(
            value && value.symbol,
            value && value.ticker,
            value && value.underlying,
            value && value.underlying_symbol
          );

    return String(raw || "")
      .trim()
      .toUpperCase() === symbol;
  }

  function recordsForSymbol(values, symbol) {
    return safeArray(values)
      .filter(
        item =>
          symbolMatches(
            item,
            symbol
          )
      );
  }

  function sourceEvidence(projection, symbol) {
    return {
      signals:
        recordsForSymbol(
          projection.signals,
          symbol
        ),

      candidates:
        recordsForSymbol(
          projection.candidates_preview,
          symbol
        ),

      watchlist:
        recordsForSymbol(
          projection.watchlist,
          symbol
        ),

      positions:
        recordsForSymbol(
          projection.positions_preview,
          symbol
        ),

      manualLive:
        recordsForSymbol(
          projection.manual_live_queue,
          symbol
        ),
    };
  }

  function findRawSymbol(projection, symbol) {
    const direct =
      safeArray(projection.symbols)
        .find(
          item =>
            symbolMatches(
              item,
              symbol
            )
        );

    if (direct) return safeObject(direct);

    for (const sector of safeArray(projection.sectors)) {
      const match =
        safeArray(sector.symbols)
          .find(
            item =>
              symbolMatches(
                item,
                symbol
              )
          );

      if (match) {
        return {
          ...safeObject(match),
          sector:
            firstDefined(
              match.sector,
              sector.name,
              sector.sector
            ),
          constellationName:
            firstDefined(
              match.constellationName,
              sector.constellationName
            ),
        };
      }
    }

    return {};
  }

  function underlyingFrom(
    projection,
    contract,
    symbol
  ) {
    const header =
      safeObject(
        contract.symbol_header
      );

    const facts =
      safeObject(
        contract.star_facts
      );

    const raw =
      {
        ...findRawSymbol(
          projection,
          symbol
        ),
        ...safeObject(facts.raw),
        ...facts,
        ...header,
      };

    return {
      symbol,
      company:
        firstDefined(
          raw.company,
          raw.company_name,
          raw.name
        ),

      sector:
        firstDefined(
          raw.constellationName,
          raw.sectorName,
          raw.sector
        ),

      state:
        firstDefined(
          raw.market_state,
          raw.state,
          raw.position,
          raw.status,
          raw.tier
        ),

      price:
        firstDefined(
          raw.price,
          raw.last,
          raw.last_price,
          raw.mark,
          raw.current_price
        ),

      change:
        firstDefined(
          raw.change_percent,
          raw.change_pct,
          raw.percent_change,
          raw.pct_change
        ),

      volume:
        firstDefined(
          raw.volume,
          raw.day_volume
        ),

      relativeVolume:
        firstDefined(
          raw.relative_volume,
          raw.relativeVolume,
          raw.rvol
        ),

      dayLow:
        firstDefined(
          raw.day_low,
          raw.low
        ),

      dayHigh:
        firstDefined(
          raw.day_high,
          raw.high
        ),

      iv:
        firstDefined(
          raw.implied_volatility,
          raw.iv
        ),

      trend:
        firstDefined(
          raw.trend,
          raw.direction
        ),

      momentum:
        firstDefined(
          raw.momentum,
          raw.momentum_state
        ),

      relativeStrength:
        firstDefined(
          raw.relative_strength,
          raw.relativeStrength
        ),

      permission:
        firstDefined(
          raw.permission,
          safeObject(
            contract.risk_permission
          ).permission
        ),

      risk:
        firstDefined(
          raw.risk,
          safeObject(
            contract.risk_permission
          ).risk
        ),

      role:
        raw.role || null,
      why:
        firstDefined(
          raw.why,
          raw.opinion
        ),
      fact:
        raw.fact || null,

      raw,
    };
  }

  // -----------------------------------------------------------------------------------------------
  // OPTIONS DATA NORMALIZATION
  //
  // This layer intentionally accepts OPTIONS DATA ONLY IF IT IS PRESENT
  // in the canonical projection / canonical symbol record.
  //
  // It does not fetch a separate chain.
  // It does not fabricate a chain.
  // -----------------------------------------------------------------------------------------------

  function optionsContainers(
    projection,
    underlying
  ) {
    return [
      underlying.raw.options,
      underlying.raw.option_chain,
      underlying.raw.options_chain,

      projection.options &&
        projection.options[
          underlying.symbol
        ],

      projection.options_by_symbol &&
        projection.options_by_symbol[
          underlying.symbol
        ],

      projection.option_chains &&
        projection.option_chains[
          underlying.symbol
        ],

      projection.options_chains &&
        projection.options_chains[
          underlying.symbol
        ],
    ].filter(Boolean);
  }

  function normalizeContract(
    value,
    expirationHint
  ) {
    const raw = safeObject(value);

    const strike =
      number(
        firstDefined(
          raw.strike,
          raw.strike_price
        )
      );

    const type =
      String(
        firstDefined(
          raw.type,
          raw.option_type,
          raw.right,
          raw.call_put
        ) || ""
      )
        .trim()
        .toLowerCase();

    const expiration =
      firstDefined(
        raw.expiration,
        raw.expiry,
        raw.expiration_date,
        expirationHint
      );

    const symbol =
      firstDefined(
        raw.contract_symbol,
        raw.contract,
        raw.symbol,
        raw.local_symbol
      );

    return {
      id:
        String(
          symbol ||
          [
            expiration || "unknown-expiry",
            strike === null ? "unknown-strike" : strike,
            type || "option",
          ].join(":")
        ),

      symbol:
        symbol || null,

      expiration:
        expiration || null,

      strike,

      type:
        type.includes("put")
          ? "put"
          : (
              type.includes("call")
                ? "call"
                : type || null
            ),

      bid:
        number(raw.bid),

      ask:
        number(raw.ask),

      last:
        number(
          firstDefined(
            raw.last,
            raw.last_price
          )
        ),

      mark:
        number(
          firstDefined(
            raw.mark,
            raw.mid,
            raw.midpoint
          )
        ),

      volume:
        number(raw.volume),

      openInterest:
        number(
          firstDefined(
            raw.open_interest,
            raw.openInterest,
            raw.oi
          )
        ),

      iv:
        number(
          firstDefined(
            raw.implied_volatility,
            raw.iv
          )
        ),

      delta:
        number(raw.delta),

      gamma:
        number(raw.gamma),

      theta:
        number(raw.theta),

      vega:
        number(raw.vega),

      dte:
        number(
          firstDefined(
            raw.dte,
            raw.days_to_expiration
          )
        ),

      raw,
    };
  }

  function normalizeOptions(
    projection,
    underlying
  ) {
    const containers =
      optionsContainers(
        projection,
        underlying
      );

    const contracts = [];
    let overview = {};

    function add(value, expirationHint) {
      const normalized =
        normalizeContract(
          value,
          expirationHint
        );

      if (
        normalized.strike === null &&
        !normalized.symbol
      ) {
        return;
      }

      contracts.push(normalized);
    }

    for (const containerValue of containers) {
      const container =
        safeObject(containerValue);

      overview = {
        ...overview,
        ...safeObject(
          container.overview
        ),
      };

      const directContracts =
        firstDefined(
          container.contracts,
          container.options,
          container.chain
        );

      if (Array.isArray(directContracts)) {
        directContracts.forEach(
          item =>
            add(
              item,
              null
            )
        );
      }

      for (const expiration of safeArray(container.expirations)) {
        if (
          typeof expiration === "string"
        ) {
          continue;
        }

        const expiry =
          firstDefined(
            expiration.expiration,
            expiration.expiry,
            expiration.date
          );

        safeArray(
          firstDefined(
            expiration.contracts,
            expiration.options,
            expiration.chain
          )
        ).forEach(
          item =>
            add(
              item,
              expiry
            )
        );

        safeArray(expiration.calls)
          .forEach(
            item =>
              add(
                {
                  ...item,
                  type: "call",
                },
                expiry
              )
          );

        safeArray(expiration.puts)
          .forEach(
            item =>
              add(
                {
                  ...item,
                  type: "put",
                },
                expiry
              )
          );
      }

      safeArray(container.calls)
        .forEach(
          item =>
            add(
              {
                ...item,
                type: "call",
              },
              container.expiration
            )
        );

      safeArray(container.puts)
        .forEach(
          item =>
            add(
              {
                ...item,
                type: "put",
              },
              container.expiration
            )
        );
    }

    const deduped = [];
    const seen = new Set();

    for (const item of contracts) {
      const key =
        [
          item.id,
          item.expiration,
          item.strike,
          item.type,
        ].join("|");

      if (seen.has(key)) continue;
      seen.add(key);
      deduped.push(item);
    }

    const expirations =
      Array.from(
        new Set(
          deduped
            .map(
              item =>
                item.expiration
            )
            .filter(Boolean)
        )
      )
        .sort();

    return {
      available:
        deduped.length > 0 ||
        Object.keys(overview).length > 0,

      overview,
      contracts: deduped,
      expirations,
    };
  }

  function spreadPercent(contract) {
    if (
      contract.bid === null ||
      contract.ask === null ||
      contract.ask <= 0
    ) {
      return null;
    }

    const mid =
      (
        contract.bid +
        contract.ask
      ) / 2;

    if (mid <= 0) return null;

    return (
      (
        contract.ask -
        contract.bid
      ) /
      mid
    ) * 100;
  }

  function setText(id, value, fallback = "—") {
    const node = byId(id);
    if (!node) return;

    node.textContent =
      text(
        value,
        fallback
      );
  }

  function metric(label, value, note = null) {
    return `
      <div class="ob-symbol-metric">
        <span>${label}</span>
        <strong>${text(value)}</strong>
        ${note ? `<small>${note}</small>` : ""}
      </div>
    `;
  }

  function truthClass(projection) {
    if (projection.current_eligible) {
      return "current";
    }

    if (projection.display_eligible) {
      return "stale";
    }

    return "guarded";
  }

  function renderTruth(projection) {
    const chip =
      byId("symbolTruthChip");

    const cls =
      truthClass(projection);

    if (chip) {
      chip.className =
        "ob-symbol-chip ob-symbol-chip--" +
        cls;

      chip.textContent =
        projection.current_eligible
          ? "Live · source-backed"
          : (
              projection.display_eligible
                ? "Stale · context only"
                : "Current truth unavailable"
            );
    }

    setText(
      "symbolSource",
      projection.source,
      "Unavailable"
    );

    setText(
      "symbolAsOf",
      formatDate(
        projection.as_of
      ),
      "Unavailable"
    );

    setText(
      "symbolFreshness",
      projection.freshness,
      "Unavailable"
    );
  }

  function renderMode(mode) {
    const chip =
      byId("symbolModeChip");

    if (chip) {
      chip.textContent =
        mode.label +
        " · " +
        mode.verb;

      chip.dataset.mode =
        mode.key;
    }

    setText(
      "symbolModeTitle",
      mode.label +
      " · " +
      mode.verb
    );

    setText(
      "symbolModeMessage",
      (
        mode.authorization &&
        mode.authorization.locked &&
        mode.authorization.reason
      )
        ? (
            mode.authorization.reason +
            " Safe Symbol Room behavior remains restricted."
          )
        : mode.message
    );

    const safety =
      byId("symbolModeSafety");

    if (safety) {
      safety.textContent =
        mode.key === "manual_live_1"
          ? "OWNER DECISION REQUIRED · OWNER EXECUTES"
          : (
              mode.key === "hybrid"
                ? "YOU CHOOSE THE OPTION · OWNER EXECUTES"
                : (
                    mode.key === "automated"
                      ? "AUTOMATED LOCKED"
                      : "NO BROKER EXECUTION"
                  )
            );
    }

    const banner =
      byId("symbolModeBanner");

    if (banner) {
      banner.dataset.mode =
        mode.key;

      banner.dataset.locked =
        mode.locked ||
        (
          mode.authorization &&
          mode.authorization.locked
        )
          ? "true"
          : "false";
    }
  }

  function renderEvidence(
    projection,
    underlying,
    evidence,
    contract
  ) {
    let changed =
      underlying.why;

    if (!changed) {
      if (evidence.signals.length) {
        changed =
          "The canonical projection currently carries a signal record for " +
          underlying.symbol +
          ". Inspect the source-backed fields before deciding what deserves attention.";
      }

      else if (evidence.candidates.length) {
        changed =
          underlying.symbol +
          " is present in the canonical candidate evidence. Candidate status is context, not an order instruction.";
      }

      else if (evidence.positions.length) {
        changed =
          underlying.symbol +
          " appears in current position evidence. This room will not invent a new signal story around it.";
      }

      else if (evidence.watchlist.length) {
        changed =
          underlying.symbol +
          " is present on the canonical watchlist. Watch status alone is not an action instruction.";
      }

      else if (projection.display_eligible) {
        changed =
          "No source-backed signal, candidate, position, or watchlist change is currently attached to this symbol.";
      }

      else {
        changed =
          "Current canonical evidence is not display-eligible. Prior market stories are not carried forward.";
      }
    }

    setText(
      "symbolWhatChanged",
      changed
    );

    const flags = [];

    if (evidence.signals.length) {
      flags.push("Signal evidence");
    }

    if (evidence.candidates.length) {
      flags.push("Candidate evidence");
    }

    if (evidence.positions.length) {
      flags.push("Position evidence");
    }

    if (evidence.watchlist.length) {
      flags.push("Watchlist");
    }

    if (evidence.manualLive.length) {
      flags.push("Manual Live queue");
    }

    const mount =
      byId("symbolEvidenceFlags");

    if (mount) {
      mount.innerHTML =
        flags.length
          ? flags
              .map(
                item =>
                  `<span>${item}</span>`
              )
              .join("")
          : `<span>No active evidence flags</span>`;
    }

    const soulaana =
      safeObject(
        contract.soulaana_read
      );

    setText(
      "symbolSoulaanaSees",
      firstDefined(
        soulaana.summary,
        changed
      ),
      "No verified symbol interpretation is available."
    );

    setText(
      "symbolSoulaanaMeans",
      projection.current_eligible
        ? (
            "These fields are current enough to investigate. Investigation is still not permission to execute."
          )
        : (
            projection.display_eligible
              ? "This evidence can provide context, but it is not current enough to treat as live truth."
              : "The room does not have enough canonical truth to form a current market interpretation."
          )
    );

    setText(
      "symbolSoulaanaCaution",
      firstDefined(
        soulaana.caution,
        projection.reason,
        "Unknown fields stay unknown. A missing value is never silently treated as clear."
      )
    );

    setText(
      "symbolSoulaanaNext",
      firstDefined(
        soulaana.next,
        "Inspect the underlying and options evidence before deciding whether anything deserves to move forward."
      )
    );
  }

  function renderUnderlying(underlying) {
    setText(
      "symbolTicker",
      underlying.symbol,
      "—"
    );

    setText(
      "symbolCompany",
      underlying.company,
      "Company unavailable"
    );

    setText(
      "symbolSector",
      underlying.sector,
      "Constellation unavailable"
    );

    setText(
      "symbolMarketState",
      underlying.state,
      "State unavailable"
    );

    const metrics =
      byId("symbolUnderlyingMetrics");

    if (metrics) {
      metrics.innerHTML = [
        metric(
          "Price",
          formatMoney(
            underlying.price
          )
        ),

        metric(
          "Change",
          formatPercent(
            underlying.change
          )
        ),

        metric(
          "Volume",
          formatNumber(
            underlying.volume,
            0
          )
        ),

        metric(
          "Relative volume",
          formatNumber(
            underlying.relativeVolume
          )
        ),

        metric(
          "Day low",
          formatMoney(
            underlying.dayLow
          )
        ),

        metric(
          "Day high",
          formatMoney(
            underlying.dayHigh
          )
        ),

        metric(
          "Trend",
          underlying.trend
        ),

        metric(
          "Momentum",
          underlying.momentum
        ),

        metric(
          "Relative strength",
          underlying.relativeStrength
        ),

        metric(
          "Underlying IV",
          underlying.iv
        ),
      ].join("");
    }

    const facts =
      byId("symbolStarFacts");

    if (facts) {
      const items = [];

      if (underlying.role) {
        items.push(
          `<div><span>Market role</span><strong>${text(underlying.role)}</strong></div>`
        );
      }

      if (underlying.permission) {
        items.push(
          `<div><span>Permission</span><strong>${text(underlying.permission)}</strong></div>`
        );
      }

      if (underlying.risk) {
        items.push(
          `<div><span>Observed risk</span><strong>${text(underlying.risk)}</strong></div>`
        );
      }

      if (underlying.fact) {
        items.push(
          `<div class="ob-symbol-fun-fact"><span>Star fact ✦</span><strong>${text(underlying.fact)}</strong></div>`
        );
      }

      facts.innerHTML =
        items.length
          ? items.join("")
          : `
            <div>
              <span>Star facts</span>
              <strong>No source-backed star facts supplied.</strong>
            </div>
          `;
    }
  }

  function renderOptionsOverview(options) {
    const mount =
      byId("symbolOptionsOverview");

    const trust =
      byId("symbolOptionsTrust");

    if (!mount) return;

    if (!options.available) {
      mount.innerHTML = `
        <div class="ob-options-empty">
          <strong>Options feed unavailable in the canonical projection.</strong>
          <span>
            OBUX036–040 does not invent strikes, Greeks, volume,
            IV, or expirations when the canonical source has not supplied them.
          </span>
        </div>
      `;

      if (trust) {
        trust.textContent =
          "No canonical options chain";
      }

      return;
    }

    if (trust) {
      trust.textContent =
        "Source-backed options evidence";
    }

    const overview =
      safeObject(
        options.overview
      );

    const totalVolume =
      firstDefined(
        overview.volume,
        overview.total_volume
      );

    const totalOI =
      firstDefined(
        overview.open_interest,
        overview.total_open_interest,
        overview.oi
      );

    const iv =
      firstDefined(
        overview.iv,
        overview.implied_volatility
      );

    const putCall =
      firstDefined(
        overview.put_call_ratio,
        overview.putCallRatio
      );

    const liquidity =
      firstDefined(
        overview.liquidity,
        overview.liquidity_quality
      );

    mount.innerHTML = [
      metric(
        "Options volume",
        formatNumber(
          totalVolume,
          0
        )
      ),
      metric(
        "Open interest",
        formatNumber(
          totalOI,
          0
        )
      ),
      metric(
        "IV",
        iv
      ),
      metric(
        "Put / Call",
        putCall
      ),
      metric(
        "Liquidity",
        liquidity
      ),
      metric(
        "Contracts visible",
        options.contracts.length
      ),
    ].join("");
  }

  function renderExpirations(options) {
    const mount =
      byId("symbolExpirations");

    if (!mount) return;

    if (!options.expirations.length) {
      selectedExpiration = null;

      mount.innerHTML = `
        <span class="ob-options-empty-inline">
          No source-backed expiration set available.
        </span>
      `;

      return;
    }

    if (
      !selectedExpiration ||
      !options.expirations.includes(
        selectedExpiration
      )
    ) {
      selectedExpiration =
        options.expirations[0];
    }

    mount.innerHTML =
      options.expirations
        .map(
          expiry => `
            <button
              type="button"
              class="ob-expiration-button ${
                expiry === selectedExpiration
                  ? "is-active"
                  : ""
              }"
              data-expiration="${text(expiry)}"
            >
              ${text(expiry)}
            </button>
          `
        )
        .join("");

    mount
      .querySelectorAll(
        "[data-expiration]"
      )
      .forEach(
        button => {
          button.addEventListener(
            "click",
            () => {
              selectedExpiration =
                button.dataset.expiration;

              selectedContract = null;

              renderInteractiveOptions(
                latestState
              );
            }
          );
        }
      );
  }

  function contractsForSelectedExpiration(options) {
    if (!selectedExpiration) {
      return options.contracts;
    }

    return options.contracts
      .filter(
        item =>
          String(
            item.expiration || ""
          ) ===
          String(
            selectedExpiration
          )
      );
  }

  function contractLabel(contract) {
    const parts = [
      contract.symbol,
      contract.expiration,
      contract.strike !== null
        ? "$" + contract.strike
        : null,
      contract.type
        ? contract.type.toUpperCase()
        : null,
    ].filter(Boolean);

    return parts.join(" · ");
  }

  function renderChain(
    options,
    mode
  ) {
    const mount =
      byId("symbolChain");

    if (!mount) return;

    const contracts =
      contractsForSelectedExpiration(
        options
      );

    if (!contracts.length) {
      mount.innerHTML = `
        <div class="ob-options-empty">
          <strong>No source-backed contracts for this expiration.</strong>
        </div>
      `;
      return;
    }

    const sorted =
      [...contracts].sort(
        (a, b) => {
          const strikeA =
            a.strike === null
              ? Number.MAX_SAFE_INTEGER
              : a.strike;

          const strikeB =
            b.strike === null
              ? Number.MAX_SAFE_INTEGER
              : b.strike;

          if (strikeA !== strikeB) {
            return strikeA - strikeB;
          }

          return String(
            a.type || ""
          ).localeCompare(
            String(
              b.type || ""
            )
          );
        }
      );

    mount.innerHTML = `
      <div class="ob-chain-head">
        <span>Type</span>
        <span>Strike</span>
        <span>Bid</span>
        <span>Ask</span>
        <span>Volume</span>
        <span>OI</span>
        <span>IV</span>
        <span>Delta</span>
      </div>

      ${sorted
        .map(
          item => `
            <button
              class="ob-chain-row"
              type="button"
              data-contract-id="${text(item.id)}"
              aria-label="Inspect ${contractLabel(item)}"
            >
              <span>${text(item.type, "option").toUpperCase()}</span>
              <strong>${item.strike === null ? "—" : "$" + item.strike}</strong>
              <span>${formatMoney(item.bid)}</span>
              <span>${formatMoney(item.ask)}</span>
              <span>${formatNumber(item.volume, 0)}</span>
              <span>${formatNumber(item.openInterest, 0)}</span>
              <span>${item.iv === null ? "—" : formatNumber(item.iv)}</span>
              <span>${item.delta === null ? "—" : formatNumber(item.delta)}</span>
            </button>
          `
        )
        .join("")}
    `;

    mount
      .querySelectorAll(
        "[data-contract-id]"
      )
      .forEach(
        button => {
          button.addEventListener(
            "click",
            () => {
              const match =
                options.contracts.find(
                  item =>
                    String(item.id) ===
                    String(
                      button.dataset.contractId
                    )
                );

              if (!match) return;

              // Survey may inspect a contract, but it does not
              // create a selected trade object.
              selectedContract =
                mode.contract_selection
                  ? match
                  : null;

              renderContractDetail(
                match,
                mode,
                mode.contract_selection
              );

              renderActionBar(
                latestState
              );

              renderPaperPanel(
                latestState
              );
            }
          );
        }
      );
  }

  function renderContractDetail(
    contract,
    mode,
    selectable
  ) {
    const panel =
      byId("symbolContractPanel");

    const metrics =
      byId("symbolContractMetrics");

    const risk =
      byId("symbolContractRisk");

    if (
      !panel ||
      !metrics ||
      !risk
    ) {
      return;
    }

    panel.hidden = false;

    setText(
      "symbolContractTitle",
      contractLabel(contract),
      "Contract detail"
    );

    const spread =
      spreadPercent(contract);

    metrics.innerHTML = [
      metric(
        "Bid",
        formatMoney(
          contract.bid
        )
      ),
      metric(
        "Ask",
        formatMoney(
          contract.ask
        )
      ),
      metric(
        "Spread",
        spread === null
          ? "—"
          : spread.toFixed(2) + "%"
      ),
      metric(
        "Volume",
        formatNumber(
          contract.volume,
          0
        )
      ),
      metric(
        "Open interest",
        formatNumber(
          contract.openInterest,
          0
        )
      ),
      metric(
        "IV",
        contract.iv
      ),
      metric(
        "Delta",
        contract.delta
      ),
      metric(
        "Gamma",
        contract.gamma
      ),
      metric(
        "Theta",
        contract.theta
      ),
      metric(
        "Vega",
        contract.vega
      ),
      metric(
        "DTE",
        contract.dte
      ),
    ].join("");

    const notes = [];

    if (
      spread !== null &&
      spread > 10
    ) {
      notes.push(
        "Wide bid/ask spread may increase slippage."
      );
    }

    if (
      contract.openInterest !== null &&
      contract.openInterest === 0
    ) {
      notes.push(
        "Open interest is reported as zero."
      );
    }

    if (
      contract.theta !== null &&
      contract.theta < 0
    ) {
      notes.push(
        "Negative theta indicates time-decay exposure."
      );
    }

    if (!notes.length) {
      notes.push(
        "No additional risk conclusion is invented from missing fields."
      );
    }

    risk.innerHTML = `
      <strong>
        ${
          selectable
            ? "User-selectable in the current mode."
            : "Inspection only in the current mode."
        }
      </strong>

      ${notes
        .map(
          note =>
            `<span>${note}</span>`
        )
        .join("")}

      <span>
        OB is displaying contract facts. It is not declaring this
        contract suitable or preferred.
      </span>
    `;
  }

  function hybridFilterValues() {
    function field(id) {
      const node = byId(id);
      if (!node) return null;

      return number(node.value);
    }

    return {
      minOI:
        field(
          "symbolFilterOI"
        ),

      maxSpread:
        field(
          "symbolFilterSpread"
        ),

      minDelta:
        field(
          "symbolFilterDeltaMin"
        ),

      maxDelta:
        field(
          "symbolFilterDeltaMax"
        ),
    };
  }

  function filterMatches(
    contracts,
    filters
  ) {
    return contracts.filter(
      contract => {
        if (
          filters.minOI !== null &&
          contract.openInterest !== null &&
          contract.openInterest < filters.minOI
        ) {
          return false;
        }

        if (
          filters.maxSpread !== null
        ) {
          const spread =
            spreadPercent(
              contract
            );

          if (
            spread !== null &&
            spread > filters.maxSpread
          ) {
            return false;
          }
        }

        if (
          filters.minDelta !== null &&
          contract.delta !== null &&
          contract.delta < filters.minDelta
        ) {
          return false;
        }

        if (
          filters.maxDelta !== null &&
          contract.delta !== null &&
          contract.delta > filters.maxDelta
        ) {
          return false;
        }

        return true;
      }
    );
  }

  function renderHybridOptionSet(state) {
    const panel =
      byId("symbolHybridPanel");

    const mount =
      byId("symbolOptionSet");

    if (
      !panel ||
      !mount
    ) {
      return;
    }

    const mode =
      state.mode;

    panel.hidden =
      !mode.objective_option_set;

    if (!mode.objective_option_set) {
      mount.innerHTML = "";
      return;
    }

    if (!state.options.available) {
      mount.innerHTML = `
        <div class="ob-options-empty">
          No canonical options contracts are available to filter.
        </div>
      `;
      return;
    }

    const filters =
      hybridFilterValues();

    const available =
      contractsForSelectedExpiration(
        state.options
      );

    const matches =
      filterMatches(
        available,
        filters
      );

    mount.innerHTML = `
      <div class="ob-option-set-note">
        ${matches.length} contract(s) match the displayed filters.
        Order is not a recommendation ranking.
      </div>

      ${matches.length
        ? matches
            .map(
              item => `
                <button
                  class="ob-option-match"
                  type="button"
                  data-hybrid-contract-id="${text(item.id)}"
                >
                  <strong>${contractLabel(item)}</strong>
                  <span>
                    Surfaced because it matches the displayed objective filters.
                  </span>
                  <small>
                    OI ${formatNumber(item.openInterest, 0)}
                    · Spread ${
                      spreadPercent(item) === null
                        ? "—"
                        : spreadPercent(item).toFixed(2) + "%"
                    }
                    · Delta ${formatNumber(item.delta)}
                  </small>
                  <b>Inspect / choose</b>
                </button>
              `
            )
            .join("")
        : `
            <div class="ob-options-empty">
              No contracts match the displayed filters.
            </div>
          `}
    `;

    mount
      .querySelectorAll(
        "[data-hybrid-contract-id]"
      )
      .forEach(
        button => {
          button.addEventListener(
            "click",
            () => {
              const match =
                state.options.contracts.find(
                  item =>
                    String(item.id) ===
                    String(
                      button.dataset.hybridContractId
                    )
                );

              if (!match) return;

              // Critical Hybrid doctrine:
              // THE USER chooses the contract.
              selectedContract =
                match;

              renderContractDetail(
                match,
                mode,
                true
              );

              renderActionBar(
                latestState
              );
            }
          );
        }
      );
  }

  function renderPaperPanel(state) {
    const panel =
      byId("symbolPaperPanel");

    const summary =
      byId("symbolPaperSummary");

    if (
      !panel ||
      !summary
    ) {
      return;
    }

    panel.hidden =
      !state.mode.paper_build;

    if (!state.mode.paper_build) {
      return;
    }

    if (!selectedContract) {
      summary.textContent =
        "Select a contract to build a hypothetical paper idea.";
      return;
    }

    const quantity =
      number(
        byId("symbolPaperQuantity")?.value
      ) || 1;

    const entry =
      number(
        byId("symbolPaperEntry")?.value
      );

    const stop =
      number(
        byId("symbolPaperStop")?.value
      );

    const target =
      number(
        byId("symbolPaperTarget")?.value
      );

    summary.innerHTML = `
      <strong>PAPER · NO LIVE ORDER</strong>
      <span>${contractLabel(selectedContract)}</span>
      <span>Hypothetical quantity: ${quantity}</span>
      <span>Hypothetical entry: ${entry === null ? "not set" : formatMoney(entry)}</span>
      <span>Hypothetical stop: ${stop === null ? "not set" : formatMoney(stop)}</span>
      <span>Hypothetical target: ${target === null ? "not set" : formatMoney(target)}</span>
    `;
  }

  function renderRisk(state) {
    const mount =
      byId("symbolRiskGrid");

    if (!mount) return;

    const underlying =
      state.underlying;

    const mode =
      state.mode;

    const contract =
      selectedContract;

    const spread =
      contract
        ? spreadPercent(contract)
        : null;

    mount.innerHTML = [
      metric(
        "Observed symbol risk",
        underlying.risk
      ),

      metric(
        "Permission field",
        underlying.permission
      ),

      metric(
        "Options liquidity",
        contract
          ? (
              contract.openInterest === null
                ? "Unknown"
                : (
                    contract.openInterest > 0
                      ? "OI present"
                      : "OI zero"
                  )
            )
          : "Unknown"
      ),

      metric(
        "Selected spread",
        spread === null
          ? "Unknown"
          : spread.toFixed(2) + "%"
      ),

      metric(
        "Mode",
        mode.label
      ),

      metric(
        "Owner decision",
        mode.owner_decision_required
          ? "Required"
          : "No trade decision"
      ),

      metric(
        "Broker API",
        "Disabled"
      ),

      metric(
        "Broker execution",
        "Disabled"
      ),

      metric(
        "Automatic contract selection",
        "Disabled"
      ),

      metric(
        "Automatic execution",
        "Disabled"
      ),
    ].join("");

    setText(
      "symbolExecutionStatus",
      "Broker execution disabled"
    );
  }

  function paperPayload() {
    return {
      quantity:
        number(
          byId("symbolPaperQuantity")?.value
        ) || 1,

      entry:
        number(
          byId("symbolPaperEntry")?.value
        ),

      stop:
        number(
          byId("symbolPaperStop")?.value
        ),

      target:
        number(
          byId("symbolPaperTarget")?.value
        ),
    };
  }

  function buildHandoff(state) {
    const mode =
      state.mode;

    if (!mode.trade_handoff) {
      return null;
    }

    if (!selectedContract) {
      return null;
    }

    return {
      version:
        "OB_SYMBOL_ROOM_HANDOFF_V1",

      created_at:
        new Date().toISOString(),

      source_room:
        "symbol_room",

      destination_room:
        "trade_center",

      symbol:
        state.underlying.symbol,

      mode:
        mode.key,

      handoff_kind:
        mode.trade_handoff_kind,

      owner_decision_required:
        true,

      owner_selected_contract:
        true,

      ob_selected_contract:
        false,

      broker_api:
        false,

      brokerage_execution:
        false,

      automatic_execution:
        false,

      automatic_contract_selection:
        false,

      contract:
        {
          ...selectedContract,
          raw: undefined,
        },

      paper:
        mode.paper_build
          ? paperPayload()
          : null,

      provenance: {
        source:
          state.projection.source ||
          null,

        as_of:
          state.projection.as_of ||
          null,

        freshness:
          state.projection.freshness ||
          "unavailable",

        current_eligible:
          Boolean(
            state.projection.current_eligible
          ),

        display_eligible:
          Boolean(
            state.projection.display_eligible
          ),
      },
    };
  }

  function handoffToTradeCenter(state) {
    const packet =
      buildHandoff(state);

    if (!packet) {
      return;
    }

    sessionStorage.setItem(
      HANDOFF_KEY,
      JSON.stringify(packet)
    );

    const symbol =
      encodeURIComponent(
        packet.symbol
      );

    window.location.assign(
      "/ob/trade-center?symbol=" +
      symbol +
      "&from=symbol-room"
    );
  }

  function actionButton(
    label,
    action,
    extraClass = ""
  ) {
    return `
      <button
        type="button"
        class="ob-symbol-button ${extraClass}"
        data-symbol-action="${action}"
      >
        ${label}
      </button>
    `;
  }

  function renderActionBar(state) {
    const mount =
      byId("symbolActionBar");

    if (!mount) return;

    const mode =
      state.mode;

    const actions = [
      actionButton(
        "Return to Market Map",
        "market-map",
        "ob-symbol-button--quiet"
      ),
    ];

    if (mode.key === "survey") {
      actions.unshift(
        actionButton(
          "Inspect Options",
          "options"
        ),
        actionButton(
          "Compare Facts",
          "facts"
        )
      );

      setText(
        "symbolNextTitle",
        "Observe. Investigate. Nothing has to become a trade."
      );

      setText(
        "symbolNextMessage",
        "Survey keeps the room informational. Trade handoff is disabled."
      );
    }

    else if (mode.key === "paper") {
      actions.unshift(
        actionButton(
          "Build Paper Idea",
          "paper"
        )
      );

      if (selectedContract) {
        actions.unshift(
          actionButton(
            "Send Paper Idea to Trade Center",
            "trade-center"
          )
        );
      }

      setText(
        "symbolNextTitle",
        "Practice the idea."
      );

      setText(
        "symbolNextMessage",
        selectedContract
          ? "The selected contract can leave this room only as a paper-only packet."
          : "Choose a contract yourself before a paper-only Trade Center handoff is available."
      );
    }

    else if (mode.key === "manual_live_1") {
      actions.unshift(
        actionButton(
          "Review Signal Evidence",
          "evidence"
        ),
        actionButton(
          "Inspect Options",
          "options"
        )
      );

      if (selectedContract) {
        actions.unshift(
          actionButton(
            "Send My Selection to Trade Center",
            "trade-center"
          )
        );
      }

      setText(
        "symbolNextTitle",
        "OWNER DECISION REQUIRED"
      );

      setText(
        "symbolNextMessage",
        selectedContract
          ? "You selected this contract. Trade Center may prepare the review. You still execute at the brokerage."
          : "OB does not choose your contract in Manual Live 1. Inspect the chain and decide independently."
      );
    }

    else if (mode.key === "hybrid") {
      actions.unshift(
        actionButton(
          "Open Option Set",
          "hybrid"
        ),
        actionButton(
          "Compare Contracts",
          "options"
        )
      );

      if (selectedContract) {
        actions.unshift(
          actionButton(
            "Send My Choice to Trade Center",
            "trade-center"
          )
        );
      }

      setText(
        "symbolNextTitle",
        "YOU CHOOSE THE OPTION"
      );

      setText(
        "symbolNextMessage",
        selectedContract
          ? "Your selected filter match can move to Trade Center. OB has not selected it for you."
          : "Use objective filters, inspect the matches, and make the selection yourself."
      );
    }

    else {
      actions.unshift(
        actionButton(
          "Automated Locked",
          "locked",
          "ob-symbol-button--danger"
        )
      );

      setText(
        "symbolNextTitle",
        "Automated is locked."
      );

      setText(
        "symbolNextMessage",
        "No automated trade handoff or execution exists in this layer."
      );
    }

    mount.innerHTML =
      actions.join("");

    mount
      .querySelectorAll(
        "[data-symbol-action]"
      )
      .forEach(
        button => {
          button.addEventListener(
            "click",
            () => {
              const action =
                button.dataset.symbolAction;

              if (action === "market-map") {
                window.location.assign(
                  "/ob/market-map"
                );
                return;
              }

              if (action === "trade-center") {
                handoffToTradeCenter(
                  latestState
                );
                return;
              }

              if (action === "options") {
                document
                  .querySelector(
                    ".ob-options-sky"
                  )
                  ?.scrollIntoView(
                    {
                      behavior: "smooth",
                      block: "start",
                    }
                  );
                return;
              }

              if (action === "paper") {
                byId("symbolPaperPanel")
                  ?.scrollIntoView(
                    {
                      behavior: "smooth",
                      block: "start",
                    }
                  );
                return;
              }

              if (action === "hybrid") {
                byId("symbolHybridPanel")
                  ?.scrollIntoView(
                    {
                      behavior: "smooth",
                      block: "start",
                    }
                  );
                return;
              }

              if (action === "evidence") {
                byId("symbolEvidenceFlags")
                  ?.scrollIntoView(
                    {
                      behavior: "smooth",
                      block: "center",
                    }
                  );
                return;
              }

              if (action === "facts") {
                byId("symbolUnderlyingMetrics")
                  ?.scrollIntoView(
                    {
                      behavior: "smooth",
                      block: "center",
                    }
                  );
              }
            }
          );
        }
      );
  }

  function renderUnavailable(state) {
    const notice =
      byId("symbolUnavailableNotice");

    if (!notice) return;

    const unavailable =
      !state.projection.display_eligible ||
      (
        state.contract.symbol_header &&
        state.contract.symbol_header.unavailable
      );

    notice.hidden =
      !unavailable;

    if (!unavailable) {
      notice.textContent = "";
      return;
    }

    notice.innerHTML = `
      <strong>Current Symbol Room truth is limited.</strong>
      <span>
        ${
          text(
            state.projection.reason,
            "The canonical projection does not currently provide display-eligible symbol evidence."
          )
        }
      </span>
      <span>
        OB will not replace missing current data with the quarantined demo fixture.
      </span>
    `;
  }

  function renderInteractiveOptions(state) {
    renderExpirations(
      state.options
    );

    renderChain(
      state.options,
      state.mode
    );

    renderHybridOptionSet(
      state
    );
  }

  function render(state) {
    latestState = state;

    renderTruth(
      state.projection
    );

    renderMode(
      state.mode
    );

    renderUnavailable(
      state
    );

    renderUnderlying(
      state.underlying
    );

    renderEvidence(
      state.projection,
      state.underlying,
      state.evidence,
      state.contract
    );

    renderOptionsOverview(
      state.options
    );

    renderInteractiveOptions(
      state
    );

    renderPaperPanel(
      state
    );

    renderRisk(
      state
    );

    renderActionBar(
      state
    );
  }

  function readState() {
    const symbol =
      routeSymbol();

    const projection =
      canonicalProjection();

    const contract =
      symbolContract(
        symbol
      );

    const underlying =
      underlyingFrom(
        projection,
        contract,
        symbol
      );

    const evidence =
      sourceEvidence(
        projection,
        symbol
      );

    const options =
      normalizeOptions(
        projection,
        underlying
      );

    const mode =
      modeState();

    return {
      version: VERSION,
      symbol,
      projection,
      contract,
      underlying,
      evidence,
      options,
      mode,
      latestFeedEventAt,
    };
  }

  function refresh() {
    const next =
      readState();

    // Clear a selected contract if it disappeared
    // from the latest canonical options evidence.
    if (selectedContract) {
      const stillExists =
        next.options.contracts.some(
          item =>
            String(item.id) ===
            String(
              selectedContract.id
            )
        );

      if (!stillExists) {
        selectedContract = null;

        const panel =
          byId(
            "symbolContractPanel"
          );

        if (panel) {
          panel.hidden = true;
        }
      }
    }

    render(next);
  }

  function wireStaticControls() {
    byId("symbolClearContract")
      ?.addEventListener(
        "click",
        () => {
          selectedContract = null;

          const panel =
            byId(
              "symbolContractPanel"
            );

          if (panel) {
            panel.hidden = true;
          }

          if (latestState) {
            renderPaperPanel(
              latestState
            );

            renderRisk(
              latestState
            );

            renderActionBar(
              latestState
            );
          }
        }
      );

    byId("symbolApplyHybridFilters")
      ?.addEventListener(
        "click",
        () => {
          if (latestState) {
            renderHybridOptionSet(
              latestState
            );
          }
        }
      );

    [
      "symbolPaperQuantity",
      "symbolPaperEntry",
      "symbolPaperStop",
      "symbolPaperTarget",
    ].forEach(
      id => {
        byId(id)
          ?.addEventListener(
            "input",
            () => {
              if (latestState) {
                renderPaperPanel(
                  latestState
                );
              }
            }
          );
      }
    );
  }

  function boot() {
    wireStaticControls();
    refresh();

    window.addEventListener(
      "obEngineFeedAdapterUpdated",
      event => {
        latestFeedEventAt =
          new Date().toISOString();

        refresh();
      }
    );

    window.addEventListener(
      "obAccountExperienceUpdated",
      () => {
        refresh();
      }
    );

    window.addEventListener(
      "obAuthorizedModeChanged",
      () => {
        selectedContract = null;
        refresh();
      }
    );
  }

  window.OB_SYMBOL_ROOM_OBUX036_040 = Object.freeze({
    VERSION,
    HANDOFF_KEY,
    readState,
    refresh,
    normalizeOptions,
    spreadPercent,
    buildHandoff,
  });

  if (
    document.readyState === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot
    );
  } else {
    boot();
  }
})();
