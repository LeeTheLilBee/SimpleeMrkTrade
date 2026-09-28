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

  let focusedRegion = null;
  let focusedRegionKey = null;
  let selectedSymbol = null;


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


  // Stable layout hashes have NO market-data meaning.
  function skyUnit(value) {
    let hash = 2166136261;
    const raw = String(value || "");
    for (let i = 0; i < raw.length; i += 1) {
      hash ^= raw.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0) / 4294967295;
  }

  function positionPoint(index, total, seed, symbol) {
    const key = seed + ":" + symbol;
    const angle = (index * 137.507764 + skyUnit(key) * 115 + seed * 41)
      * Math.PI / 180;
    const radius = 11 + Math.sqrt((index + 1) / (Math.max(total, 1) + 1))
      * 27 + skyUnit(key + ":distance") * 7;
    return {
      x: Math.max(9, Math.min(91, 50 + Math.cos(angle) * radius)),
      y: Math.max(12, Math.min(88, 50 + Math.sin(angle) * radius * 0.72)),
    };
  }

  function regionPlacement(index, total, key) {
    const columns = Math.max(1, Math.min(4, Math.ceil(Math.sqrt(total * 1.6))));
    const rows = Math.ceil(total / columns);
    const cellW = 100 / columns;
    const cellH = 100 / rows;
    const dx = (skyUnit(key + ":x") - 0.5) * cellW * 0.12;
    const dy = (skyUnit(key + ":y") - 0.5) * cellH * 0.12;
    return {
      x: Math.max(0, (index % columns) * cellW + dx + cellW * 0.035),
      y: Math.max(0, Math.floor(index / columns) * cellH + dy + cellH * 0.025),
      width: cellW * 0.93,
      height: cellH * 0.95,
    };
  }

  // This spotlight only interprets existing marketMapContract membership.
  function showWholeSky() {
    focusedRegion = null;
    focusedRegionKey = null;
    selectedSymbol = null;
    applySkyFocus();
    const drawer = byId("marketMapFocus");
    if (drawer) drawer.hidden = true;
    const open = byId("marketMapFocusOpen");
    if (open) open.hidden = true;
  }

  function applySkyFocus() {
    const mount = byId("marketMapSky");
    if (!mount) return;
    mount.querySelectorAll(".market-map-constellation").forEach(function (card) {
      const match = focusedRegion !== null
        && Number(card.dataset.regionIndex) === focusedRegion;
      card.classList.toggle("is-focused", match);
      card.classList.toggle("is-muted", focusedRegion !== null && !match);
      const btn = card.querySelector(".market-map-region-button");
      if (btn) btn.setAttribute("aria-pressed", match ? "true" : "false");
    });
    const reset = byId("marketMapReset");
    if (reset) reset.hidden = focusedRegion === null;
  }

  function focusRegion(index, name, count, sector) {
    focusedRegion = index;
    focusedRegionKey = name;
    selectedSymbol = null;
    applySkyFocus();
    const drawer = byId("marketMapFocus");
    if (!drawer) return;
    drawer.hidden = false;
    const projected = safeObject(sector);
    const meta = [projected.strength, projected.mood, projected.crowding]
      .filter(value => value !== null && value !== undefined && value !== "")
      .map(String);
    setText("marketMapFocusTitle", name, "Source sector");
    setText("marketMapFocusDescription",
      count + " source-backed symbols. "
      + (meta.length ? "Projected context: " + meta.join(" · ") + ". " : "")
      + "Location and nebula color are presentation, not performance.");
    const open = byId("marketMapFocusOpen");
    if (open) open.hidden = true;
  }

  function spotlightSymbol(symbol, index, regionName, flags) {
    focusedRegion = index;
    focusedRegionKey = regionName;
    selectedSymbol = symbol;
    applySkyFocus();
    const drawer = byId("marketMapFocus");
    if (!drawer) return;
    drawer.hidden = false;
    const labels = [
      flags.position && "Position",
      flags.signal && "Signal",
      flags.candidate && "Candidate",
      flags.watch && "Saved",
    ].filter(Boolean);
    setText("marketMapFocusTitle", symbol, "Symbol");
    setText("marketMapFocusDescription",
      "Source region: " + regionName + ". "
      + (labels.length ? "Explicit membership: " + labels.join(" · ") + ". "
        : "No special membership asserted. ")
      + "Choose Open Symbol Page for canonical details. No trade happens here.");
    const open = byId("marketMapFocusOpen");
    if (open) open.hidden = false;
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
    sets,
    sectorIndex,
    regionName
  ) {
    const symbol =
      symbolFrom(
        symbolObject
      );


    const point =
      positionPoint(
        index,
        total,
        seed,
        symbol
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
        " · select source-backed star for spotlight"
      )
    );


    button.addEventListener(
      "click",
      function () {
        spotlightSymbol(symbol, sectorIndex, regionName, flags);
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
    sets,
    sectorTotal
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

    card.className = "market-map-constellation";
    card.dataset.regionIndex = String(sectorIndex);
    const name = text(safe.name || safe.sector, "Unnamed source sector");
    const placement = regionPlacement(sectorIndex, sectorTotal, name);
    card.style.setProperty("--region-x", placement.x + "%");
    card.style.setProperty("--region-y", placement.y + "%");
    card.style.setProperty("--region-width", placement.width + "%");
    card.style.setProperty("--region-height", placement.height + "%");
    card.style.setProperty("--nebula-hue", String(177 + Math.round(skyUnit(name) * 32)));


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


    const explore = document.createElement("button");
    explore.type = "button";
    explore.className = "market-map-region-button";
    explore.textContent = "Explore region";
    explore.setAttribute("aria-label", "Explore source sector " + name);
    explore.setAttribute("aria-pressed", "false");
    explore.addEventListener("click", function () {
      focusRegion(sectorIndex, name, symbols.length, safe);
    });
    title.appendChild(explore);
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
            sets,
            sectorIndex,
            name
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
      showWholeSky();
      renderEmptySky(
        mount,
        projection
      );

      return;
    }


    // Retain the same *named* region across canonical reorder; never focus the wrong sector.
    if (focusedRegionKey !== null) {
      const actual = sectors.findIndex(function (sector) {
        const source = safeObject(sector);
        return text(source.name || source.sector, "Unnamed source sector") === focusedRegionKey;
      });
      if (actual < 0) showWholeSky();
      else focusedRegion = actual;
    }
    const columns = Math.max(1, Math.min(4, Math.ceil(Math.sqrt(sectors.length * 1.6))));
    const rows = Math.ceil(sectors.length / columns);
    mount.style.setProperty("--sky-height", Math.max(760, rows * 276) + "px");
    sectors.forEach(function (sector, index) {
      mount.appendChild(createConstellation(sector, index, sets, sectors.length));
    });
    if (focusedRegion !== null && focusedRegion >= sectors.length) {
      showWholeSky();
    } else if (focusedRegion !== null) {
      const sector = safeObject(sectors[focusedRegion]);
      const name = text(sector.name || sector.sector, "Unnamed source sector");
      const objects = sectorSymbols(sector);
      const found = selectedSymbol && objects.some(item => symbolFrom(item) === selectedSymbol);
      if (found) spotlightSymbol(selectedSymbol, focusedRegion, name, flagsFor(selectedSymbol, sets));
      else focusRegion(focusedRegion, name, objects.length, sector);
    }
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
    const reset = byId("marketMapReset");
    const drawerReset = byId("marketMapFocusReset");
    const open = byId("marketMapFocusOpen");
    if (reset) reset.addEventListener("click", showWholeSky);
    if (drawerReset) drawerReset.addEventListener("click", showWholeSky);
    if (open) open.addEventListener("click", function () {
      if (selectedSymbol) openSymbol(selectedSymbol);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && focusedRegion !== null) showWholeSky();
    });
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
