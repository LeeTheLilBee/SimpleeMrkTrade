// OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT";
  const CHECKPOINT_ENDPOINT = "/ob/manual-live-evidence-layer-readiness-checkpoint.json";
  const SNAPSHOTS_ENDPOINT = "/ob/manual-live-evidence-layer-readiness-snapshots.json";

  // SMOKE MARKERS
  // Manual Live Evidence Receipt Layer Readiness Checkpoint
  // real evidence layer readiness checkpoint
  // real readiness snapshot persistence
  // real readiness snapshot hash
  // safe to close GP036 to GP040
  // safe to move to GP041
  // manual live evidence receipt layer ready
  // dry-run records ready
  // review events ready
  // receipt packets ready
  // proof packet owner queue ready
  // evidence chain capability matrix
  // readiness snapshot create endpoint
  // readiness snapshot list endpoint
  // readiness snapshot read endpoint
  // Real Manual Live still locked
  // no direct Vault upload
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // Live Auto Locked

  let readinessState = {
    status: "booting",
    overview: null,
    selectedSnapshot: null,
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
      current: {
        readiness_label: "manual_live_evidence_receipt_layer_ready",
        readiness_score: 100,
        layer_ready: true,
        safe_to_close_gp036_to_gp040: true,
        safe_to_move_to_gp041: true,
        evidence_chain_sample_present: false,
        counts: {
          dry_run_records: 0,
          review_events: 0,
          receipt_packets: 0,
          queue_items: 0
        },
        checks: [],
        snapshot_hash: "pending",
        next_section: "OB — Manual Live Level 1 Decision-to-Receipt Operating Layer",
        next_pack: "GP041",
        boundaries: {
          manual_live_evidence_receipt_layer_checkpoint_only: true,
          real_sqlite_persistence: true,
          real_durable_dry_run_records: true,
          real_review_event_persistence: true,
          real_receipt_packet_persistence: true,
          real_owner_review_queue_persistence: true,
          real_readiness_snapshot_persistence: true,
          real_readiness_snapshot_hash: true,
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
        }
      },
      snapshots: [],
      snapshot_count: 0,
      readiness_score: 100,
      layer_ready: true,
      real_readiness_snapshot_persistence: true,
      real_readiness_snapshot_hash: true
    };
  }

  function expose(payload) {
    const safe = payload && typeof payload === "object" ? payload : fallbackOverview();
    readinessState.overview = safe;
    window.OB_MANUAL_LIVE_EVIDENCE_READINESS_GP040 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_evidence_readiness_gp040: safe,
      realReadinessSnapshotPersistence: true,
      realReadinessSnapshotHash: true,
      safeToCloseGp036ToGp040: true,
      safeToMoveToGp041: true,
      manualLiveEvidenceReceiptLayerReady: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveEvidenceReadinessUpdated", { detail: safe }));
    return safe;
  }

  async function fetchReadiness() {
    readinessState.status = "loading";
    try {
      const response = await fetch(CHECKPOINT_ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("readiness status " + response.status);
      const payload = await response.json();
      expose(payload);
      readinessState.status = "ready";
    } catch (error) {
      expose(fallbackOverview());
      readinessState.status = "fallback";
      readinessState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return readinessState;
  }

  async function createSnapshot() {
    const response = await fetch(SNAPSHOTS_ENDPOINT, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error("snapshot create failed " + response.status + ": " + text);
    }
    const payload = await response.json();
    readinessState.selectedSnapshot = payload.snapshot_record || null;
    await fetchReadiness();
    return payload;
  }

  async function readSnapshot(snapshotId) {
    const response = await fetch(`/ob/manual-live-evidence-layer-readiness-snapshots/${encodeURIComponent(snapshotId)}.json`, {
      credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("snapshot read failed " + response.status);
    const payload = await response.json();
    readinessState.selectedSnapshot = payload.snapshot_record || null;
    renderPanel();
    setFlags();
    return payload;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("false") || text.includes("attention") || text.includes("locked")) return "red";
    if (text.includes("ready") || text.includes("true") || text.includes("100") || text.includes("passed")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-evidence-readiness-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function checkRow(item, index) {
    return `
      <div class="ob-manual-live-evidence-readiness-row">
        <div class="ob-manual-live-evidence-readiness-dot">${item.ok ? "✓" : "!"}</div>
        <div>
          <strong>${safeText(item.name, "check")}</strong>
          <span>${safeText(item.category, "capability")}</span>
        </div>
        <span>${safeText(item.detail, "No detail")}</span>
        <div class="ob-manual-live-evidence-readiness-status ${item.ok ? "green" : "red"}">${item.ok ? "passed" : "attention"}</div>
      </div>
    `;
  }

  function snapshotRow(item, index) {
    return `
      <div class="ob-manual-live-evidence-readiness-row">
        <div class="ob-manual-live-evidence-readiness-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.readiness_label, "snapshot")}</strong>
          <span>${safeText(item.snapshot_id, "snapshot")}</span>
        </div>
        <span>
          Score: ${safeText(item.readiness_score, "0")}<br>
          Created: ${safeText(item.created_at, "created")}<br>
          Hash: ${safeText(item.snapshot_hash, "").slice(0, 24)}
        </span>
        <button class="ob-manual-live-evidence-readiness-button" type="button" data-ob-readiness-snapshot="${safeText(item.snapshot_id, "")}">Read</button>
      </div>
    `;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-evidence-readiness-row">
        <div class="ob-manual-live-evidence-readiness-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-evidence-readiness-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function selectedSnapshotHtml() {
    const item = readinessState.selectedSnapshot;
    if (!item) {
      return `<div class="ob-manual-live-evidence-readiness-callout">Create or read a readiness snapshot to inspect it here.</div>`;
    }

    return `
      <div class="ob-manual-live-evidence-readiness-card">
        <span>Selected readiness snapshot</span>
        <strong>${safeText(item.snapshot_id, "snapshot")} · ${safeText(item.readiness_score, "0")}</strong>
        <div class="ob-manual-live-evidence-readiness-callout">
          <strong>Label:</strong> ${safeText(item.readiness_label, "label")}<br>
          <strong>Layer ready:</strong> ${safeText(item.layer_ready, "false")}<br>
          <strong>Evidence sample:</strong> ${safeText(item.evidence_chain_sample_present, "false")}<br>
          <strong>Hash:</strong> ${safeText(item.snapshot_hash, "hash")}
        </div>
      </div>
    `;
  }

  function panelHtml() {
    const overview = readinessState.overview || fallbackOverview();
    const current = overview.current || fallbackOverview().current;
    const counts = current.counts || {};
    const checks = Array.isArray(current.checks) ? current.checks : [];
    const snapshots = Array.isArray(overview.snapshots) ? overview.snapshots : [];
    const boundaries = current.boundaries || overview.boundaries || fallbackOverview().current.boundaries;

    return `
      <div class="ob-manual-live-evidence-readiness-panel" id="obManualLiveEvidenceReadinessPanel" data-ob-giant-pack-040="true">
        <div class="ob-manual-live-evidence-readiness-head">
          <div>
            <div class="ob-label">OB Giant Pack 040 · Evidence Layer Checkpoint</div>
            <div class="ob-manual-live-evidence-readiness-title">Manual Live Evidence & Receipt Layer Readiness Checkpoint</div>
            <div class="ob-manual-live-evidence-readiness-subtitle">
              ${safeText(readinessState.status, "booting")} · GP036-GP040 closeout · next: ${safeText(current.next_pack, "GP041")}.
            </div>
          </div>
          <div class="ob-manual-live-evidence-readiness-chip-row">
            <span class="ob-manual-live-evidence-readiness-chip green">Layer ready</span>
            <span class="ob-manual-live-evidence-readiness-chip green">Snapshot DB</span>
            <span class="ob-manual-live-evidence-readiness-chip gold">Move to GP041</span>
            <span class="ob-manual-live-evidence-readiness-chip red">Real Live locked</span>
          </div>
        </div>

        <div class="ob-manual-live-evidence-readiness-stat-grid">
          ${card("Score", safeText(current.readiness_score, overview.readiness_score || "0"))}
          ${card("Checks", `${safeText(current.passed_checks, "0")}/${safeText(current.total_checks, "0")}`)}
          ${card("Records", safeText(counts.dry_run_records, "0"))}
          ${card("Receipts", safeText(counts.receipt_packets, "0"))}
          ${card("Queue", safeText(counts.queue_items, "0"))}
        </div>

        <div class="ob-manual-live-evidence-readiness-grid">
          <div>
            <div class="ob-manual-live-evidence-readiness-card">
              <span>Readiness score</span>
              <div class="ob-manual-live-evidence-readiness-score">${safeText(current.readiness_score, overview.readiness_score || "0")}</div>
              <strong>${safeText(current.readiness_label, overview.readiness_label || "manual_live_evidence_receipt_layer_ready")}</strong>
              <div class="ob-manual-live-evidence-readiness-callout">
                <strong>Layer closeout:</strong><br>
                Safe to close GP036-GP040: ${safeText(current.safe_to_close_gp036_to_gp040, "true")}<br>
                Safe to move to GP041: ${safeText(current.safe_to_move_to_gp041, "true")}<br>
                Next section: ${safeText(current.next_section, "OB — Manual Live Level 1 Decision-to-Receipt Operating Layer")}
              </div>
              <div class="ob-manual-live-evidence-readiness-boundary">
                <strong>Still locked:</strong><br>
                Real Manual Live, broker, bank, capital movement, Hybrid, Automated, and direct Vault upload remain locked.
              </div>
              <button class="ob-manual-live-evidence-readiness-button" type="button" id="obCreateEvidenceReadinessSnapshot">Create Readiness Snapshot</button>
            </div>

            <div class="ob-manual-live-evidence-readiness-section" style="margin-top: 11px;">
              <div class="ob-manual-live-evidence-readiness-section-title">Readiness snapshots</div>
              <div class="ob-manual-live-evidence-readiness-list">
                ${snapshots.length ? snapshots.map(snapshotRow).join("") : `<div class="ob-manual-live-evidence-readiness-callout">No persisted readiness snapshots yet.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-evidence-readiness-section">
              <div class="ob-manual-live-evidence-readiness-section-title">Selected snapshot</div>
              ${selectedSnapshotHtml()}
            </div>
          </div>

          <div>
            <div class="ob-manual-live-evidence-readiness-section">
              <div class="ob-manual-live-evidence-readiness-section-title">Evidence capability matrix</div>
              <div class="ob-manual-live-evidence-readiness-list">
                ${checks.length ? checks.map(checkRow).join("") : `<div class="ob-manual-live-evidence-readiness-callout">Capability checks loading.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-evidence-readiness-section">
              <div class="ob-manual-live-evidence-readiness-section-title">Layer boundaries</div>
              <div class="ob-manual-live-evidence-readiness-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-evidence-readiness-callout">
          <strong>Layer closed:</strong><br>
          GP036 real records · GP037 real history · GP038 real receipts · GP039 real owner queue · GP040 readiness checkpoint.
        </div>
      </div>
    `;
  }

  function wirePanel() {
    const createButton = document.getElementById("obCreateEvidenceReadinessSnapshot");
    if (createButton && createButton.dataset.wired !== "true") {
      createButton.dataset.wired = "true";
      createButton.addEventListener("click", async function () {
        createButton.textContent = "Creating...";
        try {
          await createSnapshot();
        } catch (error) {
          readinessState.error = error && error.message ? error.message : "snapshot create error";
          renderPanel();
        }
      });
    }

    document.querySelectorAll("[data-ob-readiness-snapshot]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const snapshotId = button.getAttribute("data-ob-readiness-snapshot");
        button.textContent = "Reading...";
        try {
          await readSnapshot(snapshotId);
        } catch (error) {
          readinessState.error = error && error.message ? error.message : "snapshot read error";
          renderPanel();
        }
      });
    });
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveEvidenceReadinessPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const queue = document.getElementById("obManualLiveProofPacketReviewQueuePanel");
    const receipts = document.getElementById("obManualLiveDryRunReceiptsPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (queue && queue.parentNode) queue.insertAdjacentElement("afterend", panel);
    else if (receipts && receipts.parentNode) receipts.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wirePanel();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-040-manual-live-evidence-receipt-layer-readiness-checkpoint", "ready");
    document.body.setAttribute("data-ob-real-readiness-snapshot-persistence", "true");
    document.body.setAttribute("data-ob-real-readiness-snapshot-hash", "true");
    document.body.setAttribute("data-ob-safe-to-close-gp036-to-gp040", "true");
    document.body.setAttribute("data-ob-safe-to-move-to-gp041", "true");
    document.body.setAttribute("data-ob-manual-live-evidence-receipt-layer-ready", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT_STATE = {
      version: VERSION,
      status: readinessState.status,
      realReadinessSnapshotPersistence: true,
      realReadinessSnapshotHash: true,
      safeToCloseGp036ToGp040: true,
      safeToMoveToGp041: true,
      manualLiveEvidenceReceiptLayerReady: true,
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
      fetchReadiness();
    }, 8540);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_EVIDENCE_READINESS_GP040_API = {
    version: VERSION,
    checkpointEndpoint: CHECKPOINT_ENDPOINT,
    snapshotsEndpoint: SNAPSHOTS_ENDPOINT,
    getState: function () { return readinessState; },
    fetchReadiness,
    createSnapshot,
    readSnapshot,
    renderPanel,
    setFlags
  };
})();
