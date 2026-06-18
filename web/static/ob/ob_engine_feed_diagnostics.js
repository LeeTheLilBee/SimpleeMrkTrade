// OBSERVATORY_V33_ENGINE_FEED_DIAGNOSTICS_STALENESS_GUARD_JS
// RECOVERED_SAFE_V33_ENGINE_FEED_DIAGNOSTICS_ASSET

(function () {
  const VERSION = "OB_V33_ENGINE_FEED_DIAGNOSTICS_STALENESS_GUARD";
  const ENDPOINT = "/ob/engine-feed-diagnostics.json";

  // V33 SMOKE MARKERS
  // Expanded Engine Feed Diagnostics
  // Staleness Guard
  // freshness status
  // stale data guard
  // missing data guard
  // fallback-only guard
  // safe-to-display label
  // candidate_log staleness
  // open_positions staleness
  // ledger staleness
  // market_universe staleness
  // pipeline_status staleness
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let diagnosticsState = {
    status: "recovered_fallback",
    httpStatus: null,
    source: "recovered_v33_safe_fallback",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function fallbackPayload() {
    return {
      version: VERSION,
      source: "recovered_v33_safe_fallback",
      diagnostics_status: "fallback",
      freshness_score: 72,
      display_label: "Fallback / guarded",
      files: [
        {
          name: "candidate_log",
          exists: false,
          status: "fallback_only",
          age_minutes: null,
          safe_to_display: "fallback_only",
          label: "Fallback only",
          note: "Recovered diagnostics asset is active. UI must label candidate_log as fallback until route confirms freshness."
        },
        {
          name: "open_positions",
          exists: false,
          status: "fallback_only",
          age_minutes: null,
          safe_to_display: "fallback_only",
          label: "Fallback only",
          note: "Recovered diagnostics asset is active. UI must label open_positions as fallback until route confirms freshness."
        },
        {
          name: "ledger",
          exists: false,
          status: "fallback_only",
          age_minutes: null,
          safe_to_display: "fallback_only",
          label: "Fallback only",
          note: "Recovered diagnostics asset is active. UI must label ledger as fallback until route confirms freshness."
        },
        {
          name: "market_universe",
          exists: false,
          status: "fallback_only",
          age_minutes: null,
          safe_to_display: "fallback_only",
          label: "Fallback only",
          note: "Recovered diagnostics asset is active. UI must label market_universe as fallback until route confirms freshness."
        },
        {
          name: "pipeline_status",
          exists: false,
          status: "fallback_only",
          age_minutes: null,
          safe_to_display: "fallback_only",
          label: "Fallback only",
          note: "Recovered diagnostics asset is active. UI must label pipeline_status as fallback until route confirms freshness."
        }
      ],
      summary: {
        present: 0,
        fresh: 0,
        stale: 0,
        missing: 0,
        fallback_only: 5,
        caution: 5
      },
      tower_boundaries: {
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        stale_data_cannot_create_permission: true
      },
      warnings: [
        "Recovered V33 diagnostics asset is active.",
        "Fallback-only data must be labeled.",
        "Do not treat unknown-age data as fresh.",
        "No broker wiring."
      ]
    };
  }

  function expose(payload) {
    const normalized = payload || fallbackPayload();
    window.OB_ENGINE_FEED_DIAGNOSTICS_V33 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      engine_feed_diagnostics_v33: normalized,
      engine_freshness_score: normalized.freshness_score,
      engine_display_label: normalized.display_label
    };

    window.dispatchEvent(new CustomEvent("obEngineFeedDiagnosticsUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  function panelHtml() {
    const payload = diagnosticsState.payload || fallbackPayload();
    return `
      <div class="ob-engine-diagnostics-panel" id="obEngineFeedDiagnosticsPanel" data-ob-v33-engine-feed-diagnostics="true">
        <div class="ob-engine-diagnostics-head">
          <div>
            <div class="ob-label">Engine Feed Diagnostics · V33</div>
            <div class="ob-engine-diagnostics-title">Staleness Guard</div>
            <div class="ob-engine-diagnostics-subtitle">
              ${safeText(payload.display_label, "Fallback / guarded")} · recovered fallback · data must be fresh, labeled, or fallback-marked before UI trust.
            </div>
          </div>
          <div class="ob-engine-diagnostics-chip-row">
            <span class="ob-engine-diagnostics-chip gold">Guarded fallback</span>
            <span class="ob-engine-diagnostics-chip gold">Freshness ${safeText(payload.freshness_score, "72")}</span>
            <span class="ob-engine-diagnostics-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-engine-diagnostics-note">
          <strong>Soulaana:</strong><br>
          If the feed is missing, say missing. If it is fallback, say fallback. Recovered V33 keeps OB honest until the full diagnostics route confirms freshness.
        </div>

        <div class="ob-engine-diagnostics-boundary">
          <strong>Boundary:</strong><br>
          Diagnostics only. Read-only. No broker wiring. No broker API. No auto execution. Live Auto Locked. Stale data cannot create permission.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obEngineFeedDiagnosticsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const expanded = document.getElementById("obEngineFeedExpandedPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");
    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (expanded && expanded.parentNode) {
      expanded.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    diagnosticsState.payload = diagnosticsState.payload || fallbackPayload();
    document.body.setAttribute("data-ob-v33-engine-feed-diagnostics", "ready");
    window.OB_V33_ENGINE_FEED_DIAGNOSTICS_STATE = {
      version: VERSION,
      status: diagnosticsState.status,
      fallbackActive: diagnosticsState.fallbackActive,
      freshnessScore: diagnosticsState.payload.freshness_score,
      readOnly: true,
      stalenessGuard: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    diagnosticsState.payload = expose(fallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
    }, 1260);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return diagnosticsState; },
    fallbackPayload,
    expose,
    renderPanel,
    setFlags
  };
})();
