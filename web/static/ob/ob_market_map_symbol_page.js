// OBSERVATORY_MARKET_MAP_V10_APP_JS
// OBSERVATORY_SYMBOL_PAGE_V12_REAL_ROUTE_HANDOFF
const sectors = window.OB_MARKET_DATA.sectors;

const skyField = document.getElementById("skyField");
const detailPanel = document.getElementById("detailPanel");

function layoutPoints(count, seed, mode) {
  const points = [];
  const centerX = 50;
  const centerY = 50;

  if (count === 1) return [{ x: centerX, y: centerY }];

  if (mode === "small") {
    const radiusX = 34;
    const radiusY = 27;
    const offset = seed * 19;
    for (let i = 0; i < count; i++) {
      const angle = ((360 / count) * i + offset - 90) * Math.PI / 180;
      points.push({
        x: centerX + Math.cos(angle) * radiusX,
        y: centerY + Math.sin(angle) * radiusY
      });
    }
    return points;
  }

  const innerCount = count > 6 ? 3 : Math.min(2, count);
  const outerCount = count - innerCount;
  const offset = seed * 13;

  for (let i = 0; i < innerCount; i++) {
    const angle = ((360 / innerCount) * i + offset - 90) * Math.PI / 180;
    points.push({
      x: centerX + Math.cos(angle) * 18,
      y: centerY + Math.sin(angle) * 14
    });
  }

  for (let i = 0; i < outerCount; i++) {
    const angle = ((360 / outerCount) * i + offset + 25 - 90) * Math.PI / 180;
    points.push({
      x: centerX + Math.cos(angle) * 39,
      y: centerY + Math.sin(angle) * 30
    });
  }

  return points;
}

function starClassByTier(tier) {
  if (tier === "hot") return "hot";
  if (tier === "watch") return "watch";
  if (tier === "blocked") return "blocked";
  return "background";
}

function sectorGlow(strength) {
  if (strength === "Strong") return "var(--ob-green)";
  if (strength === "Weak") return "var(--ob-red)";
  return "var(--ob-gold)";
}

function sectorShadow(strength) {
  if (strength === "Strong") return "0 0 18px rgba(101,242,118,0.70)";
  if (strength === "Weak") return "0 0 16px rgba(255,87,87,0.45)";
  return "0 0 16px rgba(233,194,111,0.55)";
}

function statusFromTier(tier) {
  if (tier === "hot") return "Brightening Watch";
  if (tier === "watch") return "Guarded Watch";
  if (tier === "blocked") return "Blocked / Gated";
  return "Background Star";
}

function starTypeFromTier(tier) {
  if (tier === "hot") return "Green-Gold Active Star";
  if (tier === "watch") return "Gold-Aqua Watch Star";
  if (tier === "blocked") return "Red-Gold Gated Star";
  return "Dim Background Star";
}



function soulaanaDeepRead(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      lead: "Okay, this star is talking. Not whispering. Talking. But I need you to hear me clearly: bright does not mean automatic. Bright means we slow down, inspect the reason, and make sure the glow is earned.",
      tone: "Warm but strict",
      truth: "The setup has attention, but attention is not permission.",
      warning: "Do not let a strong sector make you sloppy. Crowding can dress itself up like confidence.",
      decision: "Review it like it matters, because it does. But do not chase it like you are scared to miss it.",
      boundary: "If permission, risk, or movement stops lining up, OB should dim this star before you ever touch a trade.",
      steps: [
        ["Read the star", "Check why it brightened and whether the reason still makes sense."],
        ["Check the boundary", "Confirm Tower permission, risk glow, and live-lock state before any action."],
        ["Respect the movement", "Let the price or premium path keep proving itself. No chasing."],
        ["Move clean", "If it is valid, take it through Trade Center. If not, leave it alone."]
      ]
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      lead: "This one is leaning forward, but it has not stepped into the light yet. I like that OB is watching it, but I do not like rushing a star before it proves itself.",
      tone: "Patient and watchful",
      truth: "A forming setup is not the same thing as an approved setup.",
      warning: "The danger here is acting early because you want to be first. First is not the goal. Clean is the goal.",
      decision: "Keep it on watch. Let the next movement confirm whether this star deserves more attention.",
      boundary: "If volume fades, sector support weakens, or permission stays limited, this remains a watch item only.",
      steps: [
        ["Watch the glow", "See if the star brightens or fades from here."],
        ["Wait for confirmation", "Do not upgrade it until movement gets cleaner."],
        ["Check risk", "Make sure risk is not rising while the signal is forming."],
        ["Stay patient", "No forcing. If it is real, it will survive review."]
      ]
    };
  }

  return {
    lead: "This one is quiet. And quiet is not bad, but quiet is not a command either. OB can keep it in the sky without making it the center of your attention.",
    tone: "Calm and protective",
    truth: "This star is context, not action.",
    warning: "The danger is getting bored and trying to make a quiet symbol interesting.",
    decision: "Leave it in the background until it earns a brighter state.",
    boundary: "No trade context should open unless the symbol brightens, the sector improves, or OB finds a real reason.",
    steps: [
      ["Leave it alone", "Do not force a quiet star into the action lane."],
      ["Watch the sector", "A background star can matter later if its constellation changes."],
      ["Wait for a reason", "No reason means no action."],
      ["Protect attention", "Your focus belongs where the signal is cleaner."]
    ]
  };
}

function symbolNarrative(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      sees: symbolObj.symbol + " is brightening inside " + sector.constellationName + ". The symbol is not just present. It is asking for attention.",
      means: "OB sees strength, participation, and enough movement to justify a closer read. This is a watch-first situation, not a chase-first situation.",
      careful: "The danger is excitement. A bright star can still get pulled down if the constellation gets crowded or the broader market cools.",
      next: "Open the trade context only if permission, risk, and movement stay aligned. Let the signal keep proving itself."
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      sees: symbolObj.symbol + " is forming, but it is not fully lit yet. It is on the edge of attention.",
      means: "OB is tracking the symbol because something is developing, but it has not earned full confidence.",
      careful: "The danger is acting early. Early interest can look like conviction before it has enough confirmation.",
      next: "Keep it on watch. Wait for cleaner follow-through before treating it like an action-ready star."
    };
  }

  return {
    sees: symbolObj.symbol + " is visible in the sky, but it is not leading the move.",
    means: "OB keeps it in the background for context. It may matter later, but right now it is not the priority.",
    careful: "The danger is forcing attention onto a quiet symbol because you want action.",
    next: "Leave it alone until it brightens or the sector changes."
  };
}

function whyOBCards(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      setup: "Active star behavior",
      sector: sector.name + " is supporting the move",
      behavior: "Strength is visible without needing to force the read",
      permission: symbolObj.permission
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      setup: "Developing watch signal",
      sector: sector.name + " is being monitored for confirmation",
      behavior: "Movement is forming but not fully trusted yet",
      permission: symbolObj.permission
    };
  }

  return {
    setup: "Background context only",
    sector: sector.name + " does not make this symbol a priority yet",
    behavior: "No clear leadership from this star",
    permission: symbolObj.permission
  };
}

function soulaanaSymbolRead(sector, symbolObj) {
  if (symbolObj.tier === "hot") {
    return `
      Now look at this one carefully. ${symbolObj.symbol} is bright for a reason, but bright does not mean reckless.
      OB is watching because the ${sector.constellationName} is active and this star is carrying attention.
      That means we respect it, not chase it. Check the permission, check the risk, and let the signal keep proving itself.
    `;
  }

  if (symbolObj.tier === "watch") {
    return `
      This one has something, but it has not earned full trust yet. OB is watching, not rushing.
      A watched star can become important, but only if the movement gets cleaner and the risk stays controlled.
      Do not force it just because it is close to the action.
    `;
  }

  return `
    This star is in the sky, but it is not leading the story right now.
    OB keeps it visible for context, not action. Let it stay quiet until it proves it deserves more attention.
  `;
}

function renderDefaultDetail() {
  detailPanel.innerHTML = `
    <div class="detail-title">Select a constellation</div>
    <div class="detail-sub">Click a sector to pull the constellation forward.</div>

    <div class="detail-row">
      <span>Brightest stars</span>
      <strong>On OB radar</strong>
    </div>

    <div class="detail-row">
      <span>Dim stars</span>
      <strong>Background symbols</strong>
    </div>

    <div class="detail-row">
      <span>Click path</span>
      <strong>Constellation -> Star -> Symbol Page</strong>
    </div>

    <div class="fun-facts">
      <strong style="color: var(--ob-purple);">Soulaana:</strong><br>
      Do not try to read the whole sky at once. Pick the brightest constellation, then inspect the cleanest star.
    </div>
  `;
}

function renderSky() {
  skyField.innerHTML = `<div class="constellation-grid"></div>`;
  const grid = skyField.querySelector(".constellation-grid");

  sectors.forEach((sector, sIndex) => {
    const card = document.createElement("div");
    card.className = "constellation-card";

    const space = document.createElement("div");
    space.className = "constellation-space";

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "constellation-line-small");

    const previewSymbols = sector.symbols.slice(0, 6);
    const points = layoutPoints(previewSymbols.length, sIndex + 2, "small");

    points.forEach((p, i) => {
      if (i > 0) {
        const prev = points[i - 1];
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", prev.x + "%");
        line.setAttribute("y1", prev.y + "%");
        line.setAttribute("x2", p.x + "%");
        line.setAttribute("y2", p.y + "%");
        svg.appendChild(line);
      }
    });

    space.appendChild(svg);

    points.forEach((p, i) => {
      const star = document.createElement("div");
      star.className = "constellation-star";
      star.style.top = p.y + "%";
      star.style.left = p.x + "%";
      star.style.background = sectorGlow(sector.strength);
      star.style.boxShadow = sectorShadow(sector.strength);
      star.style.animationDelay = (i * 0.24) + "s";
      space.appendChild(star);
    });

    card.appendChild(space);

    const sectorName = document.createElement("div");
    sectorName.className = "sector-name";
    sectorName.textContent = sector.name;
    card.appendChild(sectorName);

    const constellationName = document.createElement("div");
    constellationName.className = "constellation-name";
    constellationName.textContent = sector.constellationName;
    card.appendChild(constellationName);

    card.onclick = () => renderSectorZoom(sector);
    grid.appendChild(card);
  });

  renderDefaultDetail();
}

function renderSectorZoom(sector) {
  skyField.innerHTML = `
    <div class="zoom-stage">
      <div class="zoom-title-row">
        <div>
          <div class="detail-title">${sector.name}</div>
          <div class="detail-sub">${sector.constellationName} · ${sector.strength}</div>
        </div>
        <button class="back-button" id="backToSky">Back to sky</button>
      </div>
      <div class="zoom-constellation" id="zoomConstellation">
        <svg class="zoom-lines" id="zoomLines"></svg>
      </div>
    </div>
  `;

  document.getElementById("backToSky").onclick = renderSky;

  const field = document.getElementById("zoomConstellation");
  const svg = document.getElementById("zoomLines");
  const points = layoutPoints(sector.symbols.length, sector.name.length + 5, "zoom");

  points.forEach((p, i) => {
    if (i > 0) {
      const prev = points[i - 1];
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", prev.x + "%");
      line.setAttribute("y1", prev.y + "%");
      line.setAttribute("x2", p.x + "%");
      line.setAttribute("y2", p.y + "%");
      svg.appendChild(line);
    }
  });

  sector.symbols.forEach((symbolObj, i) => {
    const p = points[i];

    const star = document.createElement("div");
    star.className = "symbol-star " + starClassByTier(symbolObj.tier);
    star.style.top = p.y + "%";
    star.style.left = p.x + "%";
    star.title = symbolObj.symbol + " · " + symbolObj.starName;
    star.onclick = () => { window.location.href = '/ob/symbol/' + encodeURIComponent(symbolObj.symbol); };

    const label = document.createElement("div");
    label.className = "symbol-label";
    label.style.top = p.y + "%";
    label.style.left = p.x + "%";
    label.textContent = symbolObj.symbol;

    field.appendChild(star);
    field.appendChild(label);
  });

  renderSectorDetail(sector);
}

function getSectorByName(name) {
  return sectors.find(s => s.name === name);
}

function getSymbolInSector(sector, symbol) {
  return sector.symbols.find(s => s.symbol === symbol);
}

function renderSectorDetail(sector) {
  const hotStars = sector.symbols.filter(s => s.tier === "hot").map(s => s.symbol).join(", ") || "None right now";
  const watchStars = sector.symbols.filter(s => s.tier === "watch").map(s => s.symbol).join(", ") || "None right now";

  detailPanel.innerHTML = `
    <div class="detail-title">${sector.name}</div>
    <div class="detail-sub">${sector.constellationName}</div>

    <div class="detail-row">
      <span>Sector strength</span>
      <strong>${sector.strength}</strong>
    </div>

    <div class="detail-row">
      <span>Brightest stars</span>
      <strong>${hotStars}</strong>
    </div>

    <div class="detail-row">
      <span>Watching</span>
      <strong>${watchStars}</strong>
    </div>

    <div class="fun-facts">
      <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
      ${sector.read}
    </div>

    <div class="fun-facts">
      Bright stars are active watch names. Dim stars are still present, but they are not the priority unless they start glowing.
    </div>
  `;
}




function tradeContextData(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      status: "Needs owner review",
      strategy: "Momentum continuation",
      confidence: "82",
      actionWindow: "20 minutes",
      direction: "Bullish watch",
      asset: symbolObj.tradeType,
      contract: symbolObj.symbol + " next monthly call",
      entry: "Review entry zone before action",
      stop: "Premium-based stop required",
      target: "Target zone only if movement confirms",
      risk: "Moderate",
      blocker: "Live automated locked. Manual review only.",
      soulaana: "This is where we slow down on purpose. A good-looking setup still has to pass risk, permission, and movement checks. If it cannot survive review, it was not clean enough.",
      doNot: [
        "Do not place if spread is too wide.",
        "Do not place if price moved above the review zone.",
        "Do not place if sector crowding turns orange.",
        "Do not place if Tower permission changes."
      ]
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      status: "Watch only",
      strategy: "Developing setup",
      confidence: "61",
      actionWindow: "No action window yet",
      direction: "Needs confirmation",
      asset: symbolObj.tradeType,
      contract: "No order ticket yet",
      entry: "Wait for confirmation",
      stop: "Not assigned",
      target: "Not assigned",
      risk: "Guarded",
      blocker: "Signal is not action-ready.",
      soulaana: "Attention is not permission. This one can stay on the board, but it does not get a trade card until it proves itself cleaner.",
      doNot: [
        "Do not force an early entry.",
        "Do not upgrade without follow-through.",
        "Do not treat watch status like approval.",
        "Do not ignore risk just because the sector is interesting."
      ]
    };
  }

  return {
    status: "Background only",
    strategy: "No active setup",
    confidence: "32",
    actionWindow: "None",
    direction: "No clear leadership",
    asset: symbolObj.tradeType,
    contract: "No order ticket",
    entry: "No entry",
    stop: "No stop",
    target: "No target",
    risk: "No action priority",
    blocker: "Background star. No trade context should open for action.",
    soulaana: "This is not where we spend energy right now. Let it stay in the sky. It can earn attention later.",
    doNot: [
      "Do not manufacture a setup.",
      "Do not open action just because it is visible.",
      "Do not confuse context with opportunity.",
      "Do not override the star state."
    ]
  };
}

function recordTradeContextAction(symbol, action) {
  const receipt = document.getElementById("tradeContextReceipt");
  if (!receipt) return;

  const now = new Date().toLocaleString();

  receipt.innerHTML = `
    <strong>Receipt updated:</strong><br>
    Symbol: ${symbol}<br>
    Action: ${action}<br>
    Time: ${now}<br>
    Execution responsibility: Owner at brokerage only if later approved.<br>
    OB status: ${action === "Approve for manual placement" ? "Awaiting broker checklist review" : action}
  `;
}

function openTradeContext(sectorName, symbol) {
  const sector = getSectorByName(sectorName);
  const symbolObj = getSymbolInSector(sector, symbol);
  const context = tradeContextData(symbolObj, sector);

  detailPanel.innerHTML = `
    <button class="back-button" onclick="openSymbolPage('${sectorName}', '${symbol}')">Back to Symbol</button>

    <div style="height: 14px;"></div>

    <div class="detail-title">Trade Context</div>
    <div class="detail-sub">${symbolObj.symbol} · ${symbolObj.starName}</div>

    <div class="trade-context-shell">
      <div class="trade-context-card gold">
        <span>Status</span>
        <strong>${context.status}</strong>
      </div>

      <div class="trade-context-card green">
        <span>Strategy</span>
        <strong>${context.strategy} · Confidence ${context.confidence}</strong>
      </div>

      <div class="trade-context-card">
        <span>Direction / asset</span>
        <strong>${context.direction} · ${context.asset}</strong>
      </div>

      <div class="trade-context-card red">
        <span>Blocker</span>
        <strong>${context.blocker}</strong>
      </div>

      <div class="ticket-box">
        <div class="ticket-line">
          <span>Contract</span>
          <strong>${context.contract}</strong>
        </div>
        <div class="ticket-line">
          <span>Entry</span>
          <strong>${context.entry}</strong>
        </div>
        <div class="ticket-line">
          <span>Stop</span>
          <strong>${context.stop}</strong>
        </div>
        <div class="ticket-line">
          <span>Target</span>
          <strong>${context.target}</strong>
        </div>
        <div class="ticket-line">
          <span>Window</span>
          <strong>${context.actionWindow}</strong>
        </div>
      </div>

      <div class="fun-facts">
        <strong style="color: var(--ob-purple);">Soulaana:</strong><br>
        ${context.soulaana}
      </div>

      <div class="trade-context-card red">
        <span>Do not place if</span>
        <strong>
          ${context.doNot.map(item => "• " + item).join("<br>")}
        </strong>
      </div>

      <div class="trade-context-actions">
        <button class="trade-context-button" onclick="recordTradeContextAction('${symbolObj.symbol}', 'Approve for manual placement')">
          Approve for manual placement
        </button>

        <button class="trade-context-button reject" onclick="recordTradeContextAction('${symbolObj.symbol}', 'Rejected')">
          Reject
        </button>

        <button class="trade-context-button watch" onclick="recordTradeContextAction('${symbolObj.symbol}', 'Snooze / watch')">
          Snooze / watch
        </button>
      </div>

      <div class="trade-context-receipt" id="tradeContextReceipt">
        <strong>No receipt yet.</strong><br>
        Choose an action to create a review receipt preview.
      </div>
    </div>
  `;
}

function riskPermissionState(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      riskLevel: "Moderate",
      accountFit: "Paper review allowed",
      crowding: symbolObj.risk,
      duplicate: "Check before action",
      cooldown: "Clear",
      tower: "Tower allows observation and paper review. Live automated remains locked.",
      action: "Review only. Manual or live action requires owner/Tower clearance.",
      classes: ["gold", "green", "gold", "green"]
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      riskLevel: "Guarded",
      accountFit: "Watch first",
      crowding: symbolObj.risk,
      duplicate: "Not action-ready",
      cooldown: "Waiting",
      tower: "Tower keeps this in watch/review territory until the signal confirms.",
      action: "Do not escalate until movement, permission, and risk all improve.",
      classes: ["gold", "gold", "gold", "gold"]
    };
  }

  return {
    riskLevel: "Low action priority",
    accountFit: "Background only",
    crowding: symbolObj.risk,
    duplicate: "No trade context",
    cooldown: "N/A",
    tower: "Tower does not need to open action permissions for a background star.",
    action: "No action. Keep it visible for context only.",
    classes: ["red", "gold", "red", "red"]
  };
}

function movementData(symbolObj) {
  if (symbolObj.tier === "hot") {
    return {
      phase: "Brightening",
      direction: "Upward pressure",
      current: "+4.8%",
      volume: "Above average",
      keyLevel: "Hold above entry zone",
      nextLevel: "Target zone approaching",
      invalidation: "Dims if sector weakens",
      soulaana: "This star is moving with purpose. That does not mean chase it. It means watch whether the move keeps proving itself without getting sloppy."
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      phase: "Forming",
      direction: "Trying to confirm",
      current: "+1.6%",
      volume: "Normal",
      keyLevel: "Needs clean follow-through",
      nextLevel: "Confirmation zone",
      invalidation: "Fails if volume dries up",
      soulaana: "This one is not ready to be trusted yet. It is showing interest, but interest is not permission. Let it confirm before you act like it already won."
    };
  }

  return {
    phase: "Quiet",
    direction: "No clear leadership",
    current: "-0.4%",
    volume: "Light",
    keyLevel: "Background only",
    nextLevel: "Needs to brighten first",
    invalidation: "No action until state changes",
    soulaana: "This star is present, but it is not speaking loudly. Leave it in the background until it earns attention."
  };
}

window.openSymbolPage = function(sectorName, symbol) {
  const sector = getSectorByName(sectorName);
  const symbolObj = getSymbolInSector(sector, symbol);
  const tierClass = starClassByTier(symbolObj.tier);

  skyField.innerHTML = `
    <div class="symbol-room">
      <div class="ob-panel symbol-header">
        <div class="symbol-header-top">
          <div>
            <div class="symbol-ticker">${symbolObj.symbol}</div>
            <div class="symbol-company">${symbolObj.company}</div>
            <div class="detail-sub">${sector.constellationName} · ${statusFromTier(symbolObj.tier)}</div>
          </div>

          <div class="chip-row">
            <span class="ob-chip ob-chip-green">${symbolObj.permission.includes("Paper") ? "Paper Eligible" : "Watch Only"}</span>
            <span class="ob-chip ob-chip-gold">${symbolObj.position}</span>
            <span class="ob-chip ob-chip-red">Live Auto Locked</span>
          </div>
        </div>
      </div>

      <div class="symbol-main-grid">
        <div class="ob-panel main-star-panel">
          <div class="ob-label">Main Symbol Star</div>
          <div class="main-star-stage">
            <div class="mini-orbit-star one"></div>
            <div class="mini-orbit-star two"></div>
            <div class="mini-orbit-star three"></div>
            <div class="symbol-orb ${tierClass}"></div>
          </div>
        </div>

        <div class="ob-panel star-facts-panel">
          <div class="ob-label">Star Facts</div>

          <div class="detail-row">
            <span>Symbol</span>
            <strong>${symbolObj.symbol}</strong>
          </div>

          <div class="detail-row">
            <span>Star Name</span>
            <strong>${symbolObj.starName}</strong>
          </div>

          <div class="detail-row">
            <span>Star Type</span>
            <strong>${starTypeFromTier(symbolObj.tier)}</strong>
          </div>

          <div class="detail-row">
            <span>Market Role</span>
            <strong>${symbolObj.role}</strong>
          </div>

          <div class="detail-row">
            <span>Permission</span>
            <strong>${symbolObj.permission}</strong>
          </div>

          <div class="fun-facts">
            <strong style="color: var(--ob-gold);">Fun fact:</strong><br>
            ${symbolObj.fact}
          </div>
        </div>
      </div>

      <div class="ob-panel soulaana-wide">
        <div class="ob-label">Soulaana · Symbol Read</div>

        <div class="soulaana-wide-text">
          ${soulaanaSymbolRead(sector, symbolObj)}
        </div>

        <div class="soulaana-voice-lead">
          <span>Auntie read</span>
          <p>${soulaanaDeepRead(symbolObj, sector).lead}</p>
        </div>

        <div class="soulaana-tone-row">
          <div class="soulaana-tone-chip gold">Tone: ${soulaanaDeepRead(symbolObj, sector).tone}</div>
          <div class="soulaana-tone-chip green">${soulaanaDeepRead(symbolObj, sector).truth}</div>
          <div class="soulaana-tone-chip red">${soulaanaDeepRead(symbolObj, sector).warning}</div>
        </div>

        <div class="soulaana-guidance-grid">
          <div class="soulaana-beat">
            <span>What she sees</span>
            <p>${symbolNarrative(symbolObj, sector).sees}</p>
          </div>

          <div class="soulaana-beat">
            <span>What it means</span>
            <p>${symbolNarrative(symbolObj, sector).means}</p>
          </div>

          <div class="soulaana-beat">
            <span>Be careful</span>
            <p>${symbolNarrative(symbolObj, sector).careful}</p>
          </div>

          <div class="soulaana-beat">
            <span>Next move</span>
            <p>${symbolNarrative(symbolObj, sector).next}</p>
          </div>
        </div>
      </div>

      <div class="ob-panel soulaana-decision-panel">
        <div class="ob-label">Soulaana · Decision Guidance</div>

        <div class="soulaana-decision-layout">
          <div class="soulaana-script">
            <span>How she wants you to move</span>
            <p>${soulaanaDeepRead(symbolObj, sector).decision}</p>

            <div class="soulaana-boundary">
              <strong>Boundary:</strong><br>
              ${soulaanaDeepRead(symbolObj, sector).boundary}
            </div>
          </div>

          <div class="soulaana-next-stack">
            <div class="soulaana-next-item">
              <div class="soulaana-next-num">1</div>
              <div>
                <strong>${soulaanaDeepRead(symbolObj, sector).steps[0][0]}</strong>
                <p>${soulaanaDeepRead(symbolObj, sector).steps[0][1]}</p>
              </div>
            </div>

            <div class="soulaana-next-item">
              <div class="soulaana-next-num">2</div>
              <div>
                <strong>${soulaanaDeepRead(symbolObj, sector).steps[1][0]}</strong>
                <p>${soulaanaDeepRead(symbolObj, sector).steps[1][1]}</p>
              </div>
            </div>

            <div class="soulaana-next-item">
              <div class="soulaana-next-num">3</div>
              <div>
                <strong>${soulaanaDeepRead(symbolObj, sector).steps[2][0]}</strong>
                <p>${soulaanaDeepRead(symbolObj, sector).steps[2][1]}</p>
              </div>
            </div>

            <div class="soulaana-next-item">
              <div class="soulaana-next-num">4</div>
              <div>
                <strong>${soulaanaDeepRead(symbolObj, sector).steps[3][0]}</strong>
                <p>${soulaanaDeepRead(symbolObj, sector).steps[3][1]}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="symbol-main-grid">
        <div class="ob-panel state-panel">
          <div class="ob-label">Position / Watch State</div>
          <div class="state-grid">
            <div class="state-card">
              <span>Status</span>
              <strong>${symbolObj.position}</strong>
            </div>
            <div class="state-card">
              <span>Asset Type</span>
              <strong>${symbolObj.tradeType}</strong>
            </div>
            <div class="state-card">
              <span>Current State</span>
              <strong>${statusFromTier(symbolObj.tier)}</strong>
            </div>
            <div class="state-card">
              <span>Risk Glow</span>
              <strong>${symbolObj.risk}</strong>
            </div>
          </div>
        </div>

        <div class="ob-panel state-panel why-ob-panel">
          <div class="ob-label">Why OB Is Watching</div>
          <div class="fun-facts">
            ${symbolObj.why}
          </div>

          <div class="why-ob-grid">
            <div class="why-ob-card">
              <span>Setup reason</span>
              <strong>${whyOBCards(symbolObj, sector).setup}</strong>
            </div>

            <div class="why-ob-card">
              <span>Sector context</span>
              <strong>${whyOBCards(symbolObj, sector).sector}</strong>
            </div>

            <div class="why-ob-card">
              <span>Behavior read</span>
              <strong>${whyOBCards(symbolObj, sector).behavior}</strong>
            </div>

            <div class="why-ob-card">
              <span>Permission</span>
              <strong>${whyOBCards(symbolObj, sector).permission}</strong>
            </div>
          </div>

          <div class="symbol-action-strip">
            <div class="symbol-action watch" onclick="openTradeContext('${sector.name}', '${symbolObj.symbol}')">Open Trade Context</div>
            <div class="symbol-action" onclick="recordTradeContextAction('${symbolObj.symbol}', 'Added to watch from Symbol Page')">Add to Watch</div>
            <div class="symbol-action locked">Live Auto Locked</div>
          </div>

          <div class="fun-facts">
            Tower state: Live automated remains locked. OB may observe, explain, and prepare review context only.
          </div>
        </div>
      </div>

      <div class="ob-panel movement-panel">
        <div class="ob-label">Movement Field / Price-Premium Path</div>

        <div class="movement-field">
          <svg class="movement-path" viewBox="0 0 100 100" preserveAspectRatio="none">
            <polyline points="4,72 18,66 33,70 48,48 64,44 78,30 94,26"></polyline>
          </svg>

          <div class="path-dot" style="left: 18%; top: 66%;"></div>
          <div class="path-dot" style="left: 48%; top: 48%;"></div>
          <div class="path-dot" style="left: 78%; top: 30%;"></div>

          <div class="movement-marker" style="left: 18%; top: 66%;">Entry</div>
          <div class="movement-marker" style="left: 48%; top: 48%;">Shift</div>
          <div class="movement-marker" style="left: 78%; top: 30%;">Now</div>
        </div>

        <div class="movement-info-grid">
          <div>
            <div class="movement-stat-grid">
              <div class="movement-stat">
                <span>Phase</span>
                <strong>${movementData(symbolObj).phase}</strong>
              </div>

              <div class="movement-stat">
                <span>Direction</span>
                <strong>${movementData(symbolObj).direction}</strong>
              </div>

              <div class="movement-stat">
                <span>Change</span>
                <strong>${movementData(symbolObj).current}</strong>
              </div>

              <div class="movement-stat">
                <span>Volume</span>
                <strong>${movementData(symbolObj).volume}</strong>
              </div>
            </div>

            <div class="movement-note" style="margin-top: 12px;">
              <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
              ${movementData(symbolObj).soulaana}
            </div>
          </div>

          <div class="movement-alert-list">
            <div class="movement-alert">
              <strong>Key level:</strong><br>
              ${movementData(symbolObj).keyLevel}
            </div>

            <div class="movement-alert">
              <strong>Next level:</strong><br>
              ${movementData(symbolObj).nextLevel}
            </div>

            <div class="movement-alert">
              <strong>Invalidation:</strong><br>
              ${movementData(symbolObj).invalidation}
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  detailPanel.innerHTML = `
    <button class="back-button" id="backToSector">Back to constellation</button>

    <div style="height: 16px;"></div>

    <div class="detail-title">${symbolObj.symbol}</div>
    <div class="detail-sub">${symbolObj.starName}</div>

    <div class="detail-row">
      <span>Constellation</span>
      <strong>${sector.constellationName}</strong>
    </div>

    <div class="detail-row">
      <span>Current State</span>
      <strong>${statusFromTier(symbolObj.tier)}</strong>
    </div>

    <div class="detail-row">
      <span>Signal Color</span>
      <strong>${symbolObj.tier === "hot" ? "Green-Gold" : symbolObj.tier === "watch" ? "Gold-Aqua" : "Blue-Gray"}</strong>
    </div>

    <div class="detail-row">
      <span>Permission</span>
      <strong>${symbolObj.permission}</strong>
    </div>

    <div class="fun-facts">
      <strong style="color: var(--ob-purple);">Soulaana:</strong><br>
      This is the private observation room for one star. We stop looking at the whole sky and ask what this one symbol is actually doing.
    </div>

    <div class="fun-facts">
      Next build after this: wire real state objects into the Symbol Page and convert this Colab preview into the OB template.
    </div>
  `;

  document.getElementById("backToSector").onclick = () => renderSectorZoom(sector);
}

renderSky();

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.marketMapContract) {
  window.OB_MARKET_MAP_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.marketMapContract();
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
