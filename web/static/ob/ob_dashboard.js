// OBUX006-OBUX010 SOULAANA_EXPLANATION_FIRST_DASHBOARD

(function () {
  "use strict";

  const VERSION = "OBUX006-OBUX010";

  const SNAPSHOT_KEY = "obux_dashboard_since_you_were_here_v1";


  // ================================================================================================
  // SAFE HELPERS
  // ================================================================================================

  function safeText(value, fallback = "") {
    if (value === null || value === undefined) return fallback;

    const text = String(value).trim();

    return text || fallback;
  }


  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }


  function safeObject(value) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    )
      ? value
      : {};
  }


  function escapeHTML(value) {
    return safeText(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }


  function compact(value, fallback = "") {
    return escapeHTML(
      safeText(
        value,
        fallback
      )
    );
  }


  function numberValue(value) {
    if (
      value === null
      || value === undefined
      || value === ""
    ) {
      return null;
    }

    if (
      typeof value === "number"
      && Number.isFinite(value)
    ) {
      return value;
    }

    const cleaned = String(value)
      .replace(/\$/g, "")
      .replace(/,/g, "")
      .replace(/%/g, "")
      .trim();

    const result = Number(cleaned);

    return Number.isFinite(result)
      ? result
      : null;
  }


  function formatMoney(value) {
    const number = numberValue(value);

    if (number === null) {
      return "Not reported";
    }

    return new Intl.NumberFormat(
      "en-US",
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2
      }
    ).format(number);
  }


  function formatPercent(value) {
    let number = numberValue(value);

    if (number === null) {
      return "Not reported";
    }

    if (
      number >= 0
      && number <= 1
    ) {
      number *= 100;
    }

    return `${Math.round(number)}%`;
  }


  // ================================================================================================
  // EXISTING DATA LAYERS
  // ================================================================================================

  function obDashboardContract() {
    try {
      if (
        window.OB_DATA_CONTRACTS_V22
        && typeof window.OB_DATA_CONTRACTS_V22.dashboardContract === "function"
      ) {
        const result = window.OB_DATA_CONTRACTS_V22.dashboardContract();

        if (
          result
          && typeof result === "object"
        ) {
          return {
            payload: result,
            source: "dashboard_contract",
            trustworthyForPositions: true
          };
        }
      }
    } catch (error) {
      console.warn(
        "[OBUX_DASHBOARD_CONTRACT]",
        error
      );
    }

    return {
      payload: {},
      source: "contract_unavailable",
      trustworthyForPositions: false
    };
  }


  function obDashboardEngineFeed() {
    const candidates = [
      window.OB_ENGINE_FEED_ADAPTER_V25,
      window.OB_ENGINE_FEED_ADAPTER,
      window.OB_ENGINE_FEED,
      window.OB_SAFE_ENGINE_FEED_ADAPTER
    ];

    for (const candidate of candidates) {
      if (
        candidate
        && typeof candidate === "object"
      ) {
        return candidate;
      }
    }

    return {};
  }


  function obDashboardSymbols() {
    const sectors = (
      window.OB_MARKET_DATA
      && Array.isArray(window.OB_MARKET_DATA.sectors)
    )
      ? window.OB_MARKET_DATA.sectors
      : [];

    const rows = [];

    sectors.forEach((sector) => {
      safeArray(sector.symbols).forEach((symbolObj) => {
        rows.push({
          ...symbolObj,
          sectorName: sector.name,
          constellationName: sector.constellationName,
          sectorStrength: sector.strength,

          // VERY IMPORTANT:
          // This source is WATCH/FALLBACK CONTEXT ONLY.
          __obux_source: "static_market_fallback",
          __obux_actionable: false,
          __obux_confirmed_position: false
        });
      });
    });

    return rows;
  }


  // ================================================================================================
  // POSITION SOURCE
  // ================================================================================================

  function obDashboardOpenPositions() {
    const contractState = obDashboardContract();

    const contract = safeObject(
      contractState.payload
    );

    const engine = safeObject(
      obDashboardEngineFeed()
    );

    const enginePayload = safeObject(
      engine.payload
      || engine.data
      || engine.snapshot
      || engine
    );


    const candidateSources = [
      {
        rows: contract.open_positions_preview,
        source: "dashboard_contract"
      },
      {
        rows: contract.open_positions,
        source: "dashboard_contract"
      },
      {
        rows: enginePayload.positions_preview,
        source: "engine_feed"
      },
      {
        rows: enginePayload.open_positions,
        source: "engine_feed"
      }
    ];


    for (const source of candidateSources) {
      const rows = safeArray(
        source.rows
      );

      if (!rows.length) {
        continue;
      }

      return rows
        .slice(0, 5)
        .map((row) => ({
          ...safeObject(row),
          __obux_source: source.source,
          __obux_confirmed_position: true
        }));
    }


    // ABSOLUTELY NO static-symbol fallback here.
    //
    // The previous Dashboard treated MU/AMD/INTC as open positions
    // merely because of symbol names. OBUX removes that behavior.
    return [];
  }


  // ================================================================================================
  // CANDIDATE / HOT-NOW SOURCE
  // ================================================================================================

  function obDashboardContractCandidates() {
    const contract = safeObject(
      obDashboardContract().payload
    );

    const engine = safeObject(
      obDashboardEngineFeed()
    );

    const enginePayload = safeObject(
      engine.payload
      || engine.data
      || engine.snapshot
      || engine
    );


    const sources = [
      {
        rows: contract.candidates_preview,
        source: "dashboard_contract"
      },
      {
        rows: contract.candidates,
        source: "dashboard_contract"
      },
      {
        rows: contract.spotlight_cards,
        source: "dashboard_contract"
      },
      {
        rows: contract.final_spotlight_cards,
        source: "dashboard_contract"
      },
      {
        rows: enginePayload.candidates_preview,
        source: "engine_feed"
      },
      {
        rows: enginePayload.candidates,
        source: "engine_feed"
      }
    ];


    for (const source of sources) {
      const rows = safeArray(
        source.rows
      );

      if (!rows.length) {
        continue;
      }

      return rows
        .slice(0, 6)
        .map((row) => ({
          ...safeObject(row),
          __obux_source: source.source
        }));
    }


    return [];
  }


  function obCandidateVerdict(row) {
    return safeText(
      row.final_verdict
      || row.verdict
      || row.decision
      || row.status
      || row.tier,
      "WATCH"
    ).toUpperCase();
  }


  function obCandidateIsActionable(row) {
    const source = safeText(
      row.__obux_source
    );

    // Static fallback is never actionable.
    if (source === "static_market_fallback") {
      return false;
    }


    if (typeof row.actionable === "boolean") {
      return row.actionable;
    }


    if (
      row.blocked
      || row.risk_blocked
      || row.entry_blocked
      || row.capital_protection_mode
    ) {
      return false;
    }


    const verdict = obCandidateVerdict(
      row
    );


    return [
      "TAKE",
      "READY",
      "ACTIONABLE",
      "ENTER"
    ].includes(
      verdict
    );
  }


  function obDashboardHotSymbols() {
    const realCandidates = (
      obDashboardContractCandidates()
    );


    if (realCandidates.length) {
      return realCandidates
        .slice(0, 5)
        .map((row) => ({
          ...row,
          __obux_actionable: (
            obCandidateIsActionable(
              row
            )
          )
        }));
    }


    // Static market context may populate "Worth watching",
    // but cannot imply a live/real candidate or execution state.
    return obDashboardSymbols()
      .filter(
        (row) => row.tier === "hot"
      )
      .slice(0, 5)
      .map((row) => ({
        ...row,
        __obux_source: "static_market_fallback",
        __obux_actionable: false
      }));
  }


  // ================================================================================================
  // HEALTH / ACCOUNT INTERPRETATION
  // ================================================================================================

  function firstValue(objects, keys) {
    for (const object of objects) {
      if (
        !object
        || typeof object !== "object"
      ) {
        continue;
      }

      for (const key of keys) {
        if (
          Object.prototype.hasOwnProperty.call(
            object,
            key
          )
          && object[key] !== null
          && object[key] !== undefined
          && object[key] !== ""
        ) {
          return object[key];
        }
      }
    }

    return null;
  }


  function obDashboardAccountState() {
    const contract = safeObject(
      obDashboardContract().payload
    );

    const account = safeObject(
      contract.account
      || contract.account_snapshot
      || contract.snapshot
      || contract.state
    );


    const objects = [
      account,
      contract
    ];


    return {
      accountName: safeText(
        firstValue(
          objects,
          [
            "account_name",
            "mission_account",
            "account",
            "name"
          ]
        ),
        "Current OB account"
      ),

      mode: safeText(
        firstValue(
          objects,
          [
            "mode",
            "user_mode",
            "trading_mode"
          ]
        ),
        "Paper"
      ),

      buyingPower: firstValue(
        objects,
        [
          "buying_power",
          "buyingPower"
        ]
      ),

      accountValue: firstValue(
        objects,
        [
          "account_value",
          "balance",
          "equity",
          "net_liquidation",
          "net_liquidation_value"
        ]
      ),

      openPnl: firstValue(
        objects,
        [
          "open_pnl",
          "unrealized_pnl",
          "unrealized_pl",
          "pnl"
        ]
      ),

      riskUse: firstValue(
        objects,
        [
          "risk_utilization",
          "risk_used_pct",
          "risk_pct",
          "capital_at_risk_pct"
        ]
      )
    };
  }


  function obDashboardMarketHealth() {
    const all = obDashboardSymbols();

    const hot = all.filter(
      (row) => row.tier === "hot"
    ).length;

    const watch = all.filter(
      (row) => row.tier === "watch"
    ).length;

    const background = all.filter(
      (row) => row.tier === "background"
    ).length;


    const contract = safeObject(
      obDashboardContract().payload
    );


    const contractHealth = safeObject(
      contract.market_health
      || contract.health
    );


    const label = safeText(
      contractHealth.label
      || contractHealth.status,
      hot > 0
        ? "Active pockets"
        : "Quiet / mixed"
    );


    const regime = safeText(
      contractHealth.regime,
      hot > 0
        ? "Leadership pockets visible"
        : "No broad leadership"
    );


    return {
      label,
      regime,
      breadth: (
        `${hot} hot · ${watch} watch · ${background} background`
      ),

      caution: (
        "Static market-map context is being used only for orientation unless a fresher contract source is available."
      ),

      soulaana: (
        hot > 0
          ? "There are bright parts of the market worth watching, but brightness is not permission."
          : "The market is not giving us a strong reason to chase anything."
      )
    };
  }


  function obDashboardRiskInterpretation(account) {
    let value = numberValue(
      account.riskUse
    );


    if (value === null) {
      return {
        state: "limited",
        label: "Risk use not reported",
        explanation: (
          "I do not have a trustworthy risk-utilization number in this Dashboard contract, so I am not going to invent one."
        )
      };
    }


    if (
      value >= 0
      && value <= 1
    ) {
      value *= 100;
    }


    if (value >= 85) {
      return {
        state: "attention",
        label: `${Math.round(value)}% used`,
        explanation: (
          "Most of the reported risk allowance is already in use. New exposure deserves a very strong reason."
        )
      };
    }


    if (value >= 60) {
      return {
        state: "selective",
        label: `${Math.round(value)}% used`,
        explanation: (
          "You still have room, but I would be more selective with anything new."
        )
      };
    }


    return {
      state: "steady",
      label: `${Math.round(value)}% used`,
      explanation: (
        "Reported risk use is below the higher-attention bands. That does not make every setup safe."
      )
    };
  }


  // ================================================================================================
  // SOULAANA EXISTING CONTRACT
  // ================================================================================================

  function obDashboardExistingSoulaanaRead() {
    const contract = safeObject(
      obDashboardContract().payload
    );

    const value = contract.soulaana_read;


    if (
      value
      && typeof value === "object"
    ) {
      return value;
    }


    if (
      typeof value === "string"
      && value.trim()
    ) {
      return {
        what_it_means: value.trim()
      };
    }


    return {};
  }


  // ================================================================================================
  // POSITION EXPLANATION
  // ================================================================================================

  function obPositionSymbol(row) {
    return safeText(
      row.symbol,
      "Position"
    ).toUpperCase();
  }


  function obPositionStatus(row) {
    return safeText(
      row.manualStatus
      || row.status
      || row.position
      || row.state,
      "Open / Review"
    );
  }


  function obPositionRisk(row) {
    return safeText(
      row.risk
      || row.risk_summary
      || row.blocker,
      "Risk details not reported"
    );
  }


  function obPositionSoulaana(row) {
    const soulaana = safeObject(
      row.soulaana
    );

    const explanation = safeObject(
      row.position_explanation
    );


    return safeText(
      soulaana.what_it_means
      || soulaana.assessment
      || soulaana.summary
      || explanation.what_it_means
      || explanation.assessment
      || explanation.summary,
      (
        "This position is in the confirmed open-position preview. "
        + "Review its current risk and next condition before adding new exposure."
      )
    );
  }


  function obPositionNext(row) {
    const soulaana = safeObject(
      row.soulaana
    );

    const explanation = safeObject(
      row.position_explanation
    );


    return safeText(
      soulaana.next_action
      || explanation.next_action
      || row.next_action,
      "Continue monitoring."
    );
  }


  function obPositionNeedsAttention(row) {
    const action = obPositionNext(
      row
    ).toLowerCase();

    const verdict = safeText(
      row.verdict
      || row.final_verdict
    ).toUpperCase();


    return (
      [
        "EXIT",
        "REDUCE",
        "PROTECT"
      ].includes(verdict)
      ||
      [
        "review",
        "reduce",
        "protect",
        "adjust",
        "close"
      ].some(
        (token) => action.includes(token)
      )
    );
  }


  // ================================================================================================
  // HOT / OPPORTUNITY EXPLANATION
  // ================================================================================================

  function obCandidateSymbol(row) {
    return safeText(
      row.symbol,
      "—"
    ).toUpperCase();
  }


  function obCandidateScore(row) {
    const raw = firstValue(
      [
        row
      ],
      [
        "readiness_score",
        "promotion_score",
        "confidence_score",
        "setup_score",
        "quality_score",
        "score"
      ]
    );


    const value = numberValue(
      raw
    );


    return value === null
      ? "—"
      : String(
          Math.round(value)
        );
  }


  function obCandidateWhy(row) {
    return safeText(
      row.why
      || row.decision_reason
      || row.assessment
      || row.summary
      || row.signal_reason,
      (
        safeText(
          row.__obux_source
        ) === "static_market_fallback"
          ? safeText(
              row.why,
              "The static market map marks this symbol as worth watching."
            )
          : "The existing candidate contract elevated this symbol above background activity."
      )
    );
  }


  function obCandidateMissing(row) {
    if (
      safeText(
        row.__obux_source
      ) === "static_market_fallback"
    ) {
      return (
        "This is fallback market context only. A trusted candidate/action contract is still required before actionability can be claimed."
      );
    }


    return safeText(
      row.what_missing
      || row.missing_confirmation
      || row.invalidation_reason,
      (
        obCandidateIsActionable(row)
          ? "No missing confirmation was explicitly reported by this candidate payload."
          : "OB has not marked this setup actionable."
      )
    );
  }


  function obCandidateNext(row) {
    return safeText(
      row.next_action,
      (
        obCandidateIsActionable(row)
          ? "Review the setup conditions."
          : "Continue monitoring."
      )
    );
  }


  // ================================================================================================
  // SINCE YOU WERE HERE
  // ================================================================================================

  function obDashboardSnapshot(
    positions,
    hotSymbols
  ) {
    return {
      positions: positions
        .map(obPositionSymbol)
        .sort(),

      attention: positions
        .filter(obPositionNeedsAttention)
        .map(obPositionSymbol)
        .sort(),

      hot: hotSymbols
        .map(obCandidateSymbol)
        .sort(),

      actionable: hotSymbols
        .filter(obCandidateIsActionable)
        .map(obCandidateSymbol)
        .sort()
    };
  }


  function obLoadPreviousSnapshot() {
    try {
      const raw = window.sessionStorage.getItem(
        SNAPSHOT_KEY
      );

      if (!raw) return null;

      const parsed = JSON.parse(raw);

      return (
        parsed
        && typeof parsed === "object"
      )
        ? parsed
        : null;

    } catch (_error) {
      return null;
    }
  }


  function obStoreSnapshot(snapshot) {
    try {
      window.sessionStorage.setItem(
        SNAPSHOT_KEY,
        JSON.stringify(snapshot)
      );
    } catch (_error) {
      // Session history is convenience-only.
      // Failure must never block the room.
    }
  }


  function difference(
    current,
    previous
  ) {
    const previousSet = new Set(
      safeArray(previous)
    );

    return safeArray(current).filter(
      (item) => !previousSet.has(item)
    );
  }


  function obSinceYouWereHere(
    previous,
    current
  ) {
    if (!previous) {
      return {
        headline: (
          "I’m setting your Dashboard baseline."
        ),

        explanation: (
          "The next time you come back, I can tell you which position, attention, and watch states actually changed."
        )
      };
    }


    const newAttention = difference(
      current.attention,
      previous.attention
    );

    const clearedAttention = difference(
      previous.attention,
      current.attention
    );

    const newHot = difference(
      current.hot,
      previous.hot
    );

    const cooled = difference(
      previous.hot,
      current.hot
    );


    const pieces = [];


    if (newAttention.length) {
      pieces.push(
        `New attention: ${newAttention.join(", ")}.`
      );
    }


    if (clearedAttention.length) {
      pieces.push(
        `No longer flagged for attention: ${clearedAttention.join(", ")}.`
      );
    }


    if (newHot.length) {
      pieces.push(
        `New to the watch picture: ${newHot.join(", ")}.`
      );
    }


    if (cooled.length) {
      pieces.push(
        `Dropped out of the elevated watch picture: ${cooled.join(", ")}.`
      );
    }


    if (!pieces.length) {
      return {
        headline: (
          "Nothing material changed since your last Dashboard visit."
        ),

        explanation: (
          "Your confirmed position, attention, and elevated-watch picture is effectively where you left it."
        )
      };
    }


    return {
      headline: (
        "Here’s what changed since you were here."
      ),

      explanation: (
        pieces.join(" ")
      )
    };
  }


  // ================================================================================================
  // OBUX006 — NOW BRIEF
  // ================================================================================================

  function obDashboardNowBrief(
    positions,
    hotSymbols,
    account,
    risk,
    since
  ) {
    const attention = positions.filter(
      obPositionNeedsAttention
    );

    const actionable = hotSymbols.filter(
      obCandidateIsActionable
    );

    const watchOnly = hotSymbols.filter(
      (row) => !obCandidateIsActionable(row)
    );


    let headline;
    let meaning;
    let needs;
    let next;
    let noAction;


    if (attention.length) {
      headline = (
        "Something in your open book deserves a look."
      );

      meaning = (
        `${attention.length} confirmed open position`
        + `${attention.length === 1 ? "" : "s"} `
        + "currently carry a review condition."
      );

      needs = (
        "Review "
        + attention
          .slice(0, 4)
          .map(obPositionSymbol)
          .join(", ")
        + "."
      );

      next = (
        "Handle the flagged open position before lower-priority opportunities."
      );

      noAction = false;

    } else if (actionable.length) {
      headline = (
        "Your open book is calm, and a setup is ready for closer review."
      );

      meaning = (
        `${actionable.length} setup`
        + `${actionable.length === 1 ? " is" : "s are"} `
        + "marked actionable by the existing candidate contract."
      );

      needs = (
        "No confirmed open position is demanding immediate review."
      );

      next = (
        "Review the actionable setup conditions before making any trading decision."
      );

      noAction = false;

    } else if (watchOnly.length) {
      headline = (
        "Nothing needs you right now."
      );

      meaning = (
        `${watchOnly.length} symbol`
        + `${watchOnly.length === 1 ? " is" : "s are"} `
        + "worth watching, but none is being presented as actionable."
      );

      needs = (
        "There is no immediate Dashboard action requirement."
      );

      next = (
        "Continue monitoring."
      );

      noAction = true;

    } else {
      headline = (
        "Nothing needs you right now."
      );

      meaning = (
        "No confirmed position review or actionable candidate is currently surfacing from the available Dashboard contracts."
      );

      needs = (
        "No immediate Dashboard action is required."
      );

      next = (
        "Continue monitoring."
      );

      noAction = true;
    }


    return {
      headline,
      meaning,

      why: (
        risk.explanation
      ),

      changed: (
        since.explanation
      ),

      needs,

      canWait: (
        "Feed diagnostics, readiness receipts, beta proof, and engineering detail can stay closed unless you choose Show me why."
      ),

      next,
      noAction,

      accountName: (
        account.accountName
      ),

      mode: (
        account.mode
      )
    };
  }


  // ================================================================================================
  // OBUX010 — EVIDENCE SOURCE SUMMARY
  // ================================================================================================

  function obDashboardSourceState(
    positions,
    hotSymbols
  ) {
    const contract = (
      obDashboardContract()
    );


    const candidateSource = hotSymbols.length
      ? safeText(
          hotSymbols[0].__obux_source,
          "unknown"
        )
      : "none";


    const positionSource = positions.length
      ? safeText(
          positions[0].__obux_source,
          "unknown"
        )
      : "none";


    return {
      contract: contract.source,
      candidateSource,
      positionSource
    };
  }


  // ================================================================================================
  // RENDER HELPERS
  // ================================================================================================

  function metricCard(
    label,
    value,
    explanation
  ) {
    return `
      <article class="obux-dashboard-metric">
        <span>${compact(label)}</span>
        <strong>${compact(value, "Not reported")}</strong>
        <p>${compact(explanation)}</p>
      </article>
    `;
  }


  function renderPosition(row) {
    const symbol = obPositionSymbol(
      row
    );

    const attention = obPositionNeedsAttention(
      row
    );


    return `
      <article class="obux-dashboard-position-card">
        <div class="obux-dashboard-card-top">
          <div>
            <strong class="obux-symbol">${compact(symbol)}</strong>
            <span>${compact(obPositionStatus(row))}</span>
          </div>

          <span class="obux-dashboard-chip ${attention ? "attention" : "calm"}">
            ${attention ? "Review" : "Watching"}
          </span>
        </div>

        <div class="obux-dashboard-position-risk">
          <span>RISK</span>
          <strong>${compact(obPositionRisk(row))}</strong>
        </div>

        <p>
          ${compact(obPositionSoulaana(row))}
        </p>

        <div class="obux-dashboard-next">
          <span>SOULAANA SAYS</span>
          <strong>${compact(obPositionNext(row))}</strong>
        </div>
      </article>
    `;
  }


  function renderHot(row) {
    const actionable = obCandidateIsActionable(
      row
    );

    const fallback = (
      safeText(
        row.__obux_source
      )
      === "static_market_fallback"
    );


    return `
      <article class="obux-dashboard-hot-card ${actionable ? "actionable" : ""}">
        <div class="obux-dashboard-card-top">
          <strong class="obux-symbol">
            ${compact(obCandidateSymbol(row))}
          </strong>

          <span class="obux-dashboard-chip ${actionable ? "actionable" : "watch"}">
            ${
              fallback
                ? "Fallback watch"
                : actionable
                  ? "Actionable review"
                  : "Worth watching"
            }
          </span>
        </div>

        <div class="obux-dashboard-score">
          <span>OB SCORE</span>
          <strong>${compact(obCandidateScore(row), "—")}</strong>
          <small>${compact(obCandidateVerdict(row))}</small>
        </div>

        <div class="obux-dashboard-explain">
          <span>WHY IT'S HERE</span>
          <p>${compact(obCandidateWhy(row))}</p>
        </div>

        <div class="obux-dashboard-explain">
          <span>WHAT'S MISSING</span>
          <p>${compact(obCandidateMissing(row))}</p>
        </div>

        <div class="obux-dashboard-next">
          <span>NEXT</span>
          <strong>${compact(obCandidateNext(row))}</strong>
        </div>
      </article>
    `;
  }


  // ================================================================================================
  // REAL RENDERER
  // ================================================================================================

  function obRenderDashboard() {
    const mount = document.getElementById(
      "dashboardMount"
    );


    if (!mount) {
      return;
    }


    const positions = (
      obDashboardOpenPositions()
    );

    const hotSymbols = (
      obDashboardHotSymbols()
    );

    const marketHealth = (
      obDashboardMarketHealth()
    );

    const account = (
      obDashboardAccountState()
    );

    const risk = (
      obDashboardRiskInterpretation(
        account
      )
    );


    const snapshot = obDashboardSnapshot(
      positions,
      hotSymbols
    );


    const previousSnapshot = (
      obLoadPreviousSnapshot()
    );


    const since = (
      obSinceYouWereHere(
        previousSnapshot,
        snapshot
      )
    );


    obStoreSnapshot(
      snapshot
    );


    const brief = (
      obDashboardNowBrief(
        positions,
        hotSymbols,
        account,
        risk,
        since
      )
    );


    const sourceState = (
      obDashboardSourceState(
        positions,
        hotSymbols
      )
    );


    const existingSoulaana = (
      obDashboardExistingSoulaanaRead()
    );


    const existingMeaning = safeText(
      existingSoulaana.what_it_means
      || existingSoulaana.assessment
      || existingSoulaana.summary
    );


    const effectiveMeaning = (
      existingMeaning
      || brief.meaning
    );


    const attentionPositions = (
      positions.filter(
        obPositionNeedsAttention
      )
    );


    const actionableHot = (
      hotSymbols.filter(
        obCandidateIsActionable
      )
    );


    const attentionCards = [
      ...attentionPositions.map(
        (row) => ({
          symbol: obPositionSymbol(row),
          kind: "Position review",
          explanation: obPositionSoulaana(row),
          next: obPositionNext(row)
        })
      ),

      ...actionableHot.map(
        (row) => ({
          symbol: obCandidateSymbol(row),
          kind: "Candidate review",
          explanation: obCandidateWhy(row),
          next: obCandidateNext(row)
        })
      )
    ].slice(
      0,
      6
    );


    mount.innerHTML = `
      <main
        id="obuxDashboardShell"
        class="obux-dashboard-shell"
        data-obux-version="${VERSION}"
      >

        <!-- =======================================================================================
             OBUX006 — SOULAANA RIGHT NOW
             ======================================================================================= -->

        <section class="ob-panel obux-dashboard-now">

          <div class="obux-dashboard-now-top">
            <div>
              <div class="obux-dashboard-kicker">
                SOULAANA · RIGHT NOW
              </div>

              <h2>
                ${compact(brief.headline)}
              </h2>

              <p class="obux-dashboard-lead">
                ${compact(effectiveMeaning)}
              </p>
            </div>

            <div class="obux-dashboard-context">
              <span>${compact(brief.accountName)}</span>
              <span>${compact(brief.mode)}</span>
              <span>Live Auto locked</span>
            </div>
          </div>


          <div class="obux-dashboard-meaning-grid">

            <article>
              <span>WHAT THIS MEANS</span>
              <p>${compact(effectiveMeaning)}</p>
            </article>

            <article>
              <span>WHY IT MATTERS</span>
              <p>${compact(brief.why)}</p>
            </article>

            <article>
              <span>WHAT NEEDS YOU</span>
              <p>${compact(brief.needs)}</p>
            </article>

            <article>
              <span>WHAT CAN WAIT</span>
              <p>${compact(brief.canWait)}</p>
            </article>

          </div>


          <div class="obux-dashboard-action-state ${brief.noAction ? "calm" : "active"}">
            <strong>
              ${
                brief.noAction
                  ? "Nothing needs you right now."
                  : "Next:"
              }
            </strong>

            <span>
              ${compact(brief.next)}
            </span>
          </div>

        </section>


        <!-- =======================================================================================
             OBUX007 — ACCOUNT / RISK HEALTH
             ======================================================================================= -->

        <section class="obux-dashboard-section">

          <div class="obux-dashboard-section-head">
            <div>
              <div class="obux-dashboard-kicker">
                ACCOUNT HEALTH
              </div>

              <h3>
                ${compact(risk.label)}
              </h3>

              <p>
                ${compact(risk.explanation)}
              </p>
            </div>

            <span class="obux-dashboard-state-chip ${compact(risk.state)}">
              ${compact(risk.state).replace(/_/g, " ")}
            </span>
          </div>


          <div class="obux-dashboard-metric-grid">

            ${metricCard(
              "Buying power",
              formatMoney(account.buyingPower),
              (
                account.buyingPower === null
                || account.buyingPower === undefined
              )
                ? "The current Dashboard contract does not report buying power."
                : "Capital currently reported as available for additional positions."
            )}

            ${metricCard(
              "Account value",
              formatMoney(account.accountValue),
              (
                account.accountValue === null
                || account.accountValue === undefined
              )
                ? "The current Dashboard contract does not report account value."
                : "Account-level value currently visible to OB."
            )}

            ${metricCard(
              "Open P&L",
              formatMoney(account.openPnl),
              (
                account.openPnl === null
                || account.openPnl === undefined
              )
                ? "The current Dashboard contract does not report open P&L."
                : "Current unrealized result reported by the available account snapshot."
            )}

            ${metricCard(
              "Risk use",
              formatPercent(account.riskUse),
              risk.explanation
            )}

            ${metricCard(
              "Confirmed open positions",
              String(positions.length),
              (
                positions.length
                  ? `Sourced from ${sourceState.positionSource.replace(/_/g, " ")}.`
                  : "No confirmed open-position preview is currently available."
              )
            )}

          </div>

        </section>


        <!-- =======================================================================================
             OBUX008 — SINCE YOU WERE HERE
             ======================================================================================= -->

        <section class="ob-panel obux-dashboard-since">
          <div class="obux-dashboard-kicker">
            SINCE YOU WERE HERE
          </div>

          <h3>
            ${compact(since.headline)}
          </h3>

          <p>
            ${compact(since.explanation)}
          </p>
        </section>


        <!-- =======================================================================================
             OBUX009 — WHAT NEEDS YOU
             ======================================================================================= -->

        <section class="obux-dashboard-section">

          <div class="obux-dashboard-section-head">
            <div>
              <div class="obux-dashboard-kicker">
                WHAT NEEDS YOU
              </div>

              <h3>
                Attention before activity
              </h3>

              <p>
                Interesting and actionable are two different things.
              </p>
            </div>
          </div>


          ${
            attentionCards.length
              ? `
                <div class="obux-dashboard-attention-grid">
                  ${attentionCards.map(
                    (item) => `
                      <article class="ob-panel obux-dashboard-attention-card">
                        <div class="obux-dashboard-card-top">
                          <strong class="obux-symbol">
                            ${compact(item.symbol)}
                          </strong>

                          <span class="obux-dashboard-chip attention">
                            ${compact(item.kind)}
                          </span>
                        </div>

                        <p>
                          ${compact(item.explanation)}
                        </p>

                        <div class="obux-dashboard-next">
                          <span>NEXT</span>
                          <strong>${compact(item.next)}</strong>
                        </div>
                      </article>
                    `
                  ).join("")}
                </div>
              `
              : `
                <div class="ob-panel obux-dashboard-calm-card">
                  <strong>
                    Nothing needs you right now.
                  </strong>

                  <p>
                    No confirmed position-review condition or actionable candidate crossed the current Dashboard threshold.
                  </p>
                </div>
              `
          }

        </section>


        <!-- =======================================================================================
             OPEN BOOK
             ======================================================================================= -->

        <section class="obux-dashboard-section">

          <div class="obux-dashboard-section-head">
            <div>
              <div class="obux-dashboard-kicker">
                OPEN BOOK
              </div>

              <h3>
                Your confirmed position preview
              </h3>

              <p>
                A symbol appears here only when an existing Dashboard/feed contract actually reports it as an open-position preview.
              </p>
            </div>
          </div>


          ${
            positions.length
              ? `
                <div class="obux-dashboard-position-grid">
                  ${positions.map(
                    renderPosition
                  ).join("")}
                </div>
              `
              : `
                <div class="ob-panel obux-dashboard-calm-card">
                  <strong>
                    No confirmed open-position preview is available.
                  </strong>

                  <p>
                    I am not filling this section with watched symbols and pretending they are positions.
                  </p>
                </div>
              `
          }

        </section>


        <!-- =======================================================================================
             OBUX009 — HOT NOW
             ======================================================================================= -->

        <section class="obux-dashboard-section">

          <div class="obux-dashboard-section-head">
            <div>
              <div class="obux-dashboard-kicker">
                HOT NOW
              </div>

              <h3>
                Worth your eyes — not automatically your money
              </h3>

              <p>
                A bright symbol can be useful context without being ready for action.
              </p>
            </div>

            <span class="obux-dashboard-state-chip">
              ${compact(sourceState.candidateSource).replace(/_/g, " ")}
            </span>
          </div>


          ${
            hotSymbols.length
              ? `
                <div class="obux-dashboard-hot-grid">
                  ${hotSymbols.map(
                    renderHot
                  ).join("")}
                </div>
              `
              : `
                <div class="ob-panel obux-dashboard-calm-card">
                  <strong>
                    Nothing is elevated enough to show here.
                  </strong>

                  <p>
                    Soulaana does not manufacture an opportunity just to keep the room busy.
                  </p>
                </div>
              `
          }

        </section>


        <!-- =======================================================================================
             MARKET CONTEXT
             ======================================================================================= -->

        <section class="ob-panel obux-dashboard-market-context">

          <div>
            <div class="obux-dashboard-kicker">
              MARKET WEATHER
            </div>

            <h3>
              ${compact(marketHealth.label)}
            </h3>

            <p>
              ${compact(marketHealth.breadth)}
            </p>
          </div>

          <div>
            <strong>
              ${compact(marketHealth.regime)}
            </strong>

            <p>
              ${compact(marketHealth.caution)}
            </p>
          </div>

          <a
            class="dashboard-action-button"
            href="/ob/market-map"
          >
            Open Market Map
          </a>

        </section>


        <!-- =======================================================================================
             OBUX010 — SHOW ME WHY
             ======================================================================================= -->

        <details
          id="obuxDashboardEvidence"
          class="ob-panel obux-dashboard-evidence"
        >

          <summary>
            <div>
              <div class="obux-dashboard-kicker">
                TECHNICAL EVIDENCE
              </div>

              <strong>
                Show me why
              </strong>
            </div>

            <span class="obux-dashboard-evidence-plus">
              +
            </span>
          </summary>


          <div class="obux-dashboard-evidence-body">

            <p>
              This is where feed plumbing, readiness proof, diagnostics, receipts, beta controls,
              source audits, and other technical evidence belong. They support the explanation;
              they do not lead the Dashboard.
            </p>


            <div class="obux-dashboard-source-grid">

              ${metricCard(
                "Dashboard contract",
                sourceState.contract.replace(/_/g, " "),
                "Existing OB data-contract source."
              )}

              ${metricCard(
                "Position source",
                sourceState.positionSource.replace(/_/g, " "),
                "Fallback market symbols are never treated as confirmed open positions."
              )}

              ${metricCard(
                "Candidate source",
                sourceState.candidateSource.replace(/_/g, " "),
                (
                  sourceState.candidateSource === "static_market_fallback"
                    ? "Static market data is being shown as watch context only."
                    : "Existing contract/feed candidate source."
                )
              )}

            </div>


            <div
              id="obuxDashboardEvidenceSink"
              class="obux-dashboard-evidence-sink"
            >
              <div class="obux-dashboard-evidence-empty">
                Additional Dashboard proof and engineering panels will collect here.
              </div>
            </div>

          </div>

        </details>

      </main>
    `;


    window.OBUX_DASHBOARD_STATE = {
      version: VERSION,

      source_state: sourceState,

      confirmed_open_positions: (
        positions.length
      ),

      hot_now_count: (
        hotSymbols.length
      ),

      attention_count: (
        attentionCards.length
      ),

      no_action_needed: (
        brief.noAction
      ),

      static_market_fallback_actionable: false,

      static_market_fallback_confirmed_position: false,

      broker_action_performed: false,

      capital_action_performed: false,

      permission_mutation_performed: false,

      live_auto_locked: true
    };


    window.dispatchEvent(
      new CustomEvent(
        "obux:dashboard-rendered",
        {
          detail: (
            window.OBUX_DASHBOARD_STATE
          )
        }
      )
    );
  }


  document.addEventListener(
    "DOMContentLoaded",
    obRenderDashboard
  );


  // Compatibility exports.
  window.obDashboardSymbols = (
    obDashboardSymbols
  );

  window.obDashboardHotSymbols = (
    obDashboardHotSymbols
  );

  window.obDashboardOpenPositions = (
    obDashboardOpenPositions
  );

  window.obDashboardMarketHealth = (
    obDashboardMarketHealth
  );

  window.obPositionStatus = (
    obPositionStatus
  );

  window.obPositionRisk = (
    obPositionRisk
  );

  window.obPositionSoulaana = (
    obPositionSoulaana
  );

  window.obRenderDashboard = (
    obRenderDashboard
  );

})();


// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.dashboardContract) {
  window.OB_DASHBOARD_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.dashboardContract();
}

// OBSERVATORY_V23_FINAL_VISUAL_CONSISTENCY_PASS_ROOM_FLAG
window.OB_V23_ROOM_VISUAL_READY = true;

// OBSERVATORY_V25_SAFE_ENGINE_FEED_ADAPTER_ROOM_FLAG
window.OB_V25_ENGINE_FEED_READY = true;

// OBSERVATORY_V26_REAL_SNAPSHOT_DISPLAY_WIRING_ROOM_FLAG
window.OB_V26_SNAPSHOT_DISPLAY_READY = true;

// OBSERVATORY_V27_ROOM_LEVEL_REAL_DATA_POLISH_ROOM_FLAG
window.OB_V27_ROOM_DATA_POLISH_READY = true;

// OBSERVATORY_V28_CANDIDATE_SIGNAL_CARD_NORMALIZATION_ROOM_FLAG
window.OB_V28_CANDIDATE_CARDS_READY = true;

// OBSERVATORY_V29_MANUAL_LIVE_RECEIPTS_REVIEW_INTEGRATION_ROOM_FLAG
window.OB_V29_MANUAL_LIVE_RECEIPTS_READY = true;

// OBSERVATORY_V31_FINAL_PRIVATE_BETA_QA_PASS_ROOM_FLAG
window.OB_V31_PRIVATE_BETA_QA_READY = true;

// OBSERVATORY_V32_REAL_ENGINE_FEED_EXPANSION_READ_ONLY_ROOM_FLAG
window.OB_V32_ENGINE_FEED_EXPANSION_READY = true;

// OBSERVATORY_V34_ENGINE_FEED_TRUST_LABELS_ROOM_WARNINGS_ROOM_FLAG
window.OB_V34_ENGINE_TRUST_LABELS_READY = true;

// OBSERVATORY_V35_ENGINE_FEED_CANONICAL_ROOM_MAPPING_ROOM_FLAG
window.OB_V35_ENGINE_ROOM_MAPPING_READY = true;

// OBSERVATORY_V36_OWNER_CONSOLE_SOURCE_AUDIT_ACTION_PLAN_ROOM_FLAG
window.OB_V36_OWNER_SOURCE_AUDIT_READY = true;

// OBSERVATORY_V37_PRIVATE_BETA_LAUNCH_CONTROL_CHECKLIST_ROOM_FLAG
window.OB_V37_PRIVATE_BETA_LAUNCH_CONTROL_READY = true;

// OBSERVATORY_V38_PRIVATE_BETA_TESTER_INVITE_PACKET_BUILDER_ROOM_FLAG
window.OB_V38_PRIVATE_BETA_INVITE_PACKET_READY = true;

// OBSERVATORY_V39_TESTER_FEEDBACK_INTAKE_CONFUSION_REPORT_PACKET_ROOM_FLAG
window.OB_V39_PRIVATE_BETA_FEEDBACK_INTAKE_READY = true;

// OBSERVATORY_V40_OWNER_TESTER_FEEDBACK_REVIEW_QUEUE_ROOM_FLAG
window.OB_V40_PRIVATE_BETA_FEEDBACK_REVIEW_QUEUE_READY = true;

// OBSERVATORY_V41_GUIDED_PRIVATE_BETA_SESSION_RUNBOOK_ROOM_FLAG
window.OB_V41_PRIVATE_BETA_SESSION_RUNBOOK_READY = true;

// OBSERVATORY_V42_PRIVATE_BETA_ISSUE_TRIAGE_FIX_PRIORITY_ROOM_FLAG
window.OB_V42_PRIVATE_BETA_ISSUE_TRIAGE_READY = true;

// OBSERVATORY_V43_PRIVATE_BETA_SESSION_CLOSEOUT_REPORT_ROOM_FLAG
window.OB_V43_PRIVATE_BETA_SESSION_CLOSEOUT_READY = true;

// OBSERVATORY_V44_PRIVATE_BETA_FIX_VERIFICATION_CHECKLIST_ROOM_FLAG
window.OB_V44_PRIVATE_BETA_FIX_VERIFICATION_READY = true;

// OBSERVATORY_V45_NEXT_TESTER_CLEARANCE_GATE_ROOM_FLAG
window.OB_V45_PRIVATE_BETA_NEXT_TESTER_GATE_READY = true;

// OB_GIANT_PACK_001_OWNER_USER_ACCOUNT_EXPERIENCE_ROOM_FLAG
window.OB_GIANT_PACK_001_ACCOUNT_EXPERIENCE_READY = true;

// OB_GIANT_PACK_002_MANUAL_LIVE_LEVEL_1_OPERATING_ROOM_FLAG
window.OB_GIANT_PACK_002_MANUAL_LIVE_L1_READY = true;

// OB_GIANT_PACK_003_RECEIPTS_REVIEW_CENTER_FOUNDATION_FLAG
window.OB_GIANT_PACK_003_RECEIPTS_REVIEW_READY = true;

// OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_POLISH_FLAG
window.OB_GIANT_PACK_004_PRIVATE_BETA_TOWER_LOCK_READY = true;

// OB_GIANT_PACK_005_MANUAL_LIVE_SAFETY_PREFLIGHT_GATE_FLAG
window.OB_GIANT_PACK_005_MANUAL_LIVE_PREFLIGHT_READY = true;

// OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET_FLAG
window.OB_GIANT_PACK_006_MANUAL_LIVE_DECISION_PACKET_READY = true;

// OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_FLAG
window.OB_GIANT_PACK_007_MANUAL_BROKER_CHECKLIST_FILL_CAPTURE_READY = true;

// OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_FLAG
window.OB_GIANT_PACK_008_POSITION_MONITOR_EXIT_CLOSE_CAPTURE_READY = true;

// OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_RECEIPT_FLAG
window.OB_GIANT_PACK_009_FINAL_TRADE_REVIEW_PERFORMANCE_READY = true;

// OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_010_MANUAL_LIVE_L1_READINESS_READY = true;

// OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_FLAG
window.OB_GIANT_PACK_011_OWNER_REHEARSAL_ENGINE_READY = true;

// OB_GIANT_PACK_012_REHEARSAL_RECORD_PERSISTENCE_CONTRACT_FLAG
window.OB_GIANT_PACK_012_REHEARSAL_RECORD_CONTRACTS_READY = true;

// OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_FLAG
window.OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_READY = true;

// OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_FLAG
window.OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_READY = true;

// OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_FLAG
window.OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_READY = true;

// OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_WIRING_PREP_FLAG
window.OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_PREP_READY = true;

// OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER_FLAG
window.OB_GIANT_PACK_017_REAL_CANDIDATE_REHEARSAL_ADAPTER_READY = true;

// OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS_FLAG
window.OB_GIANT_PACK_018_MANUAL_LIVE_OWNER_REHEARSAL_FINAL_READINESS_READY = true;

// OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE_FLAG
window.OB_GIANT_PACK_019_REHEARSAL_QUALITY_FRESHNESS_GATE_READY = true;

// OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL_FLAG
window.OB_GIANT_PACK_020_MANUAL_LIVE_PRE_LIVE_LOCK_WALL_READY = true;

// OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_CONTRACT_FLAG
window.OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_READY = true;

// OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_FLAG
window.OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_READY = true;

// OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_FLAG
window.OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_READY = true;

// OB_GIANT_PACK_024_PRACTICE_LESSON_REVIEW_QUEUE_FLAG
window.OB_GIANT_PACK_024_PRACTICE_LESSON_REVIEW_QUEUE_READY = true;

// OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_FLAG
window.OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_READY = true;

// OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_FLAG
window.OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_READY = true;

// OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_FLAG
window.OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_READY = true;

// OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_FLAG
window.OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_READY = true;

// OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_FLAG
window.OB_GIANT_PACK_031_MANUAL_LIVE_OPERATOR_CONFIDENCE_BOARD_READY = true;

// OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_FLAG
window.OB_GIANT_PACK_032_MANUAL_LIVE_OPERATOR_STEP_CONFIDENCE_CHECKLIST_READY = true;

// OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_FLAG
window.OB_GIANT_PACK_033_MANUAL_LIVE_OPERATOR_SCENARIO_CONFIDENCE_REVIEW_READY = true;

// OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_FLAG
window.OB_GIANT_PACK_034_MANUAL_LIVE_OPERATOR_CONFIDENCE_IMPROVEMENT_PLAN_READY = true;

// OB_GIANT_PACK_035_MANUAL_LIVE_OPERATOR_CONFIDENCE_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_035_MANUAL_LIVE_OPERATOR_CONFIDENCE_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_FLAG
window.OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_READY = true;

// OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_FLAG
window.OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_READY = true;

// OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_FLAG
window.OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_READY = true;

// OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE_FLAG
window.OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE_READY = true;

// OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT_FLAG
window.OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT_READY = true;

// OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF_FLAG
window.OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF_READY = true;
