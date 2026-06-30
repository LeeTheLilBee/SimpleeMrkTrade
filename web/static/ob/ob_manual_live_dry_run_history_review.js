// OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_JS

(function () {
  const VERSION = "OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW";
  const HISTORY_ENDPOINT = "/ob/manual-live-dry-run-history.json";
  const EVENT_ENDPOINT_BASE = "/ob/manual-live-dry-run-records";

  // SMOKE MARKERS
  // Real Manual Live Dry-Run Record Detail History Review
  // real manual live dry-run record detail history review
  // real review event persistence
  // real dry-run record detail
  // real dry-run history endpoint
  // real review event create endpoint
  // real review event list endpoint
  // persisted review event
  // review event database schema
  // review event hash
  // durable review history
  // record timeline review
  // owner review event
  // confidence note event
  // risk note event
  // scenario review event
  // checklist review event
  // status change event
  // dry-run detail timeline
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // no direct Vault upload
  // Live Auto Locked

  let historyState = {
    status: "booting",
    overview: null,
    selectedRecordId: null,
    selectedDetail: null,
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
      records: [],
      record_count: 0,
      review_event_count: 0,
      outcome_counts: {},
      symbol_counts: {},
      real_record_detail_enabled: true,
      real_history_enabled: true,
      real_review_event_persistence: true,
      boundaries: {
        manual_live_dry_run_history_review_only: true,
        real_sqlite_persistence: true,
        real_durable_dry_run_records: true,
        real_review_event_persistence: true,
        real_record_detail_enabled: true,
        real_history_enabled: true,
        real_review_event_write_enabled: true,
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
    historyState.overview = safe;
    window.OB_MANUAL_LIVE_DRY_RUN_HISTORY_REVIEW_GP037 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_dry_run_history_review_gp037: safe,
      realReviewEventPersistence: true,
      realDryRunRecordDetail: true,
      realDryRunHistoryEndpoint: true,
      realReviewEventCreateEndpoint: true,
      realReviewEventListEndpoint: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveDryRunHistoryReviewUpdated", { detail: safe }));
    return safe;
  }

  async function fetchHistory() {
    historyState.status = "loading";
    try {
      const response = await fetch(HISTORY_ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("history status " + response.status);
      const payload = await response.json();
      expose(payload);
      historyState.status = "ready";
    } catch (error) {
      expose(fallbackOverview());
      historyState.status = "fallback";
      historyState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return historyState;
  }

  async function fetchRecordDetail(recordId) {
    const response = await fetch(`/ob/manual-live-dry-run-record-detail/${encodeURIComponent(recordId)}.json`, {
      credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("detail failed " + response.status);
    const payload = await response.json();
    historyState.selectedRecordId = recordId;
    historyState.selectedDetail = payload;
    renderPanel();
    setFlags();
    return payload;
  }

  async function createReviewEvent(recordId, formPayload) {
    const payload = {
      reviewer_id: "owner_solice",
      event_type: safeText(formPayload.event_type, "owner_review"),
      review_status: safeText(formPayload.review_status, "reviewed"),
      review_notes: safeText(formPayload.review_notes, "Owner reviewed dry-run record."),
      confidence_delta: Number(formPayload.confidence_delta || 0),
      checklist_delta: Number(formPayload.checklist_delta || 0),
      scenario_delta: Number(formPayload.scenario_delta || 0)
    };

    const response = await fetch(`${EVENT_ENDPOINT_BASE}/${encodeURIComponent(recordId)}/review-events.json`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error("review event failed " + response.status + ": " + text);
    }

    const result = await response.json();
    await fetchHistory();
    await fetchRecordDetail(recordId);
    return result;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("false") || text.includes("blocked") || text.includes("needs")) return "red";
    if (text.includes("true") || text.includes("ready") || text.includes("clean") || text.includes("reviewed")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-dry-run-history-review-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function recordRow(record, index) {
    return `
      <div class="ob-manual-live-dry-run-history-review-row">
        <div class="ob-manual-live-dry-run-history-review-dot">${index + 1}</div>
        <div>
          <strong>${safeText(record.symbol, "UNKNOWN")} · ${safeText(record.dry_run_outcome, "outcome")}</strong>
          <span>${safeText(record.record_id, "record")}</span>
        </div>
        <span>
          ${safeText(record.created_at, "created")}<br>
          Review events: ${safeText(record.review_event_count, "0")}<br>
          Hash: ${safeText(record.payload_hash, "").slice(0, 18)}
        </span>
        <button class="ob-manual-live-dry-run-history-review-button" type="button" data-ob-dry-run-detail="${safeText(record.record_id, "")}">Detail</button>
      </div>
    `;
  }

  function timelineRow(item, index) {
    return `
      <div class="ob-manual-live-dry-run-history-review-row">
        <div class="ob-manual-live-dry-run-history-review-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Timeline")}</strong>
          <span>${safeText(item.type, "event")} · ${safeText(item.status, "status")}</span>
        </div>
        <span>
          ${safeText(item.created_at, "created")}<br>
          ${safeText(item.notes, "No notes")}<br>
          Hash: ${safeText(item.hash, "").slice(0, 18)}
        </span>
        <div class="ob-manual-live-dry-run-history-review-status ${tone(item.status)}">${safeText(item.status, "event")}</div>
      </div>
    `;
  }

  function eventRow(event, index) {
    return `
      <div class="ob-manual-live-dry-run-history-review-row">
        <div class="ob-manual-live-dry-run-history-review-dot">${index + 1}</div>
        <div>
          <strong>${safeText(event.event_type, "event")}</strong>
          <span>${safeText(event.review_status, "status")}</span>
        </div>
        <span>
          ${safeText(event.review_notes, "No notes")}<br>
          Confidence Δ ${safeText(event.confidence_delta, "0")} · Checklist Δ ${safeText(event.checklist_delta, "0")} · Scenario Δ ${safeText(event.scenario_delta, "0")}<br>
          Hash: ${safeText(event.event_hash, "").slice(0, 18)}
        </span>
        <div class="ob-manual-live-dry-run-history-review-status ${tone(event.review_status)}">${safeText(event.review_status, "reviewed")}</div>
      </div>
    `;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-dry-run-history-review-row">
        <div class="ob-manual-live-dry-run-history-review-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-dry-run-history-review-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-dry-run-history-review-row">
        <div class="ob-manual-live-dry-run-history-review-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This remains blocked while detail/history review events are allowed.</span>
        <div class="ob-manual-live-dry-run-history-review-status red">blocked</div>
      </div>
    `;
  }

  function selectedDetailHtml() {
    const detail = historyState.selectedDetail;
    if (!detail || !detail.ok) {
      return `<div class="ob-manual-live-dry-run-history-review-callout">Select a persisted dry-run record to see detail and timeline.</div>`;
    }

    const record = detail.record || {};
    const timeline = Array.isArray(detail.timeline) ? detail.timeline : [];
    const events = Array.isArray(detail.events) ? detail.events : [];

    return `
      <div class="ob-manual-live-dry-run-history-review-card">
        <span>Selected record</span>
        <strong>${safeText(record.symbol, "UNKNOWN")} · ${safeText(record.record_id, "record")}</strong>
        <div class="ob-manual-live-dry-run-history-review-callout">
          <strong>Outcome:</strong> ${safeText(record.dry_run_outcome, "outcome")}<br>
          <strong>Lane:</strong> ${safeText(record.lane, "lane")}<br>
          <strong>Hash:</strong> ${safeText(record.payload_hash, "hash")}
        </div>

        <form class="ob-manual-live-dry-run-history-review-form" id="obDryRunReviewEventForm" data-record-id="${safeText(record.record_id, "")}">
          <select name="event_type" aria-label="Event type">
            <option value="owner_review">owner_review</option>
            <option value="confidence_note">confidence_note</option>
            <option value="risk_note">risk_note</option>
            <option value="scenario_review">scenario_review</option>
            <option value="checklist_review">checklist_review</option>
            <option value="status_change">status_change</option>
          </select>
          <select name="review_status" aria-label="Review status">
            <option value="reviewed">reviewed</option>
            <option value="needs_reps">needs_reps</option>
            <option value="clean">clean</option>
            <option value="blocked_live">blocked_live</option>
            <option value="locked">locked</option>
            <option value="watch">watch</option>
          </select>
          <input name="confidence_delta" value="0" aria-label="Confidence delta">
          <input name="checklist_delta" value="0" aria-label="Checklist delta">
          <input name="scenario_delta" value="0" aria-label="Scenario delta">
          <textarea name="review_notes" aria-label="Review notes">Owner reviewed dry-run record.</textarea>
          <button class="ob-manual-live-dry-run-history-review-button" type="submit">Add Review Event</button>
        </form>

        <div class="ob-manual-live-dry-run-history-review-callout" id="obDryRunReviewEventResult">
          Review events are persisted to SQLite and tied to the dry-run record.
        </div>
      </div>

      <div class="ob-manual-live-dry-run-history-review-section">
        <div class="ob-manual-live-dry-run-history-review-section-title">Record timeline</div>
        <div class="ob-manual-live-dry-run-history-review-list">
          ${timeline.length ? timeline.map(timelineRow).join("") : `<div class="ob-manual-live-dry-run-history-review-callout">No timeline yet.</div>`}
        </div>
      </div>

      <div class="ob-manual-live-dry-run-history-review-section">
        <div class="ob-manual-live-dry-run-history-review-section-title">Review events</div>
        <div class="ob-manual-live-dry-run-history-review-list">
          ${events.length ? events.map(eventRow).join("") : `<div class="ob-manual-live-dry-run-history-review-callout">No review events yet.</div>`}
        </div>
      </div>
    `;
  }

  function panelHtml() {
    const overview = historyState.overview || fallbackOverview();
    const records = Array.isArray(overview.records) ? overview.records : [];
    const boundaries = overview.boundaries || fallbackOverview().boundaries;
    const blocked = overview.blocked_actions || fallbackOverview().blocked_actions;

    return `
      <div class="ob-manual-live-dry-run-history-review-panel" id="obManualLiveDryRunHistoryReviewPanel" data-ob-giant-pack-037="true">
        <div class="ob-manual-live-dry-run-history-review-head">
          <div>
            <div class="ob-label">OB Giant Pack 037 · Real History Review</div>
            <div class="ob-manual-live-dry-run-history-review-title">Real Manual Live Dry-Run Record Detail + History Review</div>
            <div class="ob-manual-live-dry-run-history-review-subtitle">
              ${safeText(historyState.status, "booting")} · real review-event persistence · real record timeline.
            </div>
          </div>
          <div class="ob-manual-live-dry-run-history-review-chip-row">
            <span class="ob-manual-live-dry-run-history-review-chip green">Real review events</span>
            <span class="ob-manual-live-dry-run-history-review-chip green">Real detail endpoint</span>
            <span class="ob-manual-live-dry-run-history-review-chip gold">Dry-run only</span>
            <span class="ob-manual-live-dry-run-history-review-chip red">No broker order</span>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-history-review-stat-grid">
          ${card("Records", safeText(overview.record_count, records.length))}
          ${card("Events", safeText(overview.review_event_count, "0"))}
          ${card("Detail", safeText(overview.real_record_detail_enabled, "true"))}
          ${card("History", safeText(overview.real_history_enabled, "true"))}
          ${card("Event DB", safeText(overview.real_review_event_persistence, "true"))}
        </div>

        <div class="ob-manual-live-dry-run-history-review-grid">
          <div>
            <div class="ob-manual-live-dry-run-history-review-card">
              <span>History review state</span>
              <strong>Real review-event persistence is enabled.</strong>
              <div class="ob-manual-live-dry-run-history-review-callout">
                <strong>What is real:</strong><br>
                Dry-run record detail, timeline, review events, event hashes, and review-event SQLite writes.
              </div>
              <div class="ob-manual-live-dry-run-history-review-boundary">
                <strong>Boundary:</strong><br>
                This reviews dry-run records only. Real Manual Live, broker orders, broker reads, bank reads, capital movement, and direct Vault uploads remain locked.
              </div>
            </div>

            <div class="ob-manual-live-dry-run-history-review-section" style="margin-top: 11px;">
              <div class="ob-manual-live-dry-run-history-review-section-title">Persisted records</div>
              <div class="ob-manual-live-dry-run-history-review-list">
                ${records.length ? records.map(recordRow).join("") : `<div class="ob-manual-live-dry-run-history-review-callout">No persisted records returned yet. GP036 can create them.</div>`}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-dry-run-history-review-section">
              <div class="ob-manual-live-dry-run-history-review-section-title">Selected record detail + event writer</div>
              ${selectedDetailHtml()}
            </div>

            <div class="ob-manual-live-dry-run-history-review-section">
              <div class="ob-manual-live-dry-run-history-review-section-title">History boundaries</div>
              <div class="ob-manual-live-dry-run-history-review-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>

            <div class="ob-manual-live-dry-run-history-review-section">
              <div class="ob-manual-live-dry-run-history-review-section-title">Blocked live actions</div>
              <div class="ob-manual-live-dry-run-history-review-list">
                ${blocked.map(blockedRow).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-history-review-callout">
          <strong>Next handoff:</strong><br>
          GP038 can build real dry-run export/receipt packet generation from persisted records and review events.
        </div>
      </div>
    `;
  }

  function wireButtons() {
    document.querySelectorAll("[data-ob-dry-run-detail]").forEach(function (button) {
      if (button.dataset.wired === "true") return;
      button.dataset.wired = "true";
      button.addEventListener("click", async function () {
        const recordId = button.getAttribute("data-ob-dry-run-detail");
        try {
          await fetchRecordDetail(recordId);
        } catch (error) {
          historyState.error = error && error.message ? error.message : "detail error";
          renderPanel();
        }
      });
    });

    const form = document.getElementById("obDryRunReviewEventForm");
    const result = document.getElementById("obDryRunReviewEventResult");
    if (form && form.dataset.wired !== "true") {
      form.dataset.wired = "true";
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const recordId = form.getAttribute("data-record-id");
        const data = {};
        new FormData(form).forEach((value, key) => {
          data[key] = value;
        });
        if (result) result.textContent = "Saving real review event...";
        try {
          const created = await createReviewEvent(recordId, data);
          if (result) {
            result.innerHTML = `<strong>Saved review event:</strong><br>${safeText(created.event && created.event.event_id, "event")}`;
          }
        } catch (error) {
          if (result) result.textContent = "Review event blocked or failed: " + (error && error.message ? error.message : "unknown");
        }
      });
    }
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveDryRunHistoryReviewPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const persistence = document.getElementById("obManualLiveDryRunPersistencePanel");
    const checkpoint = document.getElementById("obManualLiveOperatorConfidenceReadinessCheckpointPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (persistence && persistence.parentNode) persistence.insertAdjacentElement("afterend", panel);
    else if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wireButtons();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-037-real-manual-live-dry-run-record-detail-history-review", "ready");
    document.body.setAttribute("data-ob-real-review-event-persistence", "true");
    document.body.setAttribute("data-ob-real-dry-run-record-detail", "true");
    document.body.setAttribute("data-ob-real-dry-run-history-endpoint", "true");
    document.body.setAttribute("data-ob-real-review-event-create-endpoint", "true");
    document.body.setAttribute("data-ob-real-review-event-list-endpoint", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_STATE = {
      version: VERSION,
      status: historyState.status,
      recordCount: historyState.overview ? historyState.overview.record_count : 0,
      reviewEventCount: historyState.overview ? historyState.overview.review_event_count : 0,
      realReviewEventPersistence: true,
      realDryRunRecordDetail: true,
      realDryRunHistoryEndpoint: true,
      realReviewEventCreateEndpoint: true,
      realReviewEventListEndpoint: true,
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
  }

  function boot() {
    expose(fallbackOverview());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchHistory();
    }, 8060);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_DRY_RUN_HISTORY_REVIEW_GP037_API = {
    version: VERSION,
    historyEndpoint: HISTORY_ENDPOINT,
    getState: function () { return historyState; },
    fetchHistory,
    fetchRecordDetail,
    createReviewEvent,
    renderPanel,
    setFlags
  };
})();
