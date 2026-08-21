(function () {
  "use strict";

  const MODE_API = window.OBTradeCenterModes;

  if (!MODE_API) {
    console.error("OB Trade Center mode contract unavailable.");
    return;
  }

  const state = {
    mode: MODE_API.resolveMode(),
    projection: {},
    positions: [],
    candidates: [],
    activeTrade: null,
    rankedContracts: [],
    selectedContract: null,
  };

  const LIFE = [
    "research",
    "contract",
    "preflight",
    "entry",
    "manage",
    "exit",
    "review",
  ];

  const LIFE_MAP = Object.freeze({
    new: "research",
    research: "research",
    research_approved: "contract",
    execution_blocked: "preflight",
    execution_ready: "preflight",
    ready: "preflight",
    selected: "entry",
    entered: "manage",
    managing: "manage",
    exit_ready: "exit",
    closed: "review",
  });


  function el(id) {
    return document.getElementById(id);
  }


  function obj(value) {
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


  function arr(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function first(...values) {
    for (const value of values) {
      if (
        value !== undefined
        &&
        value !== null
        &&
        value !== ""
      ) {
        return value;
      }
    }

    return null;
  }


  function num(value) {
    const parsed = Number(value);

    return Number.isFinite(parsed)
      ? parsed
      : null;
  }


  function txt(value, fallback = "—") {
    const found = first(value);

    return found === null
      ? fallback
      : String(found);
  }


  function money(value) {
    const parsed = num(value);

    if (parsed === null) {
      return "—";
    }

    return new Intl.NumberFormat(
      "en-US",
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
      }
    ).format(parsed);
  }


  function pct(value) {
    const parsed = num(value);

    if (parsed === null) {
      return "—";
    }

    const normalized =
      Math.abs(parsed) <= 1
        ? parsed * 100
        : parsed;

    return `${normalized.toFixed(1)}%`;
  }


  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }


  function symbolOf(value) {
    const safe = obj(value);

    return txt(
      first(
        safe.symbol,
        safe.underlying,
        safe.underlying_symbol,
        safe.ticker
      ),
      ""
    ).toUpperCase();
  }


  function contractSymbolOf(value) {
    const safe = obj(value);

    return txt(
      first(
        safe.contract_symbol,
        safe.contractSymbol,
        safe.option_symbol
      ),
      ""
    );
  }


  function normalizeRight(value) {
    const raw = txt(value, "")
      .trim()
      .toUpperCase();

    if (
      raw === "C"
      ||
      raw === "CALL"
    ) {
      return "CALL";
    }

    if (
      raw === "P"
      ||
      raw === "PUT"
    ) {
      return "PUT";
    }

    return raw || "OPTION";
  }


  function contractIdentity(value) {
    const safe = obj(value);

    const strike = first(
      safe.strike,
      safe.strike_price
    );

    const expiry = first(
      safe.expiration,
      safe.expiry,
      safe.expiration_date
    );

    const right = normalizeRight(
      first(
        safe.right,
        safe.option_type,
        safe.type
      )
    );

    const pieces = [];

    if (strike !== null) {
      pieces.push(money(strike));
    }

    pieces.push(right);

    if (expiry !== null) {
      pieces.push(txt(expiry));
    }

    return pieces.join(" · ");
  }


  // ================================================================================================
  // CANONICAL PROJECTION
  // ================================================================================================

  function resolveProjection() {
    const candidates = [
      window.OB_CANONICAL_MARKET_PROJECTION,
      window.OB_MARKET_PROJECTION,
      window.OB_ENGINE_PROJECTION,
      window.OBMarketProjection,
      window.obMarketProjection,
    ];

    for (const candidate of candidates) {
      if (
        candidate
        &&
        typeof candidate === "object"
      ) {
        return candidate;
      }
    }

    return {};
  }


  function contractsForSymbol(projection, symbol) {
    const safe = obj(projection);
    const normalized = txt(symbol, "").toUpperCase();

    const rows = [];

    const maps = [
      obj(safe.options_by_symbol),
      obj(safe.option_chains),
      obj(safe.options_chains),
    ];

    for (const map of maps) {
      for (
        const [key, value]
        of Object.entries(map)
      ) {
        if (
          String(key).toUpperCase()
          !== normalized
        ) {
          continue;
        }

        if (Array.isArray(value)) {
          rows.push(...value);
        } else {
          const nested = obj(value);

          rows.push(
            ...arr(nested.contracts),
            ...arr(nested.options),
            ...arr(nested.calls),
            ...arr(nested.puts)
          );
        }
      }
    }

    const global = [
      ...arr(safe.ranked_contracts),
      ...arr(safe.research_contracts),
      ...arr(safe.options),
    ];

    rows.push(
      ...global.filter(
        contract =>
          !symbolOf(contract)
          ||
          symbolOf(contract) === normalized
      )
    );

    const seen = new Set();

    return rows.filter(
      contract => {
        const key =
          contractSymbolOf(contract)
          ||
          JSON.stringify([
            symbolOf(contract),
            first(contract.strike),
            first(
              contract.expiration,
              contract.expiry
            ),
            first(
              contract.right,
              contract.option_type
            ),
          ]);

        if (seen.has(key)) {
          return false;
        }

        seen.add(key);
        return true;
      }
    );
  }


  function extractArray(projection, keys) {
    const safe = obj(projection);

    for (const key of keys) {
      const value = safe[key];

      if (Array.isArray(value)) {
        return value;
      }
    }

    const tradeCenter = obj(
      safe.trade_center
    );

    for (const key of keys) {
      const value = tradeCenter[key];

      if (Array.isArray(value)) {
        return value;
      }
    }

    return [];
  }


  // ================================================================================================
  // HANDOFF
  // ================================================================================================

  function handoff() {
    const query = new URLSearchParams(
      window.location.search
    );

    return {
      symbol: txt(
        first(
          query.get("symbol"),
          query.get("ticker"),
          sessionStorage.getItem(
            "ob_trade_symbol"
          ),
          sessionStorage.getItem(
            "ob_symbol"
          )
        ),
        ""
      ).toUpperCase(),

      contractSymbol: txt(
        first(
          query.get("contract"),
          query.get("contract_symbol"),
          sessionStorage.getItem(
            "ob_trade_contract"
          )
        ),
        ""
      ),
    };
  }


  function initialWorkspace() {
    const incoming = handoff();

    const ranked =
      incoming.symbol
        ? contractsForSymbol(
            state.projection,
            incoming.symbol
          )
        : [];

    let selected = null;

    if (incoming.contractSymbol) {
      selected =
        ranked.find(
          contract =>
            contractSymbolOf(contract)
            === incoming.contractSymbol
        )
        || null;
    }

    // HARD AUTHORITY BOUNDARY:
    //
    // Ranked #1 is NOT silently promoted to selectedContract.
    // Manual Live 1 and Hybrid retain human selection authority.

    return {
      symbol: incoming.symbol,
      selected,
      ranked,
    };
  }


  // ================================================================================================
  // LIFECYCLE
  // ================================================================================================

  function lifecycle(value) {
    const safe = obj(value);

    const raw = txt(
      first(
        safe.lifecycle_state,
        safe.lifecycle,
        safe.stage,
        safe.status
      ),
      "research"
    )
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, "_");

    return LIFE_MAP[raw] || "research";
  }


  function renderLifecycle() {
    const current = lifecycle(
      state.activeTrade
    );

    const currentIndex = Math.max(
      0,
      LIFE.indexOf(current)
    );

    document
      .querySelectorAll(
        "#obtc-lifecycle-rail [data-stage]"
      )
      .forEach(
        node => {
          const index = LIFE.indexOf(
            node.dataset.stage
          );

          node.classList.toggle(
            "is-complete",
            index < currentIndex
          );

          node.classList.toggle(
            "is-current",
            index === currentIndex
          );
        }
      );

    el("obtc-lifecycle-chip").textContent =
      current.toUpperCase();
  }


  // ================================================================================================
  // ATTENTION RAIL
  // ================================================================================================

  function attentionCard(item) {
    const safe = obj(item);

    const button =
      document.createElement("button");

    button.type = "button";
    button.className =
      "obtc-attention-card";

    const symbol =
      symbolOf(safe)
      || "TRADE";

    const embedded = obj(
      first(
        safe.selected_contract,
        safe.contract,
        safe.option
      )
    );

    button.innerHTML = `
      <strong>${escapeHtml(symbol)}</strong>
      <small>${escapeHtml(
        txt(
          first(
            safe.lifecycle_state,
            safe.status,
            "Review"
          )
        )
      )}</small>
      <small>${escapeHtml(
        contractIdentity(embedded)
        || "Open workspace"
      )}</small>
    `;

    button.addEventListener(
      "click",
      () => {
        state.activeTrade = safe;

        state.selectedContract =
          Object.keys(embedded).length
            ? embedded
            : null;

        state.rankedContracts =
          contractsForSymbol(
            state.projection,
            symbol
          );

        renderWorkspace();
      }
    );

    return button;
  }


  function renderAttention() {
    const positionMount =
      el("obtc-active-positions");

    const queueMount =
      el("obtc-decision-queue");

    positionMount.innerHTML = "";
    queueMount.innerHTML = "";

    if (!state.positions.length) {
      positionMount.innerHTML =
        '<div class="obtc-empty">No active positions.</div>';
    } else {
      state.positions
        .slice(0, 5)
        .forEach(
          position =>
            positionMount.appendChild(
              attentionCard(position)
            )
        );
    }

    if (!state.candidates.length) {
      queueMount.innerHTML =
        '<div class="obtc-empty">Nothing waiting.</div>';
    } else {
      state.candidates
        .slice(0, 5)
        .forEach(
          candidate =>
            queueMount.appendChild(
              attentionCard(candidate)
            )
        );
    }

    el("obtc-position-count").textContent =
      String(state.positions.length);

    el("obtc-decision-count").textContent =
      String(state.candidates.length);
  }


  // ================================================================================================
  // CONTRACT
  // ================================================================================================

  function contractMetrics(value) {
    const safe = obj(value);

    const bid = first(safe.bid);
    const ask = first(safe.ask);

    return {
      title:
        contractIdentity(safe)
        ||
        contractSymbolOf(safe)
        ||
        "No contract selected",

      subtitle:
        contractSymbolOf(safe)
        ||
        "Contract intelligence",

      premium:
        money(
          first(
            safe.mark,
            safe.last,
            safe.premium
          )
        ),

      bidAsk:
        bid !== null || ask !== null
          ? `${money(bid)} / ${money(ask)}`
          : "—",

      iv:
        pct(
          first(
            safe.implied_volatility,
            safe.iv
          )
        ),

      delta:
        txt(
          first(
            safe.delta,
            obj(safe.greeks).delta
          )
        ),

      liquidity:
        txt(
          first(
            safe.quote_quality,
            safe.execution_reason,
            safe.liquidity
          )
        ),

      rank:
        txt(
          first(
            safe.rank,
            safe.contract_rank,
            safe.contract_score,
            safe.score
          )
        ),

      source:
        txt(
          first(
            safe.source,
            safe.data_source,
            safe.authority
          )
        ),
    };
  }


  function renderContract() {
    const metrics =
      contractMetrics(
        state.selectedContract
      );

    el("obtc-contract-title").textContent =
      metrics.title;

    el("obtc-contract-subtitle").textContent =
      metrics.subtitle;

    el("obtc-premium").textContent =
      metrics.premium;

    el("obtc-bid-ask").textContent =
      metrics.bidAsk;

    el("obtc-iv").textContent =
      metrics.iv;

    el("obtc-delta").textContent =
      metrics.delta;

    el("obtc-liquidity").textContent =
      metrics.liquidity;

    el("obtc-rank").textContent =
      metrics.rank;

    el("obtc-contract-source").textContent =
      `Source ${metrics.source}`;
  }


  function renderRankedOptions() {
    const wrap =
      el("obtc-ranked-options");

    const list =
      el("obtc-ranked-option-list");

    list.innerHTML = "";

    const show =
      (
        state.mode.id
        === MODE_API.MODE_HYBRID
      )
      &&
      state.rankedContracts.length > 0;

    wrap.hidden = !show;

    if (!show) {
      return;
    }

    state.rankedContracts
      .slice(0, 5)
      .forEach(
        (contract, index) => {
          const metrics =
            contractMetrics(contract);

          const button =
            document.createElement("button");

          button.type = "button";
          button.className =
            "obtc-option-choice";

          button.setAttribute(
            "aria-pressed",
            state.selectedContract === contract
              ? "true"
              : "false"
          );

          button.innerHTML = `
            <span>
              <strong>${escapeHtml(metrics.title)}</strong>
              <small>
                ${escapeHtml(metrics.premium)}
                · ${escapeHtml(metrics.bidAsk)}
                · IV ${escapeHtml(metrics.iv)}
              </small>
            </span>
            <strong>
              ${index === 0 ? "TOP RANKED" : `#${index + 1}`}
            </strong>
          `;

          button.addEventListener(
            "click",
            () => {
              // USER action establishes selection.
              state.selectedContract =
                contract;

              renderWorkspace();
            }
          );

          list.appendChild(button);
        }
      );
  }


  // ================================================================================================
  // FLIGHT PLAN
  // ================================================================================================

  function renderPlan() {
    const trade = obj(
      state.activeTrade
    );

    el("obtc-entry").textContent =
      money(
        first(
          trade.planned_entry,
          trade.entry,
          trade.entry_price
        )
      );

    el("obtc-stop").textContent =
      money(
        first(
          trade.stop,
          trade.stop_price,
          trade.planned_stop
        )
      );

    el("obtc-target").textContent =
      money(
        first(
          trade.target,
          trade.target_price,
          trade.planned_target
        )
      );

    el("obtc-max-risk").textContent =
      money(
        first(
          trade.max_risk,
          trade.risk_amount,
          trade.capital_at_risk
        )
      );

    el("obtc-hold-window").textContent =
      txt(
        first(
          trade.expected_hold,
          trade.hold_window,
          trade.expected_hold_window
        )
      );
  }


  function renderEvidence() {
    const trade = obj(
      state.activeTrade
    );

    const mount =
      el("obtc-evidence");

    const raw = first(
      trade.evidence,
      trade.reasons,
      trade.setup_evidence,
      trade.contract_notes
    );

    let values = [];

    if (Array.isArray(raw)) {
      values =
        raw
          .map(value => txt(value, ""))
          .filter(Boolean);
    }

    else if (
      raw
      &&
      typeof raw === "object"
    ) {
      values =
        Object
          .entries(raw)
          .filter(
            ([, value]) => Boolean(value)
          )
          .map(
            ([key]) =>
              key.replaceAll("_", " ")
          );
    }

    if (!values.length) {
      mount.innerHTML =
        '<span class="obtc-muted">No canonical evidence supplied.</span>';

      return;
    }

    mount.innerHTML = "";

    values
      .slice(0, 8)
      .forEach(
        value => {
          const pill =
            document.createElement("span");

          pill.className =
            "obtc-evidence-pill";

          pill.textContent = value;

          mount.appendChild(pill);
        }
      );
  }


  // ================================================================================================
  // POSITION HEALTH
  // ================================================================================================

  function renderHealth() {
    const trade =
      obj(state.activeTrade);

    const panel =
      el("obtc-position-health");

    const stage =
      lifecycle(trade);

    if (
      !["manage", "exit"].includes(stage)
    ) {
      panel.hidden = true;
      return;
    }

    panel.hidden = false;

    el("obtc-health-state").textContent =
      txt(
        first(
          trade.health_state,
          trade.position_health,
          "Monitoring"
        )
      );

    el("obtc-return").textContent =
      pct(
        first(
          trade.return_pct,
          trade.pnl_pct,
          trade.percent_return
        )
      );

    el("obtc-current-premium").textContent =
      money(
        first(
          trade.current_premium,
          trade.mark,
          trade.current_price
        )
      );

    el("obtc-time-in-trade").textContent =
      txt(
        first(
          trade.time_in_trade,
          trade.hold_duration
        )
      );

    el("obtc-thesis-health").textContent =
      txt(
        first(
          trade.thesis_health,
          trade.thesis_state
        )
      );

    el("obtc-contract-health").textContent =
      txt(
        first(
          trade.contract_health,
          trade.quote_quality
        )
      );
  }


  // ================================================================================================
  // ACTIONS
  // ================================================================================================

  function dispatch(name, extra = {}) {
    window.dispatchEvent(
      new CustomEvent(
        name,
        {
          detail: {
            mode:
              state.mode.id,

            trade:
              state.activeTrade,

            contract:
              state.selectedContract,

            ...extra,
          },
        }
      )
    );
  }


  function button(
    label,
    {
      primary = false,
      danger = false,
      disabled = false,
      onClick = null,
    } = {}
  ) {
    const node =
      document.createElement("button");

    node.type = "button";

    node.className =
      "obtc-action"
      + (primary ? " obtc-action--primary" : "")
      + (danger ? " obtc-action--danger" : "");

    node.textContent = label;
    node.disabled = disabled;

    if (onClick) {
      node.addEventListener(
        "click",
        onClick
      );
    }

    return node;
  }


  function renderActions() {
    const mount =
      el("obtc-actions");

    mount.innerHTML = "";

    el("obtc-mode-eyebrow").textContent =
      state.mode.eyebrow;

    el("obtc-mode-title").textContent =
      state.mode.copy.title;

    el("obtc-mode-instruction").textContent =
      state.mode.copy.instruction;

    if (state.mode.locked) {
      mount.appendChild(
        button(
          "Automated mode locked",
          {
            disabled: true,
          }
        )
      );

      return;
    }

    mount.appendChild(
      button(
        "Watch",
        {
          onClick: () =>
            dispatch(
              "ob:trade-center:watch"
            ),
        }
      )
    );

    mount.appendChild(
      button(
        "Compare contracts",
        {
          onClick: () =>
            dispatch(
              "ob:trade-center:compare"
            ),
        }
      )
    );

    if (
      state.mode.id
      === MODE_API.MODE_SURVEY
    ) {
      return;
    }

    if (
      state.mode.id
      === MODE_API.MODE_MANUAL_LIVE_1
      &&
      !state.selectedContract
    ) {
      mount.appendChild(
        button(
          "Choose contract in Symbol Room",
          {
            primary: true,
            onClick: openSymbol,
          }
        )
      );

      return;
    }

    if (
      state.mode.id
      === MODE_API.MODE_HYBRID
      &&
      !state.selectedContract
    ) {
      mount.appendChild(
        button(
          "Select a contract above",
          {
            primary: true,
            disabled: true,
          }
        )
      );

      return;
    }

    mount.appendChild(
      button(
        state.mode.id
        === MODE_API.MODE_PAPER
          ? "Begin paper preflight"
          : "Begin preflight",

        {
          primary: true,

          onClick: () =>
            dispatch(
              "ob:trade-center:begin-preflight"
            ),
        }
      )
    );

    if (
      state.mode.id
      === MODE_API.MODE_MANUAL_LIVE_1
    ) {
      mount.appendChild(
        button(
          "I placed it",
          {
            onClick: () =>
              dispatch(
                "ob:trade-center:owner-placed"
              ),
          }
        )
      );

      mount.appendChild(
        button(
          "I did not place it",
          {
            danger: true,

            onClick: () =>
              dispatch(
                "ob:trade-center:not-placed"
              ),
          }
        )
      );
    }
  }


  // ================================================================================================
  // SOULAANA
  // ================================================================================================

  function soulaanaLine() {
    if (!state.activeTrade) {
      return "Select a trade and I’ll explain what matters.";
    }

    const stage =
      lifecycle(state.activeTrade);

    if (stage === "manage") {
      return "This position is active. I’m watching its plan, timing, and contract health.";
    }

    if (stage === "exit") {
      return "This trade has reached an exit decision point.";
    }

    if (
      state.mode.id
      === MODE_API.MODE_MANUAL_LIVE_1
    ) {
      return "You remain the contract and execution authority.";
    }

    if (
      state.mode.id
      === MODE_API.MODE_HYBRID
    ) {
      return "I can narrow the option set. You choose the contract.";
    }

    return "I can explain the setup, contract, risk, and next step.";
  }


  function renderSoulaana() {
    const summary =
      soulaanaLine();

    el("obtc-soulaana-line").textContent =
      summary;

    const symbol =
      symbolOf(state.activeTrade)
      ||
      handoff().symbol
      ||
      "This trade";

    el("obtc-soulaana-detail").textContent =
      `${symbol}: ${summary} ${state.mode.copy.instruction}`;
  }


  function bindSoulaana() {
    const orb =
      el("obtc-soulaana-orb");

    const drawer =
      el("obtc-soulaana-drawer");

    const close =
      el("obtc-close-soulaana");

    orb.addEventListener(
      "click",
      () => {
        drawer.hidden = false;

        orb.setAttribute(
          "aria-expanded",
          "true"
        );
      }
    );

    close.addEventListener(
      "click",
      () => {
        drawer.hidden = true;

        orb.setAttribute(
          "aria-expanded",
          "false"
        );
      }
    );
  }


  // ================================================================================================
  // WORKSPACE
  // ================================================================================================

  function openSymbol() {
    const symbol =
      symbolOf(state.activeTrade)
      ||
      handoff().symbol;

    if (!symbol) {
      return;
    }

    dispatch(
      "ob:trade-center:open-symbol",
      { symbol }
    );

    window.location.assign(
      `/ob/symbol/${encodeURIComponent(symbol)}`
    );
  }


  function renderWorkspace() {
    const trade =
      obj(state.activeTrade);

    const symbol =
      symbolOf(trade)
      ||
      handoff().symbol
      ||
      "";

    el("obtc-symbol").textContent =
      symbol || "Select a trade";

    el("obtc-thesis").textContent =
      txt(
        first(
          trade.thesis,
          trade.setup,
          trade.reason,
          symbol
            ? "Review the canonical trade evidence and contract."
            : null
        ),
        "Choose a position or decision to open its operating workspace."
      );

    el("obtc-open-symbol").disabled =
      !symbol;

    renderLifecycle();
    renderContract();
    renderRankedOptions();
    renderPlan();
    renderEvidence();
    renderHealth();
    renderActions();
    renderSoulaana();
  }


  function renderChrome() {
    el("obtc-mode-chip").textContent =
      state.mode.label;

    el("obtc-room-summary").textContent =
      `${state.positions.length} active position`
      + (
        state.positions.length === 1
          ? ""
          : "s"
      )
      + ` · ${state.candidates.length} decision`
      + (
        state.candidates.length === 1
          ? ""
          : "s"
      )
      + " waiting";
  }


  // ================================================================================================
  // INIT
  // ================================================================================================

  function init() {
    state.projection =
      resolveProjection();

    state.positions =
      extractArray(
        state.projection,
        [
          "active_positions",
          "positions",
          "open_positions",
        ]
      );

    state.candidates =
      extractArray(
        state.projection,
        [
          "trade_candidates",
          "candidates",
          "opportunities",
        ]
      );

    const incoming =
      initialWorkspace();

    state.rankedContracts =
      incoming.ranked;

    state.selectedContract =
      incoming.selected;

    if (incoming.symbol) {
      state.activeTrade = {
        symbol:
          incoming.symbol,

        lifecycle_state:
          incoming.selected
            ? "selected"
            : "research",
      };
    }

    else if (state.positions.length) {
      state.activeTrade =
        state.positions[0];

      const embedded =
        obj(
          first(
            state.activeTrade.selected_contract,
            state.activeTrade.contract,
            state.activeTrade.option
          )
        );

      state.selectedContract =
        Object.keys(embedded).length
          ? embedded
          : null;

      state.rankedContracts =
        contractsForSymbol(
          state.projection,
          symbolOf(state.activeTrade)
        );
    }

    else if (state.candidates.length) {
      state.activeTrade =
        state.candidates[0];

      state.rankedContracts =
        contractsForSymbol(
          state.projection,
          symbolOf(state.activeTrade)
        );
    }

    renderAttention();
    renderChrome();
    renderWorkspace();
    bindSoulaana();

    el("obtc-open-symbol")
      .addEventListener(
        "click",
        openSymbol
      );

    window.OBTradeCenter =
      Object.freeze({
        getState() {
          return {
            mode:
              state.mode.id,

            activeTrade:
              state.activeTrade,

            selectedContract:
              state.selectedContract,

            rankedContracts:
              [...state.rankedContracts],
          };
        },

        setMode(value) {
          state.mode =
            MODE_API.getMode(value);

          renderChrome();
          renderWorkspace();
        },

        refresh() {
          state.projection =
            resolveProjection();

          renderWorkspace();
        },
      });

    window.dispatchEvent(
      new CustomEvent(
        "ob:trade-center:ready",
        {
          detail: {
            mode:
              state.mode.id,

            broker_execution:
              false,

            automatic_execution:
              false,
          },
        }
      )
    );
  }


  if (
    document.readyState
    === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      init,
      { once: true }
    );
  }

  else {
    init();
  }
})();
