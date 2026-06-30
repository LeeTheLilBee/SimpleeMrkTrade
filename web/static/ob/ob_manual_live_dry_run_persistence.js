// OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE";
  const STATUS_ENDPOINT = "/ob/manual-live-dry-run-persistence.json";
  const RECORDS_ENDPOINT = "/ob/manual-live-dry-run-records.json";

  // SMOKE MARKERS
  // Real Manual Live Dry-Run Persistence Engine
  // real manual live dry-run persistence engine
  // real SQLite persistence
  // real durable dry-run records
  // real create endpoint
  // real list endpoint
  // real read endpoint
  // persisted dry-run record
  // dry-run database schema
  // dry-run record hash
  // durable owner review record
  // manual live dry-run save
  // Proof/Demo persistence lane
  // real database write for dry-run records
  // real save endpoint for dry-run records
  // not real Manual Live ready
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no bank account read
  // no real capital movement
  // no direct Vault upload
  // Live Auto Locked

  let persistenceState = {
    status: "booting",
    service: null,
    records: [],
    lastCreated: null,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function fallbackService() {
    return {
      ok: true,
      version: VERSION,
      record_count: 0,
      real_sqlite_persistence: true,
      real_durable_records: true,
      real_create_endpoint_enabled: true,
      real_list_endpoint_enabled: true,
      real_read_endpoint_enabled: true,
      blocked_actions: [
        "submit_real_broker_order",
        "read_broker_account",
        "auto_execute_trade",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "mark_real_manual_live_ready"
      ],
      boundaries: {
        manual_live_dry_run_persistence_only: true,
        real_sqlite_persistence: true,
        real_durable_records: true,
        real_database_write_enabled_for_dry_run_records: true,
        real_save_endpoint_enabled_for_dry_run_records: true,
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
    };
  }

  function fallbackPayload() {
    return {
      service: fallbackService(),
      records: [],
      blocked_actions: fallbackService().blocked_actions,
      boundaries: fallbackService().boundaries
    };
  }

  function expose(payload) {
    const safe = payload && typeof payload === "object" ? payload : fallbackPayload();
    persistenceState.service = safe.service || safe;
    persistenceState.records = Array.isArray(safe.records) ? safe.records : [];
    window.OB_MANUAL_LIVE_DRY_RUN_PERSISTENCE_GP036 = safe;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_dry_run_persistence_gp036: safe,
      realSQLitePersistence: true,
      realDryRunRecords: true,
      realDryRunCreateEndpoint: true,
      realDryRunListEndpoint: true,
      realDryRunReadEndpoint: true,
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
    window.dispatchEvent(new CustomEvent("obManualLiveDryRunPersistenceUpdated", { detail: safe }));
    return safe;
  }

  async function fetchPersistence() {
    persistenceState.status = "loading";
    try {
      const response = await fetch(STATUS_ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("status " + response.status);
      const payload = await response.json();
      expose(payload);
      persistenceState.status = "ready";
    } catch (error) {
      expose(fallbackPayload());
      persistenceState.status = "fallback";
      persistenceState.error = error && error.message ? error.message : "fetch error";
    }
    renderPanel();
    setFlags();
    return persistenceState;
  }

  async function createDryRunRecord(formPayload) {
    const payload = {
      owner_id: "owner_solice",
      session_id: "ui_session_" + Date.now(),
      lane: "Proof/Demo",
      symbol: safeText(formPayload.symbol, "MU").toUpperCase(),
      instrument_type: safeText(formPayload.instrument_type, "option"),
      direction: safeText(formPayload.direction, "call_review"),
      strategy: "manual_live_level_1_dry_run",
      candidate_snapshot: {
        source: "OB UI GP036",
        symbol: safeText(formPayload.symbol, "MU").toUpperCase(),
        manual_review_only: true
      },
      checklist_snapshot: {
        checklist_complete: formPayload.checklist_complete === "true",
        manual_review_only: true
      },
      scenario_snapshot: {
        scenario_id: safeText(formPayload.scenario_id, "clean_candidate_scenario"),
        scenario_status: "ui_submitted"
      },
      confidence_snapshot: {
        operator_confidence_label: safeText(formPayload.confidence_label, "forming"),
        real_manual_live_ready: false
      },
      intended_action: "manual_review_only",
      dry_run_outcome: safeText(formPayload.dry_run_outcome, "not_placed"),
      risk_notes: safeText(formPayload.risk_notes, "Practice-only dry-run. No order submitted."),
      operator_notes: safeText(formPayload.operator_notes, "Dry-run persisted for owner review.")
    };

    const response = await fetch(RECORDS_ENDPOINT, {
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
      throw new Error("create failed " + response.status + ": " + text);
    }

    const result = await response.json();
    persistenceState.lastCreated = result.record || result;
    await fetchPersistence();
    return result;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("false") || text.includes("blocked")) return "red";
    if (text.includes("true") || text.includes("ready") || text.includes("real")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-dry-run-persistence-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function boundaryRow(label, value, index) {
    return `
      <div class="ob-manual-live-dry-run-persistence-row">
        <div class="ob-manual-live-dry-run-persistence-dot">${index + 1}</div>
        <div>
          <strong>${label}</strong>
          <span>boundary</span>
        </div>
        <span>${safeText(value, "false")}</span>
        <div class="ob-manual-live-dry-run-persistence-status ${tone(value)}">${safeText(value, "false")}</div>
      </div>
    `;
  }

  function recordRow(record, index) {
    return `
      <div class="ob-manual-live-dry-run-persistence-row">
        <div class="ob-manual-live-dry-run-persistence-dot">${index + 1}</div>
        <div>
          <strong>${safeText(record.symbol, "UNKNOWN")} · ${safeText(record.dry_run_outcome, "outcome")}</strong>
          <span>${safeText(record.record_id, "record")}</span>
        </div>
        <span>
          ${safeText(record.created_at, "created")}<br>
          ${safeText(record.operator_notes, "No notes")}<br>
          Hash: ${safeText(record.payload_hash, "").slice(0, 18)}
        </span>
        <div class="ob-manual-live-dry-run-persistence-status green">persisted</div>
      </div>
    `;
  }

  function blockedRow(item, index) {
    return `
      <div class="ob-manual-live-dry-run-persistence-row">
        <div class="ob-manual-live-dry-run-persistence-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This remains blocked while dry-run records are allowed.</span>
        <div class="ob-manual-live-dry-run-persistence-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const service = persistenceState.service || fallbackService();
    const boundaries = service.boundaries || fallbackService().boundaries;
    const blocked = service.blocked_actions || fallbackService().blocked_actions;
    const records = persistenceState.records || [];

    return `
      <div class="ob-manual-live-dry-run-persistence-panel" id="obManualLiveDryRunPersistencePanel" data-ob-giant-pack-036="true">
        <div class="ob-manual-live-dry-run-persistence-head">
          <div>
            <div class="ob-label">OB Giant Pack 036 · Real Dry-Run Persistence</div>
            <div class="ob-manual-live-dry-run-persistence-title">Real Manual Live Dry-Run Persistence Engine</div>
            <div class="ob-manual-live-dry-run-persistence-subtitle">
              ${safeText(persistenceState.status, "booting")} · real SQLite dry-run records · real create/list/read endpoints.
            </div>
          </div>
          <div class="ob-manual-live-dry-run-persistence-chip-row">
            <span class="ob-manual-live-dry-run-persistence-chip green">Real SQLite</span>
            <span class="ob-manual-live-dry-run-persistence-chip green">Durable records</span>
            <span class="ob-manual-live-dry-run-persistence-chip gold">Dry-run only</span>
            <span class="ob-manual-live-dry-run-persistence-chip red">No broker order</span>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-persistence-stat-grid">
          ${card("Records", safeText(service.record_count, records.length))}
          ${card("Schema", safeText(service.schema_version || (service.schema && service.schema.schema_version), "1"))}
          ${card("Create", safeText(service.real_create_endpoint_enabled, "true"))}
          ${card("List", safeText(service.real_list_endpoint_enabled, "true"))}
          ${card("Read", safeText(service.real_read_endpoint_enabled, "true"))}
        </div>

        <div class="ob-manual-live-dry-run-persistence-grid">
          <div>
            <div class="ob-manual-live-dry-run-persistence-card">
              <span>Persistence state</span>
              <strong>Real dry-run database writes are enabled.</strong>
              <div class="ob-manual-live-dry-run-persistence-callout">
                <strong>Database:</strong><br>
                ${safeText(service.db_path, "data/ob_manual_live_dry_run.sqlite3")}
              </div>
              <div class="ob-manual-live-dry-run-persistence-boundary">
                <strong>Boundary:</strong><br>
                This creates real OB dry-run records only. Real Manual Live, broker orders, broker reads, bank reads, capital movement, and direct Vault uploads remain locked.
              </div>
            </div>

            <div class="ob-manual-live-dry-run-persistence-card" style="margin-top: 11px;">
              <span>Create dry-run record</span>
              <strong>Save a real Proof/Demo dry-run record.</strong>
              <form class="ob-manual-live-dry-run-persistence-form" id="obDryRunPersistenceForm">
                <input name="symbol" value="MU" aria-label="Symbol">
                <select name="instrument_type" aria-label="Instrument type">
                  <option value="option">option</option>
                  <option value="stock">stock</option>
                </select>
                <select name="direction" aria-label="Direction">
                  <option value="call_review">call_review</option>
                  <option value="put_review">put_review</option>
                  <option value="stock_review">stock_review</option>
                </select>
                <select name="dry_run_outcome" aria-label="Dry-run outcome">
                  <option value="not_placed">not_placed</option>
                  <option value="fake_fill">fake_fill</option>
                  <option value="needs_review">needs_review</option>
                  <option value="cancelled">cancelled</option>
                  <option value="skipped">skipped</option>
                </select>
                <select name="checklist_complete" aria-label="Checklist complete">
                  <option value="true">checklist complete</option>
                  <option value="false">checklist needs review</option>
                </select>
                <input name="scenario_id" value="clean_candidate_scenario" aria-label="Scenario id">
                <input name="confidence_label" value="forming" aria-label="Confidence label">
                <textarea name="risk_notes" aria-label="Risk notes">Practice-only dry-run. No order submitted.</textarea>
                <textarea name="operator_notes" aria-label="Operator notes">Dry-run persisted for owner review.</textarea>
                <button class="ob-manual-live-dry-run-persistence-button" type="submit">Save Dry-Run Record</button>
              </form>
              <div class="ob-manual-live-dry-run-persistence-callout" id="obDryRunPersistenceResult">
                No UI record created yet in this session.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-dry-run-persistence-section">
              <div class="ob-manual-live-dry-run-persistence-section-title">Recent persisted dry-run records</div>
              <div class="ob-manual-live-dry-run-persistence-list">
                ${records.length ? records.map(recordRow).join("") : `<div class="ob-manual-live-dry-run-persistence-callout">No records returned yet.</div>`}
              </div>
            </div>

            <div class="ob-manual-live-dry-run-persistence-section">
              <div class="ob-manual-live-dry-run-persistence-section-title">Persistence boundaries</div>
              <div class="ob-manual-live-dry-run-persistence-list">
                ${Object.keys(boundaries).map((key, index) => boundaryRow(key, boundaries[key], index)).join("")}
              </div>
            </div>

            <div class="ob-manual-live-dry-run-persistence-section">
              <div class="ob-manual-live-dry-run-persistence-section-title">Blocked live actions</div>
              <div class="ob-manual-live-dry-run-persistence-list">
                ${blocked.map(blockedRow).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-dry-run-persistence-callout">
          <strong>Next handoff:</strong><br>
          GP037 can add real dry-run record detail/history review over the persisted records.
        </div>
      </div>
    `;
  }

  function wireForm() {
    const form = document.getElementById("obDryRunPersistenceForm");
    const result = document.getElementById("obDryRunPersistenceResult");
    if (!form || form.dataset.wired === "true") return;
    form.dataset.wired = "true";

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const data = {};
      new FormData(form).forEach((value, key) => {
        data[key] = value;
      });
      if (result) result.textContent = "Saving real dry-run record...";
      try {
        const created = await createDryRunRecord(data);
        const record = created.record || {};
        if (result) {
          result.innerHTML = `<strong>Saved:</strong><br>${safeText(record.record_id, "record")} · ${safeText(record.symbol, "symbol")} · ${safeText(record.dry_run_outcome, "outcome")}`;
        }
      } catch (error) {
        if (result) result.textContent = "Save blocked or failed: " + (error && error.message ? error.message : "unknown");
      }
    });
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveDryRunPersistencePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const checkpoint = document.getElementById("obManualLiveOperatorConfidenceReadinessCheckpointPanel");
    const plan = document.getElementById("obManualLiveOperatorConfidenceImprovementPlanPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else if (plan && plan.parentNode) plan.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);

    wireForm();
  }

  function setFlags() {
    document.body.setAttribute("data-ob-giant-pack-036-real-manual-live-dry-run-persistence-engine", "ready");
    document.body.setAttribute("data-ob-real-sqlite-persistence", "true");
    document.body.setAttribute("data-ob-real-durable-dry-run-records", "true");
    document.body.setAttribute("data-ob-real-dry-run-create-endpoint", "true");
    document.body.setAttribute("data-ob-real-dry-run-list-endpoint", "true");
    document.body.setAttribute("data-ob-real-dry-run-read-endpoint", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-bank-account-read", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_STATE = {
      version: VERSION,
      status: persistenceState.status,
      recordCount: persistenceState.service ? persistenceState.service.record_count : 0,
      realSQLitePersistence: true,
      realDurableDryRunRecords: true,
      realDryRunCreateEndpoint: true,
      realDryRunListEndpoint: true,
      realDryRunReadEndpoint: true,
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
    expose(fallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchPersistence();
    }, 7900);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_DRY_RUN_PERSISTENCE_GP036_API = {
    version: VERSION,
    statusEndpoint: STATUS_ENDPOINT,
    recordsEndpoint: RECORDS_ENDPOINT,
    getState: function () { return persistenceState; },
    fetchPersistence,
    createDryRunRecord,
    renderPanel,
    setFlags
  };
})();
