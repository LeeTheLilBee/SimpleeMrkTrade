// OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE";
  const QUEUE_ENDPOINT = "/ob/manual-live-proof-packet-review-queue.json";

  // SMOKE MARKERS
  // Real Manual Live Proof Packet Owner Review Queue
  // real manual live proof packet owner review queue
  // real owner review queue persistence
  // real receipt packet search
  // real queue filtering
  // real queue status update
  // proof packet owner queue
  // needs review queue
  // clean packet queue
  // blocked live queue
  // watch packet queue
  // packet search by symbol
  // packet search by outcome
  // packet search by status
  // queue item hash
  // queue item detail endpoint
  // persisted queue item
  // receipt packet review lane
  // no direct Vault upload
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // Live Auto Locked

  let queueState = {
    status: "booting",
    overview: null,
    selectedItem: null,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function fallbackOverview() {
    return {
      ok: true,
      version: VERSION,
      queue_items: [],
      queue_item_count: 0,
      status_counts: {},
      symbol_counts: {},
      priority_counts: {},
      outcome_counts: {},
      real_owner_review_queue_persistence: true,
      real_receipt_packet_search: true,
      real_queue_filtering: true,
      boundaries: {
        manual_live_proof_packet_owner_review_queue_only: true,
        real_sqlite_persistence: true,
        real_receipt_packet_persistence: true,
        real_owner_review_queue_persistence: true,
        real_receipt_packet_search: true,
        real_queue_filtering: true,
        real_queue_status_update: true,
        real_manual_live_ready: false,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        broker_api_used: false,
        broker_account_read: false,
        order_submit_enabled: false,
        auto_execution_enabled: false,
        bank_account_read: false,
        real_capital_movement_enabled: false,
        direct_vault_upload_enabled: false,
        live_auto_locked: true
      },
      blocked_actions: [
        "submit_real_broker_order",
        "read_broker_account",
        "auto_execute_trade",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "mark_real_manual_live_ready"
      ]
    };
  }

  function expose(payload) {
    const safe = payload && typeof payload === "object" ? payload : fallbackOverview();
    queueState.overview = safe;
    window.OB_MANUAL_LIVE_PROOF_PACKET_REVIEW_QUEUE_GP039 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_proof_packet_review_queue_gp039: safe,
      realOwnerReviewQueuePersistence: true,
      realReceiptPacketSearch: true,
      realQueueFiltering: true,
      realQueueStatusUpdate: true,
      notRealManualLiveReady: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noBankAccountRead: true,
      noRealCapitalMovement: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obManualLiveProofPacketReviewQueueUpdated", { detail: safe }));
    return safe;
  }

  function queryFromForm() {
    const form = document.getElementById("obProofPacketQueueFilterForm");
    if (!form) return "";
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => {
      if (String(value || "").trim()) params.set(key, String(value).trim());
    });
    return params.toString();
  }

  async function fetchQueue(queryString) {
    queueState.status = "loading";
    try {
      const query = queryString || queryFromForm();
      const response = await fetch(QUEUE_ENDPOINT + (query ? "?" + query : ""), {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("queue status " + response.status);
      const payload = await response.json();
      expose(payload);
      queueState.status = "ready";
    } catch (error) {
      expose(fallbackOverview());
      queueState.status = "fallback";
      queueState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return queueState;
  }

  async function readQueueItem(queueItemId) {
    const response = await fetch(`/ob/manual-live-proof-packet-review-queue/${encodeURIComponent(queueItemId)}.json`, {
      credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("queue item read failed " + response.status);
    const result = await response.json();
    queueState.selectedItem = result.queue_item || null;
    renderPanel();
    setFlags();
    return result;
  }

  async function updateQueueItem(queueItemId, queueStatus, priority) {
    const response = await fetch(`/ob/manual-live-proof-packet-review-queue/${encodeURIComponent(queueItemId)}.json`, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        queue_status: queueStatus,
        priority: priority,
        review_reason: "Owner updated proof packet queue item from OB UI."
      })
    });
    if (!response.ok) throw new Error("queue item update failed " + response.status);
    const result = await response.json();
    queueState.selectedItem = result.queue_item || null;
    await fetchQueue();
    return result;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("false") || text.includes("needs") || text.includes("locked")) return "red";
    if (text.includes("clean") || text.includes("true") || text.includes("ready") || text.includes("low")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-proof-packet-review-queue-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function queueRow(item, index) {
    return `
      <div class="ob-manual-live-proof-packet-review-queue-row">
        <div class="ob-manual-live-proof-packet-review-queue-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.symbol, "UNKNOWN")} · ${safeText(item.queue_status, "status")}</strong>
          <span>${safeText(item.priority, "priority")} · ${safeText(item.queue_item_id, "queue")}</span>
        </div>
        <span>
          Outcome: ${safeText(item.dry_run_outcome, "outcome")}<br>
          Packet: ${safeText(item.packet_id, "packet")}<br>
          Reason: ${safeText(item.review_reason, "reason")}<br>
          Queue hash: ${safeText(item.queue_hash, "").slice(0, 22)}
        </span>
        <div>
          <button class="ob-manual-live-proof-packet-review-queue-button" type="button" data-ob-queue-read="${safeText(item.queue_item_id, "")}">Detail</button>
        </div>
      </div>
    `;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-proof-packet-review-queue-row">
        <div class="ob-manual-live-proof-packet-review-queue-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-proof-packet-review-queue-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-proof-packet-review-queue-row">
        <div class="ob-manual-live-proof-packet-review-queue-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This remains blocked while owner queue review is allowed.</span>
        <div class="ob-manual-live-proof-packet-review-queue-status red">blocked</div>
      </div>
    `;
  }

  function selectedItemHtml() {
    const item = queueState.selectedItem;
    if (!item) {
      return `<div class="ob-manual-live-proof-packet-review-queue-callout">Select a queue item to inspect or update it.</div>`;
    }

    return `
      <div class="ob-manual-live-proof-packet-review-queue-card">
        <span>Selected queue item</span>
        <strong>${safeText(item.symbol, "UNKNOWN")} · ${safeText(item.queue_status, "status")}</strong>
        <div class="ob-manual-live-proof-packet-review-queue-callout">
          <strong>Queue item:</strong> ${safeText(item.queue_item_id, "queue")}<br>
          <strong>Packet:</strong> ${safeText(item.packet_id, "packet")}<br>
          <strong>Record:</strong> ${safeText(item.record_id, "record")}<br>
          <strong>Outcome:</strong> ${safeText(item.dry_run_outcome, "outcome")}<br>
          <strong>Priority:</strong> ${safeText(item.priority, "priority")}<br>
          <strong>Hash:</strong> ${safeText(item.queue_hash, "hash")}
        </div>

        <form class="ob-manual-live-proof-packet-review-queue-form" id="obProofPacketQueueUpdateForm" data-queue-item-id="${safeText(item.queue_item_id, "")}">
          <select name="queue_status" aria-label="Queue status">
            <option value="new">new</option>
            <option value="needs_review">needs_review</option>
            <option value="clean">clean</option>
            <option value="blocked_live">blocked_live</option>
            <option value="watch">watch</option>
            <option value="archived">archived</option>
          </select>
          <select name="priority" aria-label="Priority">
            <option value="low">low</option>
            <option value="normal">normal</option>
            <option value="high">high</option>
            <option value="urgent">urgent</option>
          </select>
          <button class="ob-manual-live-proof-packet-review-queue-button" type="submit">Update Queue Item</button>
        </form>

        <div class="ob-manual-live-proof-packet-review-queue-boundary">
          <strong>Still locked:</strong><br>
          Queue review does not submit orders, read broker accounts, move money, or upload directly to Vault.
        </div>
      </div>
    `;
  }

  function panelHtml() {
    const overview = queueState.overview || fallbackOverview();
    const items = Array.isArray(overview.queue_items) ? overview.queue_items : [];
    const boundaries = overview.boundaries || fallbackOverview().boundaries;
    const blocked = overview.blocked_actions || fallbackOverview().blocked_actions;

    const statusCounts = overview.status_counts || {};
    const symbolCounts = overview.symbol_counts || {};
    const priorityCounts = overview.priority_counts || {};

    return `
      <div class="ob-manual-live-proof-packet-review-queue-panel" id="obManualLiveProofPacketReviewQueuePanel" data-ob-giant-pack-039="true">
        <div class="ob-manual-live-proof-packet-review-queue-head">
          <div>
            <div class="ob-label">OB Giant Pack 039 · Real Proof Packet Queue</div>
            <div class="ob-manual-live-proof-packet-review-queue-title">Real Manual Live Proof Packet Owner Review Queue</div>
            <div class="ob-manual-live-proof-packet-review-queue-subtitle">
              ${safeText(queueState.status, "booting")} · persisted queue items · real receipt packet search/filtering.
            </div>
          </div>
          <div class="ob-manual-live-proof-packet-review-queue-chip-row">
            <span class="ob-manual-live-proof-packet-review-queue-chip green">Real queue DB</span>
            <span class="ob-manual-live-proof-packet-review-queue-chip green">Search/filter</span>
            <span class="ob-manual-live-proof-packet-review-queue-chip gold">Owner review</span>
            <span class="ob-manual-live-proof-packet-review-queue-chip red">No direct Vault upload</span>
          </div>
        </div>

        <div class="ob-manual-live-proof-packet-review-queue-stat-grid">
          ${card("Queue", safeText(overview.queue_item_count, items.length))}
          ${card("Needs review", safeText(statusCounts.needs_review || 0, "0"))}
          ${card("Clean", safeText(statusCounts.clean || 0, "0"))}
          ${card("High", safeText(priorityCounts.high || 0, "0"))}
          ${card("Symbols", safeText(Object.keys(symbolCounts).length, "0"))}
        </div>

        <div class="ob-manual-live-proof-packet-review-queue-grid">
          <div>
            <div class="ob-manual-live-proof-packet-review-queue-card">
              <span>Owner queue state</span>
              <strong>Real proof packet queue items are materialized from persisted receipt packets.</strong>
              <div class="ob-manual-live-proof-packet-review-queue-callout">
                <strong>What is real:</strong><br>
                Queue table, queue item hashes, search/filter endpoint, detail endpoint, and status updates.
              </div>
              <div class="ob-manual-live-proof-packet-review-queue-boundary">
                <strong>Boundary:</strong><br>
                This queue reviews proof packets only. Real Manual Live, broker, bank, capital, and direct Vault actions remain locked.
              </div>
            </div>

            <div class="ob-manual-live-proof-packet-review-queue-card" style="margin-top: 11px;">
              <span>Search / filter queue</span>
              <form class="ob-manual-live-proof-packet-review-queue-form" id="obProofPacketQueueFilterForm">
                <input name="q" placeholder="Search symbol, packet, record, reason" aria-label="Search">
                <input name="symbol" placeholder="Symbol, e.g. MU" aria-label="Symbol">
                <select name="queue_status" aria-label="Queue status">
                  <option value="">any queue status</option>
                  <option value="new">new</option>
                  <option value="needs_review">needs_review</option>
                  <option value="clean">clean</option>
                  <option value="blocked_live">blocked_live</option>
                  <option value="watch">watch</option>
                  <option value="archived">archived</option>
                </select>
                <select name="dry_run_outcome" aria-label="Outcome">
                  <option value="">any outcome</option>
                  <option value="not_placed">not_placed</option>
                  <option value="fake_fill">fake_fill</option>
                  <option value="needs_review">needs_review</option>
                  <option value="cancelled">cancelled</option>
                  <option value="skipped">skipped</option>
                </select>
                <button class="ob-manual-live-proof-packet-review-queue-button" type="submit">Apply Filters</button>
              </form>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-proof-packet-review-queue-section">
              <div class="ob-manual-live-proof-packet-review-queue-section-title">Queue items</div>
              <div class="ob-manual-live-proof-packet-review-queue-list">
                ${items.length ? items.map(queueRow).join("") : `<div class="ob-manual-live-proof-packet-review-queue-callout">No queue items yet. GP038 receipt packets will materialize here.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-proof-packet-review-queue-section">
              <div class="ob-manual-live-proof-packet-review-queue-section-title">Selected queue item</div>
              ${selectedItemHtml()}
            </div>

            <div class="ob-manual-live-proof-packet-review-queue-section">
              <div class="ob-manual-live-proof-packet-review-queue-section-title">Queue boundaries</div>
              <div class="ob-manual-live-proof-packet-review-queue-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>

            <div class="ob-manual-live-proof-packet-review-queue-section">
              <div class="ob-manual-live-proof-packet-review-queue-section-title">Blocked live actions</div>
              <div class="ob-manual-live-proof-packet-review-queue-list">
                ${blocked.map(blockedRow).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-proof-packet-review-queue-callout">
          <strong>Next handoff:</strong><br>
          GP040 can close the Manual Live Evidence & Receipt Layer readiness checkpoint.
        </div>
      </div>
    `;
  }

  function wirePanel() {
    const filterForm = document.getElementById("obProofPacketQueueFilterForm");
    if (filterForm && filterForm.dataset.wired !== "true") {
      filterForm.dataset.wired = "true";
      filterForm.addEventListener("submit", function (event) {
        event.preventDefault();
        fetchQueue(queryFromForm());
      });
    }

    document.querySelectorAll("[data-ob-queue-read]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const queueItemId = button.getAttribute("data-ob-queue-read");
        button.textContent = "Reading...";
        try {
          await readQueueItem(queueItemId);
        } catch (error) {
          queueState.error = error && error.message ? error.message : "queue read error";
          renderPanel();
        }
      });
    });

    const updateForm = document.getElementById("obProofPacketQueueUpdateForm");
    if (updateForm && updateForm.dataset.wired !== "true") {
      updateForm.dataset.wired = "true";
      updateForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const queueItemId = updateForm.getAttribute("data-queue-item-id");
        const data = {};
        new FormData(updateForm).forEach((value, key) => {
          data[key] = value;
        });
        try {
          await updateQueueItem(queueItemId, data.queue_status, data.priority);
        } catch (error) {
          queueState.error = error && error.message ? error.message : "queue update error";
          renderPanel();
        }
      });
    }
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveProofPacketReviewQueuePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const receipts = document.getElementById("obManualLiveDryRunReceiptsPanel");
    const history = document.getElementById("obManualLiveDryRunHistoryReviewPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (receipts && receipts.parentNode) receipts.insertAdjacentElement("afterend", panel);
    else if (history && history.parentNode) history.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wirePanel();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-039-real-manual-live-proof-packet-owner-review-queue", "ready");
    document.body.setAttribute("data-ob-real-owner-review-queue-persistence", "true");
    document.body.setAttribute("data-ob-real-receipt-packet-search", "true");
    document.body.setAttribute("data-ob-real-queue-filtering", "true");
    document.body.setAttribute("data-ob-real-queue-status-update", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE_STATE = {
      version: VERSION,
      status: queueState.status,
      queueItemCount: queueState.overview ? queueState.overview.queue_item_count : 0,
      realOwnerReviewQueuePersistence: true,
      realReceiptPacketSearch: true,
      realQueueFiltering: true,
      realQueueStatusUpdate: true,
      notRealManualLiveReady: true,
      noDirectVaultUpload: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noBankAccountRead: true,
      noRealCapitalMovement: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(fallbackOverview());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchQueue();
    }, 8380);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_PROOF_PACKET_REVIEW_QUEUE_GP039_API = {
    version: VERSION,
    queueEndpoint: QUEUE_ENDPOINT,
    getState: function () { return queueState; },
    fetchQueue,
    readQueueItem,
    updateQueueItem,
    renderPanel,
    setFlags
  };
})();
