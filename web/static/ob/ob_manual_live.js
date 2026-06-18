// OBSERVATORY_V19_MANUAL_LIVE_LEVEL_1_FULL_LOOP_JS

(function () {
  const RECEIPT_KEY = "ob.manualLive.v19.receipts";

  const candidates = [
    {
      symbol: "MU",
      company: "Micron Technology",
      assetType: "Option premium mode",
      direction: "Bullish watch",
      strategy: "Momentum continuation",
      confidence: "82",
      risk: "Moderate",
      reviewWindow: "20 minutes",
      action: "Buy to Open",
      contract: "MU next monthly call",
      quantity: "1",
      orderType: "Limit",
      limit: "Review current premium",
      tif: "Day",
      stop: "Premium-based stop required",
      target: "Target zone only if movement confirms",
      maxLoss: "Premium paid",
      status: "Needs owner review",
      blocker: "Live Auto Locked. Manual placement only.",
      soulaana: "MU is bright, but we still move like grown folks. Review the contract, check the spread, respect the account mission, and do not place anything if the broker screen does not match OB."
    },
    {
      symbol: "AMD",
      company: "Advanced Micro Devices",
      assetType: "Option-first review",
      direction: "Bullish watch",
      strategy: "Semiconductor continuation",
      confidence: "78",
      risk: "Moderate crowding",
      reviewWindow: "18 minutes",
      action: "Buy to Open",
      contract: "AMD next monthly call",
      quantity: "1",
      orderType: "Limit",
      limit: "Review current premium",
      tif: "Day",
      stop: "Premium-based stop required",
      target: "Target zone after confirmation",
      maxLoss: "Premium paid",
      status: "Needs owner review",
      blocker: "Crowding check required. Live Auto Locked.",
      soulaana: "AMD can talk loud when semis are glowing. Loud does not mean clean. Check crowding before you even think about broker placement."
    },
    {
      symbol: "NVDA",
      company: "NVIDIA",
      assetType: "Option-first review",
      direction: "Leadership watch",
      strategy: "Leader continuation",
      confidence: "84",
      risk: "High attention / crowding",
      reviewWindow: "15 minutes",
      action: "Buy to Open",
      contract: "NVDA next monthly call",
      quantity: "1",
      orderType: "Limit",
      limit: "Review current premium",
      tif: "Day",
      stop: "Premium-based stop required",
      target: "Target zone only if risk remains clean",
      maxLoss: "Premium paid",
      status: "Needs owner review",
      blocker: "Crowding elevated. Live Auto Locked.",
      soulaana: "This star is powerful, but powerful names can humble you fast. If the spread is ugly or crowding is hot, leave it alone."
    }
  ];

  function loadReceipts() {
    try {
      return JSON.parse(localStorage.getItem(RECEIPT_KEY) || "[]");
    } catch (error) {
      return [];
    }
  }

  function saveReceipts(receipts) {
    localStorage.setItem(RECEIPT_KEY, JSON.stringify(receipts.slice(-25)));
    window.dispatchEvent(new CustomEvent("obManualLiveReceiptsUpdated"));
  }

  function addReceipt(candidate, action, extra) {
    const receipts = loadReceipts();
    const now = new Date().toLocaleString();

    receipts.push({
      id: "ML-" + Date.now(),
      symbol: candidate.symbol,
      company: candidate.company,
      action,
      status: extra && extra.status ? extra.status : action,
      time: now,
      strategy: candidate.strategy,
      assetType: candidate.assetType,
      contract: candidate.contract,
      quantity: extra && extra.quantity ? extra.quantity : candidate.quantity,
      fillPrice: extra && extra.fillPrice ? extra.fillPrice : "",
      brokerOrderId: extra && extra.brokerOrderId ? extra.brokerOrderId : "",
      notes: extra && extra.notes ? extra.notes : "",
      responsibility: "Owner at brokerage. OB records and monitors only.",
      tower: "Live Auto Locked. Manual Live Level 1."
    });

    saveReceipts(receipts);
  }

  function getCandidate(symbol) {
    return candidates.find(item => item.symbol === symbol) || candidates[0];
  }

  function closeDrawer() {
    const existing = document.getElementById("obManualLiveBackdrop");
    if (existing) existing.remove();
  }

  function stepper(active) {
    const steps = ["Review", "Approve", "Broker", "Confirm", "Monitor"];
    return `
      <div class="manual-live-stepper">
        ${steps.map(step => `
          <div class="manual-live-step ${step === active ? "active" : ""}">${step}</div>
        `).join("")}
      </div>
    `;
  }

  function ticket(candidate) {
    return `
      <div class="manual-ticket-grid">
        <div class="manual-ticket-line"><span>Action</span><strong>${candidate.action}</strong></div>
        <div class="manual-ticket-line"><span>Symbol</span><strong>${candidate.symbol}</strong></div>
        <div class="manual-ticket-line"><span>Contract</span><strong>${candidate.contract}</strong></div>
        <div class="manual-ticket-line"><span>Quantity</span><strong>${candidate.quantity}</strong></div>
        <div class="manual-ticket-line"><span>Order type</span><strong>${candidate.orderType}</strong></div>
        <div class="manual-ticket-line"><span>Limit</span><strong>${candidate.limit}</strong></div>
        <div class="manual-ticket-line"><span>TIF</span><strong>${candidate.tif}</strong></div>
        <div class="manual-ticket-line"><span>Stop</span><strong>${candidate.stop}</strong></div>
        <div class="manual-ticket-line"><span>Target</span><strong>${candidate.target}</strong></div>
      </div>
    `;
  }

  function checklist(candidate) {
    const items = [
      "Correct brokerage account is selected.",
      "Ticker, expiration, strike, call/put, quantity, and action match OB.",
      "Bid/ask spread is acceptable.",
      "Price did not move outside review range.",
      "Buying power is still available.",
      "No new earnings/news warning appeared.",
      "Mission account rules still allow this review.",
      "Tower permission has not changed."
    ];

    return `
      <div class="manual-checklist">
        ${items.map(item => `
          <div class="manual-check-item">
            <div class="manual-check-icon"></div>
            <div>${item}</div>
          </div>
        `).join("")}
      </div>
    `;
  }

  function renderDrawer(candidate, phase) {
    closeDrawer();

    const active = phase || "Review";

    const backdrop = document.createElement("div");
    backdrop.className = "manual-live-backdrop open";
    backdrop.id = "obManualLiveBackdrop";

    const drawer = document.createElement("div");
    drawer.className = "manual-live-drawer";

    drawer.innerHTML = `
      <div class="manual-live-drawer-head">
        <div>
          <strong>${candidate.symbol} Manual Live Card</strong>
          <span>${candidate.company} · ${candidate.assetType} · ${candidate.status}</span>
        </div>
        <button class="manual-live-close" id="manualLiveClose">×</button>
      </div>

      ${stepper(active)}

      <div class="manual-live-section gold">
        <span>Candidate</span>
        <strong>${candidate.strategy} · Confidence ${candidate.confidence} · Risk ${candidate.risk}</strong>
      </div>

      <div class="manual-live-section">
        <span>Why OB is alerting</span>
        <strong>${candidate.symbol} is in a review window. OB may explain and prepare the checklist, but the owner must manually place or reject at the broker.</strong>
      </div>

      <div class="manual-live-section red">
        <span>Blocker / boundary</span>
        <strong>${candidate.blocker}</strong>
      </div>

      <div class="manual-live-section gold">
        <span>Soulaana</span>
        <strong>${candidate.soulaana}</strong>
      </div>

      ${active === "Review" ? `
        <div class="manual-live-action-grid">
          <button class="manual-live-action" id="manualApprove">Approve for manual placement</button>
          <button class="manual-live-action aqua" id="manualSnooze">Snooze / watch</button>
          <button class="manual-live-action red" id="manualReject">Reject</button>
        </div>
      ` : ""}

      ${active === "Broker" ? `
        <div class="manual-live-section green">
          <span>Broker checklist</span>
          ${ticket(candidate)}
        </div>

        <div class="manual-live-section">
          <span>Do not place if</span>
          ${checklist(candidate)}
        </div>

        <div class="manual-live-action-grid">
          <button class="manual-live-action" id="manualGoConfirm">I placed / attempted at broker</button>
          <button class="manual-live-action aqua" id="manualSnoozeBroker">Snooze / watch</button>
          <button class="manual-live-action red" id="manualCancelBroker">Canceled before broker placement</button>
        </div>
      ` : ""}

      ${active === "Confirm" ? `
        <div class="manual-live-section green">
          <span>Post-broker confirmation</span>
          <div class="manual-fill-grid">
            <div class="manual-fill-field">
              <label>Broker result</label>
              <select id="manualBrokerResult">
                <option value="Filled">Filled</option>
                <option value="Submitted but not filled">Submitted but not filled</option>
                <option value="Not placed">Not placed</option>
                <option value="Changed trade">Changed trade</option>
                <option value="Canceled">Canceled</option>
              </select>
            </div>

            <div class="manual-fill-field">
              <label>Fill price</label>
              <input id="manualFillPrice" placeholder="Example: 2.50" />
            </div>

            <div class="manual-fill-field">
              <label>Quantity</label>
              <input id="manualQuantity" placeholder="${candidate.quantity}" />
            </div>

            <div class="manual-fill-field">
              <label>Broker order ID</label>
              <input id="manualBrokerOrderId" placeholder="Optional" />
            </div>
          </div>
        </div>

        <div class="manual-live-action-grid">
          <button class="manual-live-action" id="manualConfirmResult">Confirm result in OB</button>
          <button class="manual-live-action red" id="manualConfirmCancel">Cancel confirmation</button>
        </div>
      ` : ""}

      ${active === "Monitor" ? `
        <div class="manual-live-section green">
          <span>Monitoring state</span>
          <strong>OB status: monitoring confirmed position. Watch premium, stop, target, time decay, liquidity, and Tower permission state.</strong>
        </div>

        <div class="manual-live-section">
          <span>Exit process</span>
          <strong>If OB detects target, stop, or risk change, it should alert the owner to review a Sell-to-Close checklist. Owner still closes manually at broker.</strong>
        </div>

        <div class="manual-live-action-grid">
          <button class="manual-live-action" id="manualExitAlert">Create exit alert receipt</button>
          <button class="manual-live-action aqua" id="manualReviewCenter">Review receipts</button>
          <button class="manual-live-action red" id="manualCloseDrawer">Close</button>
        </div>
      ` : ""}

      <div class="manual-receipt-box" id="manualLiveReceiptBox">
        <strong>Manual Live Level 1:</strong><br>
        OB prepares. Owner places manually. Broker executes. OB records and monitors.
      </div>
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("manualLiveClose").addEventListener("click", closeDrawer);
    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });

    const approve = document.getElementById("manualApprove");
    if (approve) {
      approve.addEventListener("click", function () {
        addReceipt(candidate, "Approved for manual placement", { status: "Awaiting broker checklist review" });
        renderDrawer(candidate, "Broker");
      });
    }

    const snooze = document.getElementById("manualSnooze");
    if (snooze) {
      snooze.addEventListener("click", function () {
        addReceipt(candidate, "Snooze / watch", { status: "Snoozed" });
        document.getElementById("manualLiveReceiptBox").innerHTML = `<strong>Receipt created:</strong><br>${candidate.symbol} snoozed / watch. No broker action.`;
        renderTradePanel();
        renderReviewReceiptsPanel();
      });
    }

    const reject = document.getElementById("manualReject");
    if (reject) {
      reject.addEventListener("click", function () {
        addReceipt(candidate, "Rejected", { status: "Rejected" });
        document.getElementById("manualLiveReceiptBox").innerHTML = `<strong>Receipt created:</strong><br>${candidate.symbol} rejected. No broker action.`;
        renderTradePanel();
        renderReviewReceiptsPanel();
      });
    }

    const goConfirm = document.getElementById("manualGoConfirm");
    if (goConfirm) {
      goConfirm.addEventListener("click", function () {
        addReceipt(candidate, "Broker checklist opened", { status: "Awaiting broker result" });
        renderDrawer(candidate, "Confirm");
      });
    }

    const snoozeBroker = document.getElementById("manualSnoozeBroker");
    if (snoozeBroker) {
      snoozeBroker.addEventListener("click", function () {
        addReceipt(candidate, "Snoozed before broker placement", { status: "Snoozed" });
        closeDrawer();
        renderTradePanel();
        renderReviewReceiptsPanel();
      });
    }

    const cancelBroker = document.getElementById("manualCancelBroker");
    if (cancelBroker) {
      cancelBroker.addEventListener("click", function () {
        addReceipt(candidate, "Canceled before broker placement", { status: "Canceled" });
        closeDrawer();
        renderTradePanel();
        renderReviewReceiptsPanel();
      });
    }

    const confirmResult = document.getElementById("manualConfirmResult");
    if (confirmResult) {
      confirmResult.addEventListener("click", function () {
        const result = document.getElementById("manualBrokerResult").value;
        const fillPrice = document.getElementById("manualFillPrice").value || "";
        const quantity = document.getElementById("manualQuantity").value || candidate.quantity;
        const brokerOrderId = document.getElementById("manualBrokerOrderId").value || "";

        addReceipt(candidate, result, {
          status: result === "Filled" ? "Monitoring" : result,
          fillPrice,
          quantity,
          brokerOrderId
        });

        renderTradePanel();
        renderReviewReceiptsPanel();

        if (result === "Filled") {
          renderDrawer(candidate, "Monitor");
        } else {
          document.getElementById("manualLiveReceiptBox").innerHTML = `<strong>Receipt created:</strong><br>${candidate.symbol} broker result: ${result}.`;
        }
      });
    }

    const confirmCancel = document.getElementById("manualConfirmCancel");
    if (confirmCancel) {
      confirmCancel.addEventListener("click", function () {
        addReceipt(candidate, "Confirmation canceled", { status: "Canceled" });
        closeDrawer();
        renderTradePanel();
        renderReviewReceiptsPanel();
      });
    }

    const exitAlert = document.getElementById("manualExitAlert");
    if (exitAlert) {
      exitAlert.addEventListener("click", function () {
        addReceipt(candidate, "Exit alert created", { status: "Exit review required" });
        document.getElementById("manualLiveReceiptBox").innerHTML = `<strong>Exit alert receipt:</strong><br>${candidate.symbol} exit review required. Owner must manually close at broker if approved.`;
        renderReviewReceiptsPanel();
      });
    }

    const reviewCenter = document.getElementById("manualReviewCenter");
    if (reviewCenter) {
      reviewCenter.addEventListener("click", function () {
        window.location.href = "/ob/review-center";
      });
    }

    const closeButton = document.getElementById("manualCloseDrawer");
    if (closeButton) {
      closeButton.addEventListener("click", closeDrawer);
    }
  }

  function latestStatus(symbol) {
    const receipts = loadReceipts().filter(item => item.symbol === symbol);
    if (!receipts.length) return "Needs owner review";
    return receipts[receipts.length - 1].status;
  }

  function renderTradePanel() {
    const mount = document.getElementById("tradeCenterMount");
    if (!mount) return;

    const existing = document.getElementById("obManualLiveV19Panel");
    if (existing) existing.remove();

    const panel = document.createElement("div");
    panel.id = "obManualLiveV19Panel";
    panel.className = "ob-panel manual-live-panel";

    panel.innerHTML = `
      <div class="manual-live-header-row">
        <div>
          <div class="ob-label">Manual Live Level 1</div>
          <div class="manual-live-title">Owner review → broker checklist → fill confirmation</div>
          <div class="manual-live-subtitle">
            No broker API. No automatic execution. OB prepares the trade card, the owner places manually, and OB records the result.
          </div>
        </div>

        <div class="manual-live-chip-row">
          <span class="manual-live-chip gold">Manual guarded</span>
          <span class="manual-live-chip green">Receipts on</span>
          <span class="manual-live-chip red">Live Auto Locked</span>
        </div>
      </div>

      <div class="manual-live-grid">
        ${candidates.map(candidate => `
          <div class="manual-live-card">
            <div class="manual-live-card-top">
              <div>
                <div class="manual-live-symbol">${candidate.symbol}</div>
                <div class="manual-live-company">${candidate.company}</div>
              </div>

              <div class="manual-live-chip-row">
                <span class="manual-live-chip gold">${latestStatus(candidate.symbol)}</span>
              </div>
            </div>

            <div class="manual-live-metrics">
              <div class="manual-live-metric"><span>Strategy</span><strong>${candidate.strategy}</strong></div>
              <div class="manual-live-metric"><span>Confidence</span><strong>${candidate.confidence}</strong></div>
              <div class="manual-live-metric"><span>Risk</span><strong>${candidate.risk}</strong></div>
              <div class="manual-live-metric"><span>Window</span><strong>${candidate.reviewWindow}</strong></div>
            </div>

            <div class="manual-live-note">
              <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
              ${candidate.soulaana}
            </div>

            <button class="manual-live-button" data-manual-symbol="${candidate.symbol}">
              Open Manual Live Card
            </button>
          </div>
        `).join("")}
      </div>
    `;

    mount.prepend(panel);

    panel.querySelectorAll("[data-manual-symbol]").forEach(button => {
      button.addEventListener("click", function () {
        renderDrawer(getCandidate(this.dataset.manualSymbol), "Review");
      });
    });
  }

  function renderReviewReceiptsPanel() {
    const mount = document.getElementById("reviewCenterMount");
    if (!mount) return;

    const existing = document.getElementById("obManualLiveReviewPanel");
    if (existing) existing.remove();

    const receipts = loadReceipts().slice().reverse();

    const panel = document.createElement("div");
    panel.id = "obManualLiveReviewPanel";
    panel.className = "ob-panel manual-review-panel";

    panel.innerHTML = `
      <div class="manual-live-header-row">
        <div>
          <div class="ob-label">Manual Live Receipts</div>
          <div class="manual-live-title">Level 1 action record</div>
          <div class="manual-live-subtitle">
            These records separate OB alert, owner review, broker action, fill confirmation, monitoring, and exit review.
          </div>
        </div>

        <div class="manual-live-chip-row">
          <span class="manual-live-chip gold">Private</span>
          <span class="manual-live-chip green">Review Center</span>
          <span class="manual-live-chip red">Tower export gated</span>
        </div>
      </div>

      <div class="manual-review-list">
        ${receipts.length ? receipts.map(receipt => `
          <div class="manual-review-row">
            <strong>${receipt.symbol} · ${receipt.status}</strong>
            <span>
              ${receipt.action} · ${receipt.time}<br>
              ${receipt.contract} · ${receipt.quantity ? "Qty " + receipt.quantity : "Qty pending"}
              ${receipt.fillPrice ? " · Fill " + receipt.fillPrice : ""}<br>
              ${receipt.responsibility}
            </span>
          </div>
        `).join("") : `
          <div class="manual-review-row">
            <strong>No Manual Live receipts yet.</strong>
            <span>Open Trade Center, review a Manual Live card, and choose approve / reject / snooze to create one.</span>
          </div>
        `}
      </div>

      <div class="manual-receipt-box">
        <strong>Soulaana:</strong><br>
        Receipts are memory. Memory keeps the system honest. We do not blur OB recommendation, owner approval, broker fill, and monitoring state.
      </div>
    `;

    mount.prepend(panel);
  }

  function boot() {
    renderTradePanel();
    renderReviewReceiptsPanel();
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(boot, 60);
  });

  window.addEventListener("obManualLiveReceiptsUpdated", function () {
    renderTradePanel();
    renderReviewReceiptsPanel();
  });

  window.OB_MANUAL_LIVE_V19 = {
    candidates,
    loadReceipts,
    addReceipt,
    renderTradePanel,
    renderReviewReceiptsPanel,
    openManualLiveCard: function (symbol) {
      renderDrawer(getCandidate(symbol), "Review");
    }
  };
})();

// OBSERVATORY_V22_REAL_ENGINE_DATA_WIRING_PREP_CONTRACT_HOOK
if (window.OB_DATA_CONTRACTS_V22 && window.OB_DATA_CONTRACTS_V22.manualLiveQueue) {
  window.OB_MANUAL_LIVE_QUEUE_CONTRACT_V22 = window.OB_DATA_CONTRACTS_V22.manualLiveQueue();
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
