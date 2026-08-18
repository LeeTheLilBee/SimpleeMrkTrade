// THE OBSERVATORY
// OBUX031–OBUX035
//
// LIVE ROOM BEHAVIOR:
//   canonical adapter refresh
//       → obEngineFeedAdapterUpdated
//       → reread marketMapContract()
//       → rerender Market Map + Soulaana
//
// NO independent data fetch.
// NO independent market polling.
// NO second engine.

(function () {
  "use strict";


  const VERSION =
    "OBUX031_OBUX035_LIVE_MARKET_MAP";


  let previousSnapshot =
    null;


  let latestFeedEventAt =
    null;


  let relativeAgeTimer =
    null;


  function byId(id) {
    return document.getElementById(
      id
    );
  }


  function safeArray(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


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


  function text(
    value,
    fallback
  ) {
    if (
      value === null
      ||
      value === undefined
      ||
      value === ""
    ) {
      return fallback;
    }

    return String(value);
  }


  function symbolFrom(value) {
    if (
      typeof value === "string"
    ) {
      return value
        .trim()
        .toUpperCase();
    }

    if (
      !value
      ||
      typeof value !== "object"
    ) {
      return "";
    }

    return String(
      value.symbol
      ||
      value.ticker
      ||
      ""
    )
      .trim()
      .toUpperCase();
  }


  function canonicalProjection() {
    const api =
      window.OB_ENGINE_FEED_ADAPTER_V25
      ||
      window.OB_CANONICAL_WEB_PROJECTION_OBDATA003_API;


    if (
      api
      &&
      typeof api.getProjection === "function"
    ) {
      return api.getProjection();
    }


    return {
      projection_status:
        "unavailable",

      freshness:
        "unavailable",

      source:
        null,

      as_of:
        null,

      current_eligible:
        false,

      display_eligible:
        false,

      reason:
        "Canonical engine projection is unavailable.",
    };
  }


  function marketMapContract() {
    const contracts =
      window.OB_DATA_CONTRACTS_V22;


    if (
      contracts
      &&
      typeof contracts.marketMapContract === "function"
    ) {
      return contracts.marketMapContract();
    }


    return {
      sectors: [],
      symbols: [],
      signals: [],
      watchlist: [],
      open_positions: [],
      candidates: [],
      source: null,
      as_of: null,
      freshness: "unavailable",
      current: false,
    };
  }


  function symbolSet(values) {
    return new Set(
      safeArray(values)
        .map(
          symbolFrom
        )
        .filter(
          Boolean
        )
    );
  }


  function evidenceSets(contract) {
    return {
      positions:
        symbolSet(
          contract.open_positions
        ),

      signals:
        symbolSet(
          contract.signals
        ),

      candidates:
        symbolSet(
          contract.candidates
        ),

      watchlist:
        symbolSet(
          contract.watchlist
        ),
    };
  }


  function snapshotOf(
    contract,
    projection
  ) {
    const sortedSymbols = value =>
      Array.from(
        symbolSet(value)
      ).sort();


    return {
      source:
        projection.source
        ||
        null,

      as_of:
        projection.as_of
        ||
        null,

      freshness:
        projection.freshness
        ||
        "unavailable",

      current:
        Boolean(
          projection.current_eligible
        ),

      display:
        Boolean(
          projection.display_eligible
        ),

      sectors:
        safeArray(
          contract.sectors
        ).length,

      symbols:
        sortedSymbols(
          contract.symbols
        ),

      signals:
        sortedSymbols(
          contract.signals
        ),

      positions:
        sortedSymbols(
          contract.open_positions
        ),

      candidates:
        sortedSymbols(
          contract.candidates
        ),

      watchlist:
        sortedSymbols(
          contract.watchlist
        ),
    };
  }


  function deltaSet(
    before,
    after
  ) {
    const oldSet =
      new Set(
        before
        ||
        []
      );

    const newSet =
      new Set(
        after
        ||
        []
      );


    return {
      added:
        Array.from(
          newSet
        ).filter(
          item =>
            !oldSet.has(item)
        ),

      removed:
        Array.from(
          oldSet
        ).filter(
          item =>
            !newSet.has(item)
        ),
    };
  }


  function describeChange(
    previous,
    current
  ) {
    if (!previous) {
      if (!current.display) {
        return (
          "The first canonical view is not display-eligible, "
          +
          "so I am not inventing a market change story."
        );
      }

      return (
        "This is the first source-backed Market Map view "
        +
        "in this browser session."
      );
    }


    if (
      previous.display
      &&
      !current.display
    ) {
      return (
        "Display eligibility disappeared on the latest feed refresh. "
        +
        "I cleared the prior sky instead of carrying stale visual truth forward."
      );
    }


    const parts = [];


    if (
      previous.freshness
      !==
      current.freshness
    ) {
      parts.push(
        (
          "freshness changed from "
          +
          previous.freshness
          +
          " to "
          +
          current.freshness
        )
      );
    }


    if (
      previous.source
      !==
      current.source
    ) {
      parts.push(
        "the source label changed"
      );
    }


    if (
      previous.sectors
      !==
      current.sectors
    ) {
      parts.push(
        (
          "sector groups changed from "
          +
          previous.sectors
          +
          " to "
          +
          current.sectors
        )
      );
    }


    const groups = [
      [
        "signals",
        previous.signals,
        current.signals,
      ],

      [
        "positions",
        previous.positions,
        current.positions,
      ],

      [
        "candidates",
        previous.candidates,
        current.candidates,
      ],

      [
        "watchlist",
        previous.watchlist,
        current.watchlist,
      ],
    ];


    groups.forEach(
      function (group) {
        const label =
          group[0];

        const delta =
          deltaSet(
            group[1],
            group[2]
          );


        if (
          delta.added.length
          ||
          delta.removed.length
        ) {
          const pieces = [];

          if (delta.added.length) {
            pieces.push(
              (
                "added "
                +
                delta.added.join(", ")
              )
            );
          }

          if (delta.removed.length) {
            pieces.push(
              (
                "removed "
                +
                delta.removed.join(", ")
              )
            );
          }

          parts.push(
            (
              label
              +
              " "
              +
              pieces.join(" and ")
            )
          );
        }
      }
    );


    if (!parts.length) {
      return (
        "The latest canonical feed refresh did not materially "
        +
        "change the Market Map evidence."
      );
    }


    return (
      "Since the previous feed view, "
      +
      parts.join("; ")
      +
      "."
    );
  }


  function formatDate(value) {
    if (!value) {
      return "not identified";
    }


    const parsed =
      new Date(value);


    if (
      Number.isNaN(
        parsed.getTime()
      )
    ) {
      return String(value);
    }


    return parsed.toLocaleString();
  }


  function relativeAge(value) {
    if (!value) {
      return "unknown";
    }


    const parsed =
      new Date(value);


    if (
      Number.isNaN(
        parsed.getTime()
      )
    ) {
      return "unknown";
    }


    const seconds =
      Math.max(
        0,
        Math.floor(
          (
            Date.now()
            -
            parsed.getTime()
          )
          /
          1000
        )
      );


    if (seconds < 60) {
      return (
        seconds
        +
        "s ago"
      );
    }


    const minutes =
      Math.floor(
        seconds / 60
      );


    if (minutes < 60) {
      return (
        minutes
        +
        "m ago"
      );
    }


    const hours =
      Math.floor(
        minutes / 60
      );


    return (
      hours
      +
      "h ago"
    );
  }


  function setText(
    id,
    value,
    fallback
  ) {
    const node =
      byId(id);

    if (!node) {
      return;
    }

    node.textContent =
      text(
        value,
        fallback
      );
  }


  function renderFeedState(
    projection
  ) {
    const feed =
      byId(
        "marketMapFeedState"
      );

    const badge =
      byId(
        "marketMapTruthBadge"
      );


    let label =
      "Feed unavailable";

    let className =
      "unavailable";


    if (
      projection.current_eligible
    ) {
      label =
        "Live · auto-updating";

      className =
        "current";
    }

    else if (
      projection.display_eligible
    ) {
      label =
        (
          "Stale · context only"
        );

      className =
        "stale";
    }


    if (feed) {
      feed.textContent =
        label;
    }


    if (badge) {
      badge.className =
        (
          "market-map-truth-badge "
          +
          className
        );

      badge.textContent =
        label;
    }


    setText(
      "marketMapSource",
      projection.source,
      "source unavailable"
    );

    setText(
      "marketMapAsOf",
      formatDate(
        projection.as_of
      ),
      "not identified"
    );

    setText(
      "marketMapAge",
      relativeAge(
        projection.as_of
      ),
      "unknown"
    );

    setText(
      "marketMapEvidenceProjection",
      projection.projection_status,
      "unavailable"
    );

    setText(
      "marketMapEvidenceCurrent",
      projection.current_eligible
        ? "yes"
        : "no",
      "no"
    );

    setText(
      "marketMapEvidenceDisplay",
      projection.display_eligible
        ? "yes"
        : "no",
      "no"
    );

    setText(
      "marketMapEvidenceEvent",
      latestFeedEventAt
        ? formatDate(
            latestFeedEventAt
          )
        : "not observed yet",
      "not observed yet"
    );

    setText(
      "marketMapEvidenceReason",
      projection.reason,
      "No canonical projection explanation supplied."
    );
  }


  function renderSoulaana(
    contract,
    projection,
    changeText
  ) {
    const api =
      window.OB_MARKET_MAP_SOULAANA_OBUX033;


    if (
      !api
      ||
      typeof api.explain !== "function"
    ) {
      return;
    }


    const reading =
      api.explain(
        contract,
        projection,
        changeText
      );


    setText(
      "marketMapWhatISee",
      reading.what_i_see,
      "I do not have enough verified context yet."
    );

    setText(
      "marketMapWhatItMeans",
      reading.what_it_means,
      "No interpretation available."
    );

    setText(
      "marketMapWhatChanged",
      reading.what_changed,
      "No verified change statement available."
    );

    setText(
      "marketMapNeedsYou",
      reading.what_needs_you,
      "Nothing needs attention."
    );

    setText(
      "marketMapCanWait",
      reading.what_can_wait,
      "Background context can wait."
    );

    setText(
      "marketMapNextMove",
      reading.next_best_move,
      "No move required."
    );


    const noAction =
      byId(
        "marketMapNoAction"
      );

    if (noAction) {
      noAction.hidden =
        !reading.no_action_needed;
    }
  }


  function positionPoint(
    index,
    total,
    seed
  ) {
    const safeTotal =
      Math.max(
        1,
        total
      );


    const angle =
      (
        (
          360
          /
          safeTotal
        )
        *
        index
        +
        seed * 29
        -
        90
      )
      *
      Math.PI
      /
      180;


    const ring =
      (
        index % 3 === 0
      )
        ? 25
        : (
            index % 3 === 1
              ? 34
              : 42
          );


    return {
      x:
        Math.max(
          7,
          Math.min(
            93,
            50
            +
            Math.cos(angle)
            *
            ring
          )
        ),

      y:
        Math.max(
          10,
          Math.min(
            90,
            50
            +
            Math.sin(angle)
            *
            ring
            *
            0.72
          )
        ),
    };
  }


  function flagsFor(
    symbol,
    sets
  ) {
    return {
      position:
        sets.positions.has(
          symbol
        ),

      signal:
        sets.signals.has(
          symbol
        ),

      candidate:
        sets.candidates.has(
          symbol
        ),

      watch:
        sets.watchlist.has(
          symbol
        ),
    };
  }


  function openSymbol(symbol) {
    if (!symbol) {
      return;
    }


    window.location.assign(
      (
        "/ob/symbol/"
        +
        encodeURIComponent(
          symbol
        )
      )
    );
  }


  function createStar(
    symbolObject,
    index,
    total,
    seed,
    sets
  ) {
    const symbol =
      symbolFrom(
        symbolObject
      );


    const point =
      positionPoint(
        index,
        total,
        seed
      );


    const flags =
      flagsFor(
        symbol,
        sets
      );


    const button =
      document.createElement(
        "button"
      );


    button.type =
      "button";

    button.className =
      "market-map-star";


    if (flags.position) {
      button.classList.add(
        "position"
      );
    }

    else if (flags.signal) {
      button.classList.add(
        "signal"
      );
    }

    else if (flags.candidate) {
      button.classList.add(
        "candidate"
      );
    }

    else if (flags.watch) {
      button.classList.add(
        "watch"
      );
    }


    button.style.setProperty(
      "--x",
      point.x + "%"
    );

    button.style.setProperty(
      "--y",
      point.y + "%"
    );


    button.setAttribute(
      "aria-label",
      (
        symbol
        +
        " · open source-backed Symbol Page"
      )
    );


    button.addEventListener(
      "click",
      function () {
        openSymbol(
          symbol
        );
      }
    );


    const label =
      document.createElement(
        "span"
      );

    label.className =
      "market-map-star-label";

    label.style.setProperty(
      "--x",
      point.x + "%"
    );

    label.style.setProperty(
      "--y",
      point.y + "%"
    );

    label.textContent =
      symbol;


    return {
      button,
      label,
    };
  }


  function sectorSymbols(sector) {
    return safeArray(
      safeObject(
        sector
      ).symbols
    )
      .filter(
        item =>
          Boolean(
            symbolFrom(
              item
            )
          )
      );
  }


  function addMeta(
    mount,
    value
  ) {
    if (
      value === null
      ||
      value === undefined
      ||
      value === ""
    ) {
      return;
    }


    const node =
      document.createElement(
        "span"
      );

    node.textContent =
      String(value);

    mount.appendChild(
      node
    );
  }


  function createConstellation(
    sector,
    sectorIndex,
    sets
  ) {
    const safe =
      safeObject(
        sector
      );

    const symbols =
      sectorSymbols(
        safe
      );


    const card =
      document.createElement(
        "article"
      );

    card.className =
      "market-map-constellation";


    const head =
      document.createElement(
        "div"
      );

    head.className =
      "market-map-constellation-head";


    const title =
      document.createElement(
        "div"
      );

    title.className =
      "market-map-constellation-title";


    const strong =
      document.createElement(
        "strong"
      );

    strong.textContent =
      text(
        safe.name
        ||
        safe.sector,
        "Unnamed source sector"
      );


    const sub =
      document.createElement(
        "span"
      );

    sub.textContent =
      text(
        safe.constellationName,
        (
          symbols.length
          +
          " source-backed symbol"
          +
          (
            symbols.length === 1
              ? ""
              : "s"
          )
        )
      );


    title.appendChild(
      strong
    );

    title.appendChild(
      sub
    );


    const meta =
      document.createElement(
        "div"
      );

    meta.className =
      "market-map-sector-meta";


    // Display only explicit projected attributes.
    addMeta(
      meta,
      safe.strength
    );

    addMeta(
      meta,
      safe.mood
    );

    addMeta(
      meta,
      safe.crowding
    );


    head.appendChild(
      title
    );

    head.appendChild(
      meta
    );


    const field =
      document.createElement(
        "div"
      );

    field.className =
      "market-map-star-field";


    symbols.forEach(
      function (
        symbolObject,
        index
      ) {
        const star =
          createStar(
            symbolObject,
            index,
            symbols.length,
            sectorIndex + 1,
            sets
          );

        field.appendChild(
          star.button
        );

        field.appendChild(
          star.label
        );
      }
    );


    card.appendChild(
      head
    );

    card.appendChild(
      field
    );


    return card;
  }


  function renderEmptySky(
    mount,
    projection
  ) {
    const wrapper =
      document.createElement(
        "div"
      );

    wrapper.className =
      "market-map-empty";


    const inner =
      document.createElement(
        "div"
      );

    inner.className =
      "market-map-empty-inner";


    const orbit =
      document.createElement(
        "div"
      );

    orbit.className =
      "market-map-empty-orbit";


    const title =
      document.createElement(
        "h3"
      );

    title.textContent =
      "The sky is staying quiet.";


    const body =
      document.createElement(
        "p"
      );

    body.textContent =
      text(
        projection.reason,
        (
          "No source-backed Market Map is available. "
          +
          "OB will not invent stars, sectors, or opportunities."
        )
      );


    inner.appendChild(
      orbit
    );

    inner.appendChild(
      title
    );

    inner.appendChild(
      body
    );

    wrapper.appendChild(
      inner
    );

    mount.appendChild(
      wrapper
    );
  }


  function renderSky(
    contract,
    projection
  ) {
    const mount =
      byId(
        "marketMapSky"
      );

    if (!mount) {
      return;
    }


    mount.replaceChildren();


    const sectors =
      safeArray(
        contract.sectors
      );


    const sets =
      evidenceSets(
        contract
      );


    if (
      !projection.display_eligible
      ||
      !sectors.length
    ) {
      renderEmptySky(
        mount,
        projection
      );

      return;
    }


    sectors.forEach(
      function (
        sector,
        index
      ) {
        mount.appendChild(
          createConstellation(
            sector,
            index,
            sets
          )
        );
      }
    );
  }


  function renderAttention(
    contract
  ) {
    const mount =
      byId(
        "marketMapAttention"
      );

    if (!mount) {
      return;
    }


    mount.replaceChildren();


    const cards = [
      {
        name:
          "Open positions",

        value:
          safeArray(
            contract.open_positions
          ).length,

        meaning:
          "Already exposed to the market. Review before hunting for more.",
      },

      {
        name:
          "Signals",

        value:
          safeArray(
            contract.signals
          ).length,

        meaning:
          "Source-backed attention records. Attention is not permission.",
      },

      {
        name:
          "Candidates",

        value:
          safeArray(
            contract.candidates
          ).length,

        meaning:
          "Projected candidates that may deserve a deeper Symbol Page read.",
      },

      {
        name:
          "Watchlist",

        value:
          safeArray(
            contract.watchlist
          ).length,

        meaning:
          "Background watch context that can wait until evidence changes.",
      },
    ];


    cards.forEach(
      function (item) {
        const card =
          document.createElement(
            "article"
          );

        card.className =
          "market-map-attention-card";


        const name =
          document.createElement(
            "span"
          );

        name.textContent =
          item.name;


        const value =
          document.createElement(
            "strong"
          );

        value.textContent =
          String(
            item.value
          );


        const meaning =
          document.createElement(
            "p"
          );

        meaning.textContent =
          item.meaning;


        card.appendChild(
          name
        );

        card.appendChild(
          value
        );

        card.appendChild(
          meaning
        );

        mount.appendChild(
          card
        );
      }
    );
  }


  function renderCountLabel(
    contract
  ) {
    setText(
      "marketMapCountLabel",
      (
        safeArray(
          contract.sectors
        ).length
        +
        " sector groups · "
        +
        safeArray(
          contract.symbols
        ).length
        +
        " source-backed symbols"
      ),
      "no market groups"
    );
  }


  function render(
    reason
  ) {
    const contract =
      marketMapContract();


    const projection =
      canonicalProjection();


    const currentSnapshot =
      snapshotOf(
        contract,
        projection
      );


    const changeText =
      describeChange(
        previousSnapshot,
        currentSnapshot
      );


    renderFeedState(
      projection
    );

    renderSoulaana(
      contract,
      projection,
      changeText
    );

    renderSky(
      contract,
      projection
    );

    renderAttention(
      contract
    );

    renderCountLabel(
      contract
    );


    previousSnapshot =
      currentSnapshot;


    return {
      reason:
        reason
        ||
        "manual-render",

      contract,
      projection,
      changeText,
    };
  }


  function handleCanonicalFeedUpdate() {
    latestFeedEventAt =
      new Date().toISOString();


    // IMPORTANT:
    // do not trust a copied event payload as room truth.
    // Reread the canonical room contract and adapter projection.
    render(
      "obEngineFeedAdapterUpdated"
    );
  }


  function refreshRelativeAgeOnly() {
    const projection =
      canonicalProjection();


    setText(
      "marketMapAge",
      relativeAge(
        projection.as_of
      ),
      "unknown"
    );
  }


  function boot() {
    render(
      "initial-load"
    );


    window.addEventListener(
      "obEngineFeedAdapterUpdated",
      handleCanonicalFeedUpdate
    );


    // UI clock only.
    // This does NOT fetch data and is not a market polling loop.
    relativeAgeTimer =
      window.setInterval(
        refreshRelativeAgeOnly,
        5000
      );
  }


  if (
    document.readyState === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot,
      {
        once: true,
      }
    );
  }

  else {
    boot();
  }


  window.OB_MARKET_MAP_OBUX031_035 = {
    version:
      VERSION,

    render,

    marketMapContract,

    canonicalProjection,

    handleCanonicalFeedUpdate,

    safety: {
      independent_market_fetch:
        false,

      independent_market_polling:
        false,

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
    },
  };
})();
