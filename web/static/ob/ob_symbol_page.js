// OBSERVATORY_SYMBOL_PAGE_V12_REAL_STAR_ROOM_JS

function obFindSymbol(symbol) {
  const sectors = (window.OB_MARKET_DATA && window.OB_MARKET_DATA.sectors) || [];
  const wanted = String(symbol || "MU").toUpperCase();

  for (const sector of sectors) {
    const found = sector.symbols.find(item => String(item.symbol).toUpperCase() === wanted);
    if (found) {
      return { sector, symbolObj: found };
    }
  }

  return { sector: sectors[0], symbolObj: sectors[0] && sectors[0].symbols[0] };
}

function obStatusFromTier(tier) {
  if (tier === "hot") return "Brightening Watch";
  if (tier === "watch") return "Guarded Watch";
  if (tier === "blocked") return "Blocked / Gated";
  return "Background Star";
}

function obStarTypeFromTier(tier) {
  if (tier === "hot") return "Green-Gold Active Star";
  if (tier === "watch") return "Gold-Aqua Watch Star";
  if (tier === "blocked") return "Red-Gold Gated Star";
  return "Dim Background Star";
}

function obStarClass(tier) {
  if (tier === "hot") return "hot";
  if (tier === "watch") return "watch";
  if (tier === "blocked") return "blocked";
  return "background";
}

function obSignalColor(tier) {
  if (tier === "hot") return "Green-Gold";
  if (tier === "watch") return "Gold-Aqua";
  if (tier === "blocked") return "Red-Gold";
  return "Blue-Gray";
}

function obSoulaanaDeepRead(symbolObj, sector) {
  if (symbolObj.tier === "hot") {
    return {
      lead: "Okay, this star is talking. Not whispering. Talking. But bright does not mean automatic. Bright means we slow down, inspect the reason, and make sure the glow is earned.",
      sees: symbolObj.symbol + " is brightening inside " + sector.constellationName + ". The symbol is not just present. It is asking for attention.",
      means: "OB sees strength, participation, and enough movement to justify a closer read. This is a watch-first situation, not a chase-first situation.",
      careful: "The danger is excitement. A bright star can still get pulled down if the constellation gets crowded or the broader market cools.",
      next: "Open trade context only if permission, risk, and movement stay aligned. Let the signal keep proving itself."
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      lead: "This one is leaning forward, but it has not stepped into the light yet. I like that OB is watching it, but I do not like rushing a star before it proves itself.",
      sees: symbolObj.symbol + " is forming, but it is not fully lit yet. It is on the edge of attention.",
      means: "OB is tracking the symbol because something is developing, but it has not earned full confidence.",
      careful: "The danger is acting early because you want to be first. First is not the goal. Clean is the goal.",
      next: "Keep it on watch. Wait for cleaner follow-through before treating it like an action-ready star."
    };
  }

  return {
    lead: "This one is quiet. Quiet is not bad, but quiet is not a command either. OB can keep it in the sky without making it the center of your attention.",
    sees: symbolObj.symbol + " is visible in the sky, but it is not leading the move.",
    means: "OB keeps it in the background for context. It may matter later, but right now it is not the priority.",
    careful: "The danger is getting bored and trying to make a quiet symbol interesting.",
    next: "Leave it in the background until it earns a brighter state."
  };
}

function obMovementData(symbolObj) {
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

function obRiskPermissionState(symbolObj) {
  if (symbolObj.tier === "hot") {
    return {
      riskLevel: "Moderate",
      accountFit: "Paper review allowed",
      crowding: symbolObj.risk || "Moderate",
      duplicate: "Check before action",
      cooldown: "Clear",
      tower: "Tower allows observation and paper review. Live automated remains locked.",
      action: "Review only. Manual or live action requires owner/Tower clearance."
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      riskLevel: "Guarded",
      accountFit: "Watch first",
      crowding: symbolObj.risk || "Guarded",
      duplicate: "Not action-ready",
      cooldown: "Waiting",
      tower: "Tower keeps this in watch/review territory until the signal confirms.",
      action: "Do not escalate until movement, permission, and risk all improve."
    };
  }

  return {
    riskLevel: "Low action priority",
    accountFit: "Background only",
    crowding: symbolObj.risk || "No active risk",
    duplicate: "No trade context",
    cooldown: "N/A",
    tower: "Tower does not need to open action permissions for a background star.",
    action: "No action. Keep it visible for context only."
  };
}

function obTradeContextData(symbolObj) {
  if (symbolObj.tier === "hot") {
    return {
      status: "Needs owner review",
      strategy: "Momentum continuation",
      confidence: "82",
      actionWindow: "20 minutes",
      direction: "Bullish watch",
      asset: symbolObj.tradeType || "Option-first",
      contract: symbolObj.symbol + " next monthly call",
      entry: "Review entry zone before action",
      stop: "Premium-based stop required",
      target: "Target zone only if movement confirms",
      blocker: "Live automated locked. Manual review only.",
      soulaana: "This is where we slow down on purpose. A good-looking setup still has to pass risk, permission, and movement checks."
    };
  }

  if (symbolObj.tier === "watch") {
    return {
      status: "Watch only",
      strategy: "Developing setup",
      confidence: "61",
      actionWindow: "No action window yet",
      direction: "Needs confirmation",
      asset: symbolObj.tradeType || "Watch",
      contract: "No order ticket yet",
      entry: "Wait for confirmation",
      stop: "Not assigned",
      target: "Not assigned",
      blocker: "Signal is not action-ready.",
      soulaana: "Attention is not permission. This one can stay on the board, but it does not get a trade card until it proves itself cleaner."
    };
  }

  return {
    status: "Background only",
    strategy: "No active setup",
    confidence: "32",
    actionWindow: "None",
    direction: "No clear leadership",
    asset: symbolObj.tradeType || "Watch only",
    contract: "No order ticket",
    entry: "No entry",
    stop: "No stop",
    target: "No target",
    blocker: "Background star. No trade context should open for action.",
    soulaana: "This is not where we spend energy right now. Let it stay in the sky. It can earn attention later."
  };
}

function obOpenTradeContext(symbol) {
  const { sector, symbolObj } = obFindSymbol(symbol);
  const context = obTradeContextData(symbolObj);
  const panel = document.getElementById("symbolSidePanel");

  panel.innerHTML = `
    <button class="back-button" onclick="obRenderSymbolRoom('${symbolObj.symbol}')">Back to Symbol</button>

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
        <div class="ticket-line"><span>Contract</span><strong>${context.contract}</strong></div>
        <div class="ticket-line"><span>Entry</span><strong>${context.entry}</strong></div>
        <div class="ticket-line"><span>Stop</span><strong>${context.stop}</strong></div>
        <div class="ticket-line"><span>Target</span><strong>${context.target}</strong></div>
        <div class="ticket-line"><span>Window</span><strong>${context.actionWindow}</strong></div>
      </div>

      <div class="fun-facts">
        <strong style="color: var(--ob-purple);">Soulaana:</strong><br>
        ${context.soulaana}
      </div>

      <div class="trade-context-actions">
        <button class="trade-context-button" onclick="obRecordTradeContextAction('${symbolObj.symbol}', 'Approve for manual placement')">Approve for manual placement</button>
        <button class="trade-context-button reject" onclick="obRecordTradeContextAction('${symbolObj.symbol}', 'Rejected')">Reject</button>
        <button class="trade-context-button watch" onclick="obRecordTradeContextAction('${symbolObj.symbol}', 'Snooze / watch')">Snooze / watch</button>
      </div>

      <div class="trade-context-receipt" id="tradeContextReceipt">
        <strong>No receipt yet.</strong><br>
        Choose an action to create a review receipt preview.
      </div>
    </div>
  `;
}

function obRecordTradeContextAction(symbol, action) {
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

function obRenderSymbolRoom(symbol) {
  const found = obFindSymbol(symbol);
  const sector = found.sector;
  const symbolObj = found.symbolObj;
  const mount = document.getElementById("symbolRoomMount");
  const side = document.getElementById("symbolSidePanel");
  const narrative = obSoulaanaDeepRead(symbolObj, sector);
  const movement = obMovementData(symbolObj);
  const risk = obRiskPermissionState(symbolObj);
  const tierClass = obStarClass(symbolObj.tier);

  document.getElementById("symbolRoomTitle").textContent = symbolObj.symbol;
  document.getElementById("symbolRoomSubtitle").textContent = `OB://SymbolPage/${symbolObj.symbol} · ${sector.constellationName} · ${obStatusFromTier(symbolObj.tier)}`;
  document.getElementById("symbolHeroSoulaana").textContent = narrative.lead;

  mount.innerHTML = `
    <div class="sky-layout">
      <div class="symbol-room">
        <div class="ob-panel symbol-header">
          <div class="symbol-header-top">
            <div>
              <div class="symbol-ticker">${symbolObj.symbol}</div>
              <div class="symbol-company">${symbolObj.company || symbolObj.symbol}</div>
              <div class="detail-sub">${sector.constellationName} · ${obStatusFromTier(symbolObj.tier)}</div>
            </div>

            <div class="chip-row">
              <span class="ob-chip ob-chip-green">${String(symbolObj.permission || "").includes("Paper") ? "Paper Eligible" : "Watch Only"}</span>
              <span class="ob-chip ob-chip-gold">${symbolObj.position || "Watch"}</span>
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
            <div class="detail-row"><span>Symbol</span><strong>${symbolObj.symbol}</strong></div>
            <div class="detail-row"><span>Star Name</span><strong>${symbolObj.starName || symbolObj.symbol + " Star"}</strong></div>
            <div class="detail-row"><span>Star Type</span><strong>${obStarTypeFromTier(symbolObj.tier)}</strong></div>
            <div class="detail-row"><span>Market Role</span><strong>${symbolObj.role || "Market watch"}</strong></div>
            <div class="detail-row"><span>Permission</span><strong>${symbolObj.permission || "Watch Only"}</strong></div>
            <div class="fun-facts"><strong style="color: var(--ob-gold);">Fun fact:</strong><br>${symbolObj.fact || "OB is still learning this star."}</div>
          </div>
        </div>

        <div class="ob-panel soulaana-wide">
          <div class="ob-label">Soulaana · Symbol Read</div>
          <div class="soulaana-wide-text">${narrative.lead}</div>

          <div class="soulaana-guidance-grid">
            <div class="soulaana-beat"><span>What she sees</span><p>${narrative.sees}</p></div>
            <div class="soulaana-beat"><span>What it means</span><p>${narrative.means}</p></div>
            <div class="soulaana-beat"><span>Be careful</span><p>${narrative.careful}</p></div>
            <div class="soulaana-beat"><span>Next move</span><p>${narrative.next}</p></div>
          </div>
        </div>

        <div class="symbol-main-grid">
          <div class="ob-panel state-panel">
            <div class="ob-label">Position / Watch State</div>
            <div class="state-grid">
              <div class="state-card"><span>Status</span><strong>${symbolObj.position || "Watch"}</strong></div>
              <div class="state-card"><span>Asset Type</span><strong>${symbolObj.tradeType || "Watch only"}</strong></div>
              <div class="state-card"><span>Current State</span><strong>${obStatusFromTier(symbolObj.tier)}</strong></div>
              <div class="state-card"><span>Risk Glow</span><strong>${symbolObj.risk || risk.riskLevel}</strong></div>
            </div>
          </div>

          <div class="ob-panel state-panel why-ob-panel">
            <div class="ob-label">Why OB Is Watching</div>
            <div class="fun-facts">${symbolObj.why || "OB is tracking this star as part of its constellation context."}</div>

            <div class="symbol-action-strip">
              <div class="symbol-action watch" onclick="obOpenTradeContext('${symbolObj.symbol}')">Open Trade Context</div>
              <div class="symbol-action">Add to Watch</div>
              <div class="symbol-action locked">Live Auto Locked</div>
            </div>
          </div>
        </div>

        <div class="ob-panel risk-permission-panel">
          <div class="ob-label">Risk + Permission State</div>
          <div class="risk-permission-layout">
            <div class="risk-stack">
              <div class="risk-card gold"><span>Risk level</span><strong>${risk.riskLevel}</strong></div>
              <div class="risk-card green"><span>Account fit</span><strong>${risk.accountFit}</strong></div>
              <div class="risk-card gold"><span>Crowding / exposure</span><strong>${risk.crowding}</strong></div>
              <div class="risk-card gold"><span>Duplicate / cooldown</span><strong>${risk.duplicate} · ${risk.cooldown}</strong></div>
              <div class="tower-boundary-note"><strong>Tower boundary:</strong><br>${risk.tower}<br><br>${risk.action}</div>
            </div>

            <div>
              <div class="permission-orbit">
                <div class="permission-core"></div>
                <div class="permission-tag green" style="left: 50%; top: 19%;">Paper</div>
                <div class="permission-tag gold" style="left: 22%; top: 52%;">Manual guarded</div>
                <div class="permission-tag red" style="left: 72%; top: 52%;">Live auto locked</div>
                <div class="permission-tag gold" style="left: 50%; top: 82%;">Tower gate</div>
              </div>
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
                <div class="movement-stat"><span>Phase</span><strong>${movement.phase}</strong></div>
                <div class="movement-stat"><span>Direction</span><strong>${movement.direction}</strong></div>
                <div class="movement-stat"><span>Change</span><strong>${movement.current}</strong></div>
                <div class="movement-stat"><span>Volume</span><strong>${movement.volume}</strong></div>
              </div>

              <div class="movement-note" style="margin-top: 12px;">
                <strong style="color: var(--ob-gold);">Soulaana:</strong><br>${movement.soulaana}
              </div>
            </div>

            <div class="movement-alert-list">
              <div class="movement-alert"><strong>Key level:</strong><br>${movement.keyLevel}</div>
              <div class="movement-alert"><strong>Next level:</strong><br>${movement.nextLevel}</div>
              <div class="movement-alert"><strong>Invalidation:</strong><br>${movement.invalidation}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="ob-panel detail-panel" id="symbolSidePanel"></div>
    </div>
  `;

  side.innerHTML = `
    <div class="detail-title">${symbolObj.symbol}</div>
    <div class="detail-sub">${symbolObj.starName || symbolObj.symbol + " Star"}</div>
    <div class="detail-row"><span>Constellation</span><strong>${sector.constellationName}</strong></div>
    <div class="detail-row"><span>Current State</span><strong>${obStatusFromTier(symbolObj.tier)}</strong></div>
    <div class="detail-row"><span>Signal Color</span><strong>${obSignalColor(symbolObj.tier)}</strong></div>
    <div class="detail-row"><span>Permission</span><strong>${symbolObj.permission || "Watch Only"}</strong></div>
    <div class="fun-facts"><strong style="color: var(--ob-purple);">Soulaana:</strong><br>This is the private observation room for one star. We stop looking at the whole sky and ask what this one symbol is actually doing.</div>
  `;
}

document.addEventListener("DOMContentLoaded", function() {
  const app = document.getElementById("ob-app");
  const symbol = app ? app.getAttribute("data-symbol") : "MU";
  obRenderSymbolRoom(symbol || "MU");
});

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.symbolPageContract) {
  window.OB_SYMBOL_PAGE_CONTRACT_V22_READY = true;
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
