// OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF_JS

(function () {
  const VERSION = "OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF";
  const HANDOFF_ENDPOINT = "/ob/manual-live-candidate-decision-handoffs.json";

  // SMOKE MARKERS
  // Real Candidate-to-Decision Handoff
  // real candidate decision handoff persistence
  // real candidate payload fingerprint
  // real owner decision state
  // candidate-to-owner-decision status
  // decision-to-receipt operating layer started
  // candidate handoff create endpoint
  // candidate handoff list endpoint
  // candidate handoff read endpoint
  // candidate handoff update endpoint
  // queued for owner decision
  // owner reviewing candidate
  // decided not placed
  // decided fake fill
  // needs review
  // blocked live candidate
  // Real Manual Live still locked
  // no direct Vault upload
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // Live Auto Locked

  let handoffState = {
    status: "booting",
    overview: null,
    selectedHandoff: null,
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
      handoffs: [],
      handoff_count: 0,
      status_counts: {},
      symbol_counts: {},
      source_counts: {},
      real_candidate_decision_handoff_persistence: true,
      real_candidate_payload_fingerprint: true,
      real_owner_decision_state: true,
      next_expected_step: "GP042 — Real Checklist-to-Record Save Flow",
      section: "OB — Manual Live Level 1 Decision-to-Receipt Operating Layer",
      boundaries: {
        manual_live_candidate_to_decision_handoff_only: true,
        decision_to_receipt_operating_layer_started: true,
        real_sqlite_persistence: true,
        real_candidate_decision_handoff_persistence: true,
        real_candidate_payload_fingerprint: true,
        real_owner_decision_state: true,
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
    handoffState.overview = safe;
    window.OB_MANUAL_LIVE_CANDIDATE_DECISION_HANDOFF_GP041 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_candidate_decision_handoff_gp041: safe,
      realCandidateDecisionHandoffPersistence: true,
      realCandidatePayloadFingerprint: true,
      realOwnerDecisionState: true,
      decisionToReceiptOperatingLayerStarted: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveCandidateDecisionHandoffUpdated", { detail: safe }));
    return safe;
  }

  function queryFromForm() {
    const form = document.getElementById("obCandidateHandoffFilterForm");
    if (!form) return "";
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => {
      if (String(value || "").trim()) params.set(key, String(value).trim());
    });
    return params.toString();
  }

  async function fetchHandoffs(queryString) {
    handoffState.status = "loading";
    try {
      const query = queryString || queryFromForm();
      const response = await fetch(HANDOFF_ENDPOINT + (query ? "?" + query : ""), {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("handoff status " + response.status);
      const payload = await response.json();
      expose(payload);
      handoffState.status = "ready";
    } catch (error) {
      expose(fallbackOverview());
      handoffState.status = "fallback";
      handoffState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return handoffState;
  }

  async function createHandoff(formPayload) {
    const candidate = {
      symbol: safeText(formPayload.symbol, "MU").toUpperCase(),
      candidate_id: safeText(formPayload.candidate_id, "owner_entered_candidate"),
      candidate_source: safeText(formPayload.candidate_source, "owner_manual_entry"),
      strategy: safeText(formPayload.strategy, "manual_live_review"),
      direction: safeText(formPayload.direction, "watch"),
      score: Number(formPayload.score || 0),
      confidence: safeText(formPayload.confidence, "owner_review_required"),
      notes: safeText(formPayload.notes, "Owner-created candidate handoff.")
    };

    const response = await fetch(HANDOFF_ENDPOINT, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        owner_id: "owner_solice",
        lane: "Manual Live Level 1",
        decision_status: "queued_for_owner_decision",
        decision_intent: "review_candidate",
        handoff_reason: safeText(formPayload.handoff_reason, `Candidate ${candidate.symbol} queued for owner decision review.`),
        candidate
      })
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error("handoff create failed " + response.status + ": " + text);
    }

    const payload = await response.json();
    handoffState.selectedHandoff = payload.handoff || null;
    await fetchHandoffs();
    return payload;
  }

  async function readHandoff(handoffId) {
    const response = await fetch(`/ob/manual-live-candidate-decision-handoffs/${encodeURIComponent(handoffId)}.json`, {
      credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("handoff read failed " + response.status);
    const payload = await response.json();
    handoffState.selectedHandoff = payload.handoff || null;
    renderPanel();
    setFlags();
    return payload;
  }

  async function updateHandoff(handoffId, decisionStatus, decisionIntent) {
    const response = await fetch(`/ob/manual-live-candidate-decision-handoffs/${encodeURIComponent(handoffId)}.json`, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        decision_status: decisionStatus,
        decision_intent: decisionIntent,
        handoff_reason: "Owner updated candidate decision handoff from OB UI."
      })
    });
    if (!response.ok) throw new Error("handoff update failed " + response.status);
    const payload = await response.json();
    handoffState.selectedHandoff = payload.handoff || null;
    await fetchHandoffs();
    return payload;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("false") || text.includes("need") || text.includes("locked")) return "red";
    if (text.includes("clean") || text.includes("true") || text.includes("ready") || text.includes("decided")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-candidate-handoff-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function handoffRow(item, index) {
    return `
      <div class="ob-manual-live-candidate-handoff-row">
        <div class="ob-manual-live-candidate-handoff-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.symbol, "UNKNOWN")} · ${safeText(item.decision_status, "status")}</strong>
          <span>${safeText(item.candidate_source, "source")} · ${safeText(item.candidate_strategy, "strategy")}</span>
        </div>
        <span>
          Candidate: ${safeText(item.candidate_id, "candidate")}<br>
          Intent: ${safeText(item.decision_intent, "intent")}<br>
          Reason: ${safeText(item.handoff_reason, "reason")}<br>
          Hash: ${safeText(item.handoff_hash, "").slice(0, 24)}
        </span>
        <button class="ob-manual-live-candidate-handoff-button" type="button" data-ob-candidate-handoff-read="${safeText(item.handoff_id, "")}">Detail</button>
      </div>
    `;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-candidate-handoff-row">
        <div class="ob-manual-live-candidate-handoff-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-candidate-handoff-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function selectedHandoffHtml() {
    const item = handoffState.selectedHandoff;
    if (!item) {
      return `<div class="ob-manual-live-candidate-handoff-callout">Select or create a candidate handoff to inspect it here.</div>`;
    }

    return `
      <div class="ob-manual-live-candidate-handoff-card">
        <span>Selected candidate handoff</span>
        <strong>${safeText(item.symbol, "UNKNOWN")} · ${safeText(item.decision_status, "status")}</strong>
        <div class="ob-manual-live-candidate-handoff-callout">
          <strong>Handoff:</strong> ${safeText(item.handoff_id, "handoff")}<br>
          <strong>Candidate:</strong> ${safeText(item.candidate_id, "candidate")}<br>
          <strong>Fingerprint:</strong> ${safeText(item.candidate_fingerprint, "fingerprint")}<br>
          <strong>Handoff hash:</strong> ${safeText(item.handoff_hash, "hash")}<br>
          <strong>Linked evidence record:</strong> ${safeText(item.linked_evidence_record_id, "none")}<br>
          <strong>Linked receipt packet:</strong> ${safeText(item.linked_receipt_packet_id, "none")}
        </div>

        <form class="ob-manual-live-candidate-handoff-form" id="obCandidateHandoffUpdateForm" data-handoff-id="${safeText(item.handoff_id, "")}">
          <select name="decision_status" aria-label="Decision status">
            <option value="queued_for_owner_decision">queued_for_owner_decision</option>
            <option value="owner_reviewing">owner_reviewing</option>
            <option value="decided_not_placed">decided_not_placed</option>
            <option value="decided_fake_fill">decided_fake_fill</option>
            <option value="needs_review">needs_review</option>
            <option value="blocked_live">blocked_live</option>
            <option value="archived">archived</option>
          </select>
          <select name="decision_intent" aria-label="Decision intent">
            <option value="review_candidate">review_candidate</option>
            <option value="create_evidence_record_next">create_evidence_record_next</option>
            <option value="create_receipt_after_record">create_receipt_after_record</option>
            <option value="watch_only">watch_only</option>
            <option value="blocked_live_review">blocked_live_review</option>
          </select>
          <button class="ob-manual-live-candidate-handoff-button" type="submit">Update Handoff</button>
        </form>

        <div class="ob-manual-live-candidate-handoff-boundary">
          <strong>Still locked:</strong><br>
          Updating this handoff does not place orders, read brokers, move money, or upload directly to Vault.
        </div>
      </div>
    `;
  }

  function panelHtml() {
    const overview = handoffState.overview || fallbackOverview();
    const items = Array.isArray(overview.handoffs) ? overview.handoffs : [];
    const boundaries = overview.boundaries || fallbackOverview().boundaries;
    const statusCounts = overview.status_counts || {};
    const symbolCounts = overview.symbol_counts || {};

    return `
      <div class="ob-manual-live-candidate-handoff-panel" id="obManualLiveCandidateHandoffPanel" data-ob-giant-pack-041="true">
        <div class="ob-manual-live-candidate-handoff-head">
          <div>
            <div class="ob-label">OB Giant Pack 041 · Decision-to-Receipt Layer</div>
            <div class="ob-manual-live-candidate-handoff-title">Real Candidate-to-Decision Handoff</div>
            <div class="ob-manual-live-candidate-handoff-subtitle">
              ${safeText(handoffState.status, "booting")} · persisted candidate handoffs · real owner decision state.
            </div>
          </div>
          <div class="ob-manual-live-candidate-handoff-chip-row">
            <span class="ob-manual-live-candidate-handoff-chip green">Real handoff DB</span>
            <span class="ob-manual-live-candidate-handoff-chip green">Payload fingerprint</span>
            <span class="ob-manual-live-candidate-handoff-chip gold">Owner decision</span>
            <span class="ob-manual-live-candidate-handoff-chip red">Real Live locked</span>
          </div>
        </div>

        <div class="ob-manual-live-candidate-handoff-stat-grid">
          ${card("Handoffs", safeText(overview.handoff_count, items.length))}
          ${card("Queued", safeText(statusCounts.queued_for_owner_decision || 0, "0"))}
          ${card("Reviewing", safeText(statusCounts.owner_reviewing || 0, "0"))}
          ${card("Blocked", safeText(statusCounts.blocked_live || 0, "0"))}
          ${card("Symbols", safeText(Object.keys(symbolCounts).length, "0"))}
        </div>

        <div class="ob-manual-live-candidate-handoff-grid">
          <div>
            <div class="ob-manual-live-candidate-handoff-card">
              <span>Operating layer state</span>
              <strong>Decision-to-Receipt Operating Layer has started.</strong>
              <div class="ob-manual-live-candidate-handoff-callout">
                <strong>What is real:</strong><br>
                Candidate handoff rows, payload fingerprints, handoff hashes, owner decision status, search/list/read/update endpoints.
              </div>
              <div class="ob-manual-live-candidate-handoff-boundary">
                <strong>Boundary:</strong><br>
                This captures owner decision intent only. It does not create broker orders or unlock live trading.
              </div>
            </div>

            <div class="ob-manual-live-candidate-handoff-card" style="margin-top: 11px;">
              <span>Create candidate handoff</span>
              <form class="ob-manual-live-candidate-handoff-form" id="obCandidateHandoffCreateForm">
                <input name="symbol" placeholder="Symbol, e.g. MU" value="MU" aria-label="Symbol">
                <input name="candidate_id" placeholder="Candidate ID" value="owner_manual_candidate_mu" aria-label="Candidate ID">
                <input name="candidate_source" placeholder="Source" value="owner_manual_entry" aria-label="Candidate source">
                <input name="strategy" placeholder="Strategy" value="manual_live_review" aria-label="Strategy">
                <input name="direction" placeholder="Direction" value="watch" aria-label="Direction">
                <input name="score" placeholder="Score" value="82" aria-label="Score">
                <input name="confidence" placeholder="Confidence" value="owner_review_required" aria-label="Confidence">
                <textarea name="handoff_reason" aria-label="Handoff reason">Candidate queued for owner Manual Live decision review.</textarea>
                <button class="ob-manual-live-candidate-handoff-button" type="submit">Create Handoff</button>
              </form>
            </div>

            <div class="ob-manual-live-candidate-handoff-card" style="margin-top: 11px;">
              <span>Search / filter handoffs</span>
              <form class="ob-manual-live-candidate-handoff-form" id="obCandidateHandoffFilterForm">
                <input name="q" placeholder="Search symbol, candidate, source, reason" aria-label="Search">
                <input name="symbol" placeholder="Symbol" aria-label="Symbol">
                <select name="decision_status" aria-label="Decision status">
                  <option value="">any status</option>
                  <option value="queued_for_owner_decision">queued_for_owner_decision</option>
                  <option value="owner_reviewing">owner_reviewing</option>
                  <option value="decided_not_placed">decided_not_placed</option>
                  <option value="decided_fake_fill">decided_fake_fill</option>
                  <option value="needs_review">needs_review</option>
                  <option value="blocked_live">blocked_live</option>
                  <option value="archived">archived</option>
                </select>
                <button class="ob-manual-live-candidate-handoff-button" type="submit">Apply Filters</button>
              </form>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-candidate-handoff-section">
              <div class="ob-manual-live-candidate-handoff-section-title">Candidate handoffs</div>
              <div class="ob-manual-live-candidate-handoff-list">
                ${items.length ? items.map(handoffRow).join("") : `<div class="ob-manual-live-candidate-handoff-callout">No candidate handoffs yet.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-candidate-handoff-section">
              <div class="ob-manual-live-candidate-handoff-section-title">Selected handoff</div>
              ${selectedHandoffHtml()}
            </div>

            <div class="ob-manual-live-candidate-handoff-section">
              <div class="ob-manual-live-candidate-handoff-section-title">Handoff boundaries</div>
              <div class="ob-manual-live-candidate-handoff-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-candidate-handoff-callout">
          <strong>Next handoff:</strong><br>
          GP042 can build real checklist-to-record save flow from candidate handoff into the evidence record layer.
        </div>
      </div>
    `;
  }

  function wirePanel() {
    const createForm = document.getElementById("obCandidateHandoffCreateForm");
    if (createForm && createForm.dataset.wired !== "true") {
      createForm.dataset.wired = "true";
      createForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const data = {};
        new FormData(createForm).forEach((value, key) => {
          data[key] = value;
        });
        try {
          await createHandoff(data);
        } catch (error) {
          handoffState.error = error && error.message ? error.message : "handoff create error";
          renderPanel();
        }
      });
    }

    const filterForm = document.getElementById("obCandidateHandoffFilterForm");
    if (filterForm && filterForm.dataset.wired !== "true") {
      filterForm.dataset.wired = "true";
      filterForm.addEventListener("submit", function (event) {
        event.preventDefault();
        fetchHandoffs(queryFromForm());
      });
    }

    document.querySelectorAll("[data-ob-candidate-handoff-read]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const handoffId = button.getAttribute("data-ob-candidate-handoff-read");
        button.textContent = "Reading...";
        try {
          await readHandoff(handoffId);
        } catch (error) {
          handoffState.error = error && error.message ? error.message : "handoff read error";
          renderPanel();
        }
      });
    });

    const updateForm = document.getElementById("obCandidateHandoffUpdateForm");
    if (updateForm && updateForm.dataset.wired !== "true") {
      updateForm.dataset.wired = "true";
      updateForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const handoffId = updateForm.getAttribute("data-handoff-id");
        const data = {};
        new FormData(updateForm).forEach((value, key) => {
          data[key] = value;
        });
        try {
          await updateHandoff(handoffId, data.decision_status, data.decision_intent);
        } catch (error) {
          handoffState.error = error && error.message ? error.message : "handoff update error";
          renderPanel();
        }
      });
    }
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveCandidateHandoffPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const readiness = document.getElementById("obManualLiveEvidenceReadinessPanel");
    const queue = document.getElementById("obManualLiveProofPacketReviewQueuePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (readiness && readiness.parentNode) readiness.insertAdjacentElement("afterend", panel);
    else if (queue && queue.parentNode) queue.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wirePanel();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-041-real-candidate-to-decision-handoff", "ready");
    document.body.setAttribute("data-ob-real-candidate-decision-handoff-persistence", "true");
    document.body.setAttribute("data-ob-real-candidate-payload-fingerprint", "true");
    document.body.setAttribute("data-ob-real-owner-decision-state", "true");
    document.body.setAttribute("data-ob-decision-to-receipt-operating-layer-started", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF_STATE = {
      version: VERSION,
      status: handoffState.status,
      realCandidateDecisionHandoffPersistence: true,
      realCandidatePayloadFingerprint: true,
      realOwnerDecisionState: true,
      decisionToReceiptOperatingLayerStarted: true,
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
      fetchHandoffs();
    }, 8700);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_CANDIDATE_DECISION_HANDOFF_GP041_API = {
    version: VERSION,
    handoffEndpoint: HANDOFF_ENDPOINT,
    getState: function () { return handoffState; },
    fetchHandoffs,
    createHandoff,
    readHandoff,
    updateHandoff,
    renderPanel,
    setFlags
  };
})();
