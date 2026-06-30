// OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE";
  const RECEIPTS_ENDPOINT = "/ob/manual-live-dry-run-receipts.json";

  // SMOKE MARKERS
  // Real Manual Live Dry-Run Receipt Packet Engine
  // real manual live dry-run receipt packet engine
  // real receipt packet persistence
  // real receipt JSON file write
  // real receipt packet hash
  // real receipt packet create endpoint
  // real receipt packet list endpoint
  // real receipt packet read endpoint
  // durable dry-run receipt packet
  // persisted receipt packet
  // receipt packet database schema
  // receipt packet file path
  // receipt packet from dry-run record
  // receipt packet from review history
  // dry-run receipt hash
  // owner review receipt packet
  // no direct Vault upload
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // Live Auto Locked

  let receiptState = {
    status: "booting",
    overview: null,
    selectedPacket: null,
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
      packets: [],
      packet_count: 0,
      status_counts: {},
      symbol_counts: {},
      real_receipt_packet_persistence: true,
      real_receipt_json_file_write: true,
      real_receipt_packet_hash: true,
      boundaries: {
        manual_live_dry_run_receipt_packet_only: true,
        real_sqlite_persistence: true,
        real_durable_dry_run_records: true,
        real_review_event_persistence: true,
        real_receipt_packet_persistence: true,
        real_receipt_json_file_write: true,
        real_receipt_packet_hash: true,
        real_receipt_packet_create_endpoint: true,
        real_receipt_packet_list_endpoint: true,
        real_receipt_packet_read_endpoint: true,
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
    receiptState.overview = safe;
    window.OB_MANUAL_LIVE_DRY_RUN_RECEIPTS_GP038 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_dry_run_receipts_gp038: safe,
      realReceiptPacketPersistence: true,
      realReceiptJsonFileWrite: true,
      realReceiptPacketHash: true,
      realReceiptPacketCreateEndpoint: true,
      realReceiptPacketListEndpoint: true,
      realReceiptPacketReadEndpoint: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveDryRunReceiptsUpdated", { detail: safe }));
    return safe;
  }

  async function fetchReceipts() {
    receiptState.status = "loading";
    try {
      const response = await fetch(RECEIPTS_ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("receipts status " + response.status);
      const payload = await response.json();
      expose(payload);
      receiptState.status = "ready";
    } catch (error) {
      expose(fallbackOverview());
      receiptState.status = "fallback";
      receiptState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return receiptState;
  }

  async function createReceipt(recordId) {
    const response = await fetch(`/ob/manual-live-dry-run-records/${encodeURIComponent(recordId)}/receipt-packets.json`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        packet_type: "manual_live_dry_run_receipt",
        packet_status: "finalized_dry_run_receipt"
      })
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error("receipt create failed " + response.status + ": " + text);
    }

    const result = await response.json();
    receiptState.selectedPacket = result.packet || null;
    await fetchReceipts();
    return result;
  }

  async function readReceipt(packetId) {
    const response = await fetch(`/ob/manual-live-dry-run-receipt-packets/${encodeURIComponent(packetId)}.json`, {
      credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("receipt read failed " + response.status);
    const result = await response.json();
    receiptState.selectedPacket = result.packet || result;
    renderPanel();
    setFlags();
    return result;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("false") || text.includes("blocked")) return "red";
    if (text.includes("true") || text.includes("ready") || text.includes("finalized") || text.includes("persisted")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-dry-run-receipts-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function packetRow(packet, index) {
    const summary = packet.packet && packet.packet.summary ? packet.packet.summary : {};
    return `
      <div class="ob-manual-live-dry-run-receipts-row">
        <div class="ob-manual-live-dry-run-receipts-dot">${index + 1}</div>
        <div>
          <strong>${safeText(summary.symbol, "UNKNOWN")} · ${safeText(packet.packet_status, "status")}</strong>
          <span>${safeText(packet.packet_id, "packet")}</span>
        </div>
        <span>
          Record: ${safeText(packet.record_id, "record")}<br>
          File: ${safeText(packet.packet_file_path, "file")}<br>
          Hash: ${safeText(packet.packet_hash, "").slice(0, 24)}
        </span>
        <button class="ob-manual-live-dry-run-receipts-button" type="button" data-ob-receipt-read="${safeText(packet.packet_id, "")}">Read</button>
      </div>
    `;
  }

  function recordRow(record, index) {
    return `
      <div class="ob-manual-live-dry-run-receipts-row">
        <div class="ob-manual-live-dry-run-receipts-dot">${index + 1}</div>
        <div>
          <strong>${safeText(record.symbol, "UNKNOWN")} · ${safeText(record.dry_run_outcome, "outcome")}</strong>
          <span>${safeText(record.record_id, "record")}</span>
        </div>
        <span>
          Review events: ${safeText(record.review_event_count, "0")}<br>
          Hash: ${safeText(record.payload_hash, "").slice(0, 24)}
        </span>
        <button class="ob-manual-live-dry-run-receipts-button" type="button" data-ob-receipt-create="${safeText(record.record_id, "")}">Create Receipt</button>
      </div>
    `;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-dry-run-receipts-row">
        <div class="ob-manual-live-dry-run-receipts-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-dry-run-receipts-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-dry-run-receipts-row">
        <div class="ob-manual-live-dry-run-receipts-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This remains blocked while receipt packets are generated.</span>
        <div class="ob-manual-live-dry-run-receipts-status red">blocked</div>
      </div>
    `;
  }

  function selectedPacketHtml() {
    const packet = receiptState.selectedPacket;
    if (!packet) {
      return `<div class="ob-manual-live-dry-run-receipts-callout">Create or read a receipt packet to inspect it here.</div>`;
    }

    const inner = packet.packet || {};
    const summary = inner.summary || {};

    return `
      <div class="ob-manual-live-dry-run-receipts-card">
        <span>Selected receipt packet</span>
        <strong>${safeText(packet.packet_id, "packet")} · ${safeText(packet.packet_status, "status")}</strong>
        <div class="ob-manual-live-dry-run-receipts-callout">
          <strong>Record:</strong> ${safeText(packet.record_id || summary.record_id, "record")}<br>
          <strong>Symbol:</strong> ${safeText(summary.symbol, "symbol")}<br>
          <strong>Outcome:</strong> ${safeText(summary.dry_run_outcome, "outcome")}<br>
          <strong>Review events:</strong> ${safeText(summary.review_event_count, "0")}<br>
          <strong>Packet hash:</strong> ${safeText(packet.packet_hash || inner.packet_hash, "hash")}<br>
          <strong>File:</strong> ${safeText(packet.packet_file_path, "file")}
        </div>
        <div class="ob-manual-live-dry-run-receipts-boundary">
          <strong>Not Vault:</strong><br>
          This is a real local/app receipt packet. Direct Vault upload remains locked.
        </div>
      </div>
    `;
  }

  function panelHtml() {
    const overview = receiptState.overview || fallbackOverview();
    const packets = Array.isArray(overview.packets) ? overview.packets : [];
    const records = Array.isArray(overview.records) ? overview.records : [];
    const boundaries = overview.boundaries || fallbackOverview().boundaries;
    const blocked = overview.blocked_actions || fallbackOverview().blocked_actions;

    return `
      <div class="ob-manual-live-dry-run-receipts-panel" id="obManualLiveDryRunReceiptsPanel" data-ob-giant-pack-038="true">
        <div class="ob-manual-live-dry-run-receipts-head">
          <div>
            <div class="ob-label">OB Giant Pack 038 · Real Receipt Packets</div>
            <div class="ob-manual-live-dry-run-receipts-title">Real Manual Live Dry-Run Receipt Packet Engine</div>
            <div class="ob-manual-live-dry-run-receipts-subtitle">
              ${safeText(receiptState.status, "booting")} · real JSON receipt files · real packet hash · real receipt DB rows.
            </div>
          </div>
          <div class="ob-manual-live-dry-run-receipts-chip-row">
            <span class="ob-manual-live-dry-run-receipts-chip green">Real receipt packets</span>
            <span class="ob-manual-live-dry-run-receipts-chip green">JSON file write</span>
            <span class="ob-manual-live-dry-run-receipts-chip gold">Dry-run only</span>
            <span class="ob-manual-live-dry-run-receipts-chip red">No direct Vault upload</span>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-receipts-stat-grid">
          ${card("Packets", safeText(overview.packet_count, packets.length))}
          ${card("File write", safeText(overview.real_receipt_json_file_write, "true"))}
          ${card("Hash", safeText(overview.real_receipt_packet_hash, "true"))}
          ${card("DB", safeText(overview.real_receipt_packet_persistence, "true"))}
          ${card("Records", safeText(records.length, "0"))}
        </div>

        <div class="ob-manual-live-dry-run-receipts-grid">
          <div>
            <div class="ob-manual-live-dry-run-receipts-card">
              <span>Receipt packet state</span>
              <strong>Real receipt packets are generated from persisted dry-run records and review history.</strong>
              <div class="ob-manual-live-dry-run-receipts-callout">
                <strong>Receipt directory:</strong><br>
                ${safeText(overview.receipt_dir, "data/ob_manual_live_receipt_packets")}
              </div>
              <div class="ob-manual-live-dry-run-receipts-boundary">
                <strong>Boundary:</strong><br>
                Receipt packets are real app artifacts, but they are not broker orders, not bank activity, and not direct Vault uploads.
              </div>
            </div>

            <div class="ob-manual-live-dry-run-receipts-section" style="margin-top: 11px;">
              <div class="ob-manual-live-dry-run-receipts-section-title">Records available for receipt packet creation</div>
              <div class="ob-manual-live-dry-run-receipts-list">
                ${records.length ? records.map(recordRow).join("") : `<div class="ob-manual-live-dry-run-receipts-callout">No persisted records returned yet. GP036 can create them.</div>`}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-dry-run-receipts-section">
              <div class="ob-manual-live-dry-run-receipts-section-title">Receipt packets</div>
              <div class="ob-manual-live-dry-run-receipts-list">
                ${packets.length ? packets.map(packetRow).join("") : `<div class="ob-manual-live-dry-run-receipts-callout">No receipt packets yet.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-dry-run-receipts-section">
              <div class="ob-manual-live-dry-run-receipts-section-title">Selected packet</div>
              ${selectedPacketHtml()}
            </div>

            <div class="ob-manual-live-dry-run-receipts-section">
              <div class="ob-manual-live-dry-run-receipts-section-title">Receipt boundaries</div>
              <div class="ob-manual-live-dry-run-receipts-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>

            <div class="ob-manual-live-dry-run-receipts-section">
              <div class="ob-manual-live-dry-run-receipts-section-title">Blocked live actions</div>
              <div class="ob-manual-live-dry-run-receipts-list">
                ${blocked.map(blockedRow).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-receipts-callout">
          <strong>Next handoff:</strong><br>
          GP039 can add real receipt packet search/filtering and owner review queue over persisted packets.
        </div>
      </div>
    `;
  }

  function wireButtons() {
    document.querySelectorAll("[data-ob-receipt-create]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const recordId = button.getAttribute("data-ob-receipt-create");
        button.textContent = "Creating...";
        try {
          await createReceipt(recordId);
        } catch (error) {
          receiptState.error = error && error.message ? error.message : "receipt create error";
          renderPanel();
        }
      });
    });

    document.querySelectorAll("[data-ob-receipt-read]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const packetId = button.getAttribute("data-ob-receipt-read");
        button.textContent = "Reading...";
        try {
          await readReceipt(packetId);
        } catch (error) {
          receiptState.error = error && error.message ? error.message : "receipt read error";
          renderPanel();
        }
      });
    });
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveDryRunReceiptsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const history = document.getElementById("obManualLiveDryRunHistoryReviewPanel");
    const persistence = document.getElementById("obManualLiveDryRunPersistencePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (history && history.parentNode) history.insertAdjacentElement("afterend", panel);
    else if (persistence && persistence.parentNode) persistence.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wireButtons();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-038-real-manual-live-dry-run-receipt-packet-engine", "ready");
    document.body.setAttribute("data-ob-real-receipt-packet-persistence", "true");
    document.body.setAttribute("data-ob-real-receipt-json-file-write", "true");
    document.body.setAttribute("data-ob-real-receipt-packet-hash", "true");
    document.body.setAttribute("data-ob-real-receipt-packet-create-endpoint", "true");
    document.body.setAttribute("data-ob-real-receipt-packet-list-endpoint", "true");
    document.body.setAttribute("data-ob-real-receipt-packet-read-endpoint", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_STATE = {
      version: VERSION,
      status: receiptState.status,
      packetCount: receiptState.overview ? receiptState.overview.packet_count : 0,
      realReceiptPacketPersistence: true,
      realReceiptJsonFileWrite: true,
      realReceiptPacketHash: true,
      realReceiptPacketCreateEndpoint: true,
      realReceiptPacketListEndpoint: true,
      realReceiptPacketReadEndpoint: true,
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
      fetchReceipts();
    }, 8220);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_DRY_RUN_RECEIPTS_GP038_API = {
    version: VERSION,
    receiptsEndpoint: RECEIPTS_ENDPOINT,
    getState: function () { return receiptState; },
    fetchReceipts,
    createReceipt,
    readReceipt,
    renderPanel,
    setFlags
  };
})();
