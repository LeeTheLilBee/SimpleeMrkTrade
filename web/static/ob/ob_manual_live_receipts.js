// OBSERVATORY_V29_MANUAL_LIVE_RECEIPTS_REVIEW_INTEGRATION_JS

(function () {
  const VERSION = "OB_V29_MANUAL_LIVE_RECEIPTS_REVIEW_INTEGRATION";
  const FILTER_KEY = "ob.v29.manualLiveReceiptFilter";

  // V29 SMOKE MARKERS
  // Manual Live receipts stronger Review Center integration
  // Receipt timeline
  // Approve reject snooze fill exit receipt grouping
  // Review Center receipt filters
  // Private proof classification
  // Owner responsibility wording
  // No broker API
  // No auto execution
  // Live Auto Locked

  const fallbackReceipts = [
    {
      id: "v29-fallback-approval",
      symbol: "MU",
      company: "Micron Technology",
      action: "approve",
      status: "Owner approved manual placement",
      phase: "approval",
      classification: "official_manual_live",
      time: "Preview",
      responsibility: "Owner places manually at broker. OB does not execute.",
      contract: "MU next monthly call",
      tower: "Live Auto Locked"
    },
    {
      id: "v29-fallback-fill",
      symbol: "MU",
      company: "Micron Technology",
      action: "fill_confirmed",
      status: "Fill confirmation pending or recorded",
      phase: "fill",
      classification: "official_manual_live",
      time: "Preview",
      responsibility: "Owner confirms broker result back inside OB.",
      contract: "MU next monthly call",
      tower: "Live Auto Locked"
    },
    {
      id: "v29-fallback-review",
      symbol: "MU",
      company: "Micron Technology",
      action: "review",
      status: "Review receipt ready",
      phase: "review",
      classification: "private_review",
      time: "Preview",
      responsibility: "Review Center keeps the receipt private unless Tower clears export.",
      contract: "Manual Live Level 1",
      tower: "Proof/Demo private"
    }
  ];

  function currentRoomKey() {
    const path = window.location.pathname.toLowerCase();

    if (path.includes("/symbol/")) return "symbol_page";
    if (path.includes("market-map")) return "market_map";
    if (path.includes("trade-center")) return "trade_center";
    if (path.includes("review-center")) return "review_center";
    if (path.includes("owner-console")) return "owner_console";
    return "dashboard";
  }

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function loadManualReceiptsRaw() {
    if (window.OB_MANUAL_LIVE_V19 && window.OB_MANUAL_LIVE_V19.loadReceipts) {
      const rows = window.OB_MANUAL_LIVE_V19.loadReceipts();
      if (Array.isArray(rows) && rows.length) return rows;
    }

    const possibleKeys = [
      "ob.v19.manualLiveReceipts",
      "ob.manualLive.receipts",
      "ob.manual_live_receipts",
      "manualLiveReceipts"
    ];

    for (const key of possibleKeys) {
      try {
        const parsed = JSON.parse(localStorage.getItem(key) || "[]");
        if (Array.isArray(parsed) && parsed.length) return parsed;
      } catch (error) {
        // keep checking
      }
    }

    return fallbackReceipts;
  }

  function inferPhase(row) {
    const value = [
      row.phase,
      row.action,
      row.status,
      row.manualStatus,
      row.receiptState
    ].map(item => safeText(item, "").toLowerCase()).join(" ");

    if (value.includes("approve")) return "approval";
    if (value.includes("reject")) return "rejected";
    if (value.includes("snooze") || value.includes("watch")) return "watch";
    if (value.includes("fill") || value.includes("submitted")) return "fill";
    if (value.includes("exit") || value.includes("close") || value.includes("sell")) return "exit";
    if (value.includes("monitor")) return "monitoring";
    if (value.includes("review")) return "review";
    return "review";
  }

  function inferClassification(row, phase) {
    const value = [
      row.classification,
      row.proof,
      row.status,
      row.tower,
      row.type
    ].map(item => safeText(item, "").toLowerCase()).join(" ");

    if (value.includes("proof") || value.includes("demo")) return "private_proof_demo";
    if (value.includes("test") || value.includes("preview")) return "test_or_preview";
    if (phase === "approval" || phase === "fill" || phase === "exit" || phase === "monitoring") return "official_manual_live";
    if (phase === "rejected" || phase === "watch") return "decision_receipt";
    return "private_review";
  }

  function normalizeReceipt(row, index) {
    const phase = inferPhase(row);
    const classification = inferClassification(row, phase);
    const symbol = safeText(row.symbol || row.ticker || row.underlying, "UNKNOWN").toUpperCase();

    return {
      version: VERSION,
      id: safeText(row.id || row.receipt_id || row.createdAt || ("receipt-" + index), "receipt-" + index),
      symbol,
      company: safeText(row.company || row.name, symbol),
      action: safeText(row.action || row.status || phase, phase),
      status: safeText(row.status || row.manualStatus || row.receiptState, phase),
      phase,
      classification,
      time: safeText(row.time || row.createdAt || row.timestamp || row.date, "Local receipt"),
      contract: safeText(row.contract || row.contractSymbol || row.orderTicket || row.suggested_contract, "Manual Live Level 1"),
      responsibility: safeText(row.responsibility || row.note || row.notes, "Execution responsibility stays with owner at brokerage. OB records, explains, and monitors."),
      tower: safeText(row.tower || row.permission || row.boundary, "Live Auto Locked"),
      privateProof: classification === "private_proof_demo" || classification === "private_review",
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true,
      raw: row
    };
  }

  function allReceipts() {
    return loadManualReceiptsRaw().map(normalizeReceipt);
  }

  function receiptFilter() {
    return localStorage.getItem(FILTER_KEY) || "all";
  }

  function setReceiptFilter(filter) {
    localStorage.setItem(FILTER_KEY, filter);
    renderPanel();
  }

  function filteredReceipts() {
    const filter = receiptFilter();
    const rows = allReceipts();

    if (filter === "all") return rows;
    if (filter === "official") return rows.filter(row => row.classification === "official_manual_live");
    if (filter === "decision") return rows.filter(row => row.classification === "decision_receipt" || row.phase === "rejected" || row.phase === "watch");
    if (filter === "fill_exit") return rows.filter(row => row.phase === "fill" || row.phase === "exit" || row.phase === "monitoring");
    if (filter === "proof") return rows.filter(row => row.classification === "private_proof_demo" || row.classification === "private_review");
    if (filter === "test") return rows.filter(row => row.classification === "test_or_preview");
    return rows;
  }

  function summary() {
    const rows = allReceipts();

    return {
      total: rows.length,
      approval: rows.filter(row => row.phase === "approval").length,
      rejected: rows.filter(row => row.phase === "rejected").length,
      watch: rows.filter(row => row.phase === "watch").length,
      fillExit: rows.filter(row => row.phase === "fill" || row.phase === "exit" || row.phase === "monitoring").length,
      proof: rows.filter(row => row.classification === "private_proof_demo" || row.classification === "private_review").length
    };
  }

  function summaryCard(label, value) {
    return `
      <div class="ob-ml-receipts-summary-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function badge(text, kind) {
    return `<span class="ob-ml-receipt-badge ${kind || ""}">${text}</span>`;
  }

  function phaseKind(phase) {
    if (phase === "approval" || phase === "fill" || phase === "monitoring") return "green";
    if (phase === "watch" || phase === "review") return "gold";
    if (phase === "rejected" || phase === "exit") return "red";
    return "gold";
  }

  function classificationKind(classification) {
    if (classification === "official_manual_live") return "green";
    if (classification === "private_proof_demo" || classification === "private_review") return "gold";
    if (classification === "test_or_preview") return "gold";
    return "gold";
  }

  function receiptRow(row, index) {
    return `
      <div class="ob-ml-receipt-row" data-ob-v29-manual-live-receipt="${row.id}">
        <div class="ob-ml-receipt-dot">${index + 1}</div>

        <div>
          <div class="ob-ml-receipt-symbol">${row.symbol}</div>
          <div class="ob-ml-receipt-meta">${row.time}<br>${row.contract}</div>
        </div>

        <div class="ob-ml-receipt-copy">
          <strong>${row.status}</strong>
          <span>${row.responsibility}</span>
        </div>

        <div class="ob-ml-receipt-badges">
          ${badge(row.phase, phaseKind(row.phase))}
          ${badge(row.classification.replaceAll("_", " "), classificationKind(row.classification))}
          ${badge("Live Auto Locked", "red")}
        </div>
      </div>
    `;
  }

  function tabsHtml() {
    const current = receiptFilter();
    const tabs = [
      ["all", "All receipts"],
      ["official", "Official Manual Live"],
      ["decision", "Approve / Reject / Snooze"],
      ["fill_exit", "Fill / Exit"],
      ["proof", "Private Proof"],
      ["test", "Test / Preview"]
    ];

    return `
      <div class="ob-ml-receipts-tabs">
        ${tabs.map(tab => `
          <button class="ob-ml-receipts-tab ${current === tab[0] ? "active" : ""}" type="button" data-ob-v29-receipt-filter="${tab[0]}">
            ${tab[1]}
          </button>
        `).join("")}
      </div>
    `;
  }

  function panelTitle() {
    const room = currentRoomKey();

    if (room === "review_center") return "Review Center Manual Live receipt timeline";
    if (room === "trade_center") return "Trade Center Manual Live receipt handoff";
    if (room === "owner_console") return "Owner Console receipt audit";
    return "Manual Live receipt summary";
  }

  function panelSubtitle() {
    const room = currentRoomKey();

    if (room === "review_center") {
      return "Approve, reject, snooze, fill, monitor, exit, and review receipts are grouped for private review.";
    }

    if (room === "trade_center") {
      return "Trade actions and owner confirmations are recorded as receipts before Review Center classification.";
    }

    if (room === "owner_console") {
      return "Owner can audit Manual Live receipt grouping, private proof boundaries, and no-execution rules.";
    }

    return "Manual Live receipt status is visible without exposing private proof or changing execution.";
  }

  function panelHtml() {
    const totals = summary();
    const rows = filteredReceipts();

    return `
      <div class="ob-ml-receipts-panel" id="obManualLiveReceiptsPanel" data-ob-v29-manual-live-receipts="true">
        <div class="ob-ml-receipts-head">
          <div>
            <div class="ob-label">Manual Live Receipts · V29</div>
            <div class="ob-ml-receipts-title">${panelTitle()}</div>
            <div class="ob-ml-receipts-subtitle">${panelSubtitle()}</div>
          </div>

          <div class="ob-ml-receipts-chip-row">
            <span class="ob-ml-receipts-chip green">Receipt timeline</span>
            <span class="ob-ml-receipts-chip gold">Private proof</span>
            <span class="ob-ml-receipts-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-ml-receipts-summary">
          ${summaryCard("Total", totals.total)}
          ${summaryCard("Approved", totals.approval)}
          ${summaryCard("Rejected", totals.rejected)}
          ${summaryCard("Snoozed / Watch", totals.watch)}
          ${summaryCard("Fill / Exit", totals.fillExit)}
          ${summaryCard("Private", totals.proof)}
        </div>

        ${tabsHtml()}

        <div class="ob-ml-receipts-timeline">
          ${rows.length ? rows.slice(-8).reverse().map(receiptRow).join("") : `
            <div class="ob-ml-receipt-row">
              <div class="ob-ml-receipt-dot">0</div>
              <div>
                <div class="ob-ml-receipt-symbol">WAIT</div>
                <div class="ob-ml-receipt-meta">No rows</div>
              </div>
              <div class="ob-ml-receipt-copy">
                <strong>No receipts match this filter.</strong>
                <span>Manual Live receipts will appear after owner review, broker confirmation, fill, exit, or review classification.</span>
              </div>
              <div class="ob-ml-receipt-badges">${badge("Private", "gold")}</div>
            </div>
          `}
        </div>

        <div class="ob-ml-receipts-private-proof">
          <strong>Private proof classification:</strong><br>
          Proof/Demo, test, preview, and private review records stay internal. Public proof remains cut unless Tower clears a redacted export later.
        </div>

        <div class="ob-ml-receipts-boundary">
          <strong>Owner responsibility:</strong><br>
          OB may detect, explain, record, and monitor. Owner places or does not place at brokerage. No broker API. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveReceiptsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const candidatePanel = document.getElementById("obCandidateCardsPanel");
    const roomPolishPanel = document.getElementById("obRoomDataPolishPanel");
    const snapshotPanel = document.getElementById("obSnapshotDisplayPanel");
    const engineBar = document.getElementById("obEngineFeedBar");
    const dataBar = document.getElementById("obDataStatusBar");
    const missionBar = document.getElementById("obMissionBar");
    const routeBar = document.getElementById("obRouteBar");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (candidatePanel && candidatePanel.parentNode) {
      candidatePanel.insertAdjacentElement("afterend", panel);
    } else if (roomPolishPanel && roomPolishPanel.parentNode) {
      roomPolishPanel.insertAdjacentElement("afterend", panel);
    } else if (snapshotPanel && snapshotPanel.parentNode) {
      snapshotPanel.insertAdjacentElement("afterend", panel);
    } else if (engineBar && engineBar.parentNode) {
      engineBar.insertAdjacentElement("afterend", panel);
    } else if (dataBar && dataBar.parentNode) {
      dataBar.insertAdjacentElement("afterend", panel);
    } else if (missionBar && missionBar.parentNode) {
      missionBar.insertAdjacentElement("afterend", panel);
    } else if (routeBar && routeBar.parentNode) {
      routeBar.insertAdjacentElement("afterend", panel);
    } else {
      layer.prepend(panel);
    }

    panel.querySelectorAll("[data-ob-v29-receipt-filter]").forEach(button => {
      button.addEventListener("click", function () {
        setReceiptFilter(this.getAttribute("data-ob-v29-receipt-filter"));
      });
    });
  }

  function setFlags() {
    document.body.setAttribute("data-ob-v29-manual-live-receipts", "ready");
    window.OB_V29_MANUAL_LIVE_RECEIPT_STATE = {
      version: VERSION,
      room: currentRoomKey(),
      receiptCount: allReceipts().length,
      filter: receiptFilter(),
      privateProof: true,
      ownerResponsibility: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    setTimeout(function () {
      renderPanel();
      setFlags();
    }, 790);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedAdapterUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_MANUAL_LIVE_RECEIPTS_V29 = {
    version: VERSION,
    loadManualReceiptsRaw,
    normalizeReceipt,
    allReceipts,
    filteredReceipts,
    summary,
    renderPanel,
    setReceiptFilter,
    setFlags
  };
})();
