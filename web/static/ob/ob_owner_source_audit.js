// OBSERVATORY_V36_OWNER_CONSOLE_SOURCE_AUDIT_ACTION_PLAN_JS

(function () {
  const VERSION = "OB_V36_OWNER_CONSOLE_SOURCE_AUDIT_ACTION_PLAN";
  const ENDPOINT = "/ob/owner-source-audit.json";

  // V36 SMOKE MARKERS
  // Owner Console Source Audit
  // Missing Data Action Plan
  // present missing stale fallback-only files
  // owner fix-next plan
  // beta tester reliance warning
  // candidate_log source audit
  // open_positions source audit
  // ledger source audit
  // market_universe source audit
  // pipeline_status source audit
  // room mapping source audit
  // trust label source audit
  // read-only source audit
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let auditState = {
    status: "booting",
    httpStatus: null,
    source: "waiting",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function diagnosticsPayload() {
    if (window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API && window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API.getState) {
      const state = window.OB_ENGINE_FEED_DIAGNOSTICS_V33_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_FEED_DIAGNOSTICS_V33) return window.OB_ENGINE_FEED_DIAGNOSTICS_V33;

    return {
      source: "v36_diagnostics_fallback",
      display_label: "Fallback / guarded",
      freshness_score: 72,
      files: [],
      summary: {
        present: 0,
        fresh: 0,
        stale: 0,
        missing: 0,
        fallback_only: 1,
        caution: 1
      }
    };
  }

  function trustPayload() {
    if (window.OB_ENGINE_TRUST_LABELS_V34_API && window.OB_ENGINE_TRUST_LABELS_V34_API.getState) {
      const state = window.OB_ENGINE_TRUST_LABELS_V34_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_TRUST_LABELS_V34) return window.OB_ENGINE_TRUST_LABELS_V34;

    return {
      trust: {
        level: "fallback",
        label: "Fallback / guarded",
        safeToDisplay: "fallback_only"
      },
      freshness_score: 72
    };
  }

  function mappingPayload() {
    if (window.OB_ENGINE_ROOM_MAPPING_V35_API && window.OB_ENGINE_ROOM_MAPPING_V35_API.getState) {
      const state = window.OB_ENGINE_ROOM_MAPPING_V35_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_ENGINE_ROOM_MAPPING_V35) return window.OB_ENGINE_ROOM_MAPPING_V35;

    return {
      source: "v36_mapping_fallback",
      mapping_status: "fallback",
      rooms: {},
      trust_label: "Fallback / guarded",
      safe_to_display: "fallback_only"
    };
  }

  function fallbackFiles() {
    const diagnostics = diagnosticsPayload();
    const files = Array.isArray(diagnostics.files) ? diagnostics.files : [];

    if (files.length) {
      return files.map(file => ({
        name: safeText(file.name, "unknown"),
        status: safeText(file.status, "unknown"),
        exists: !!file.exists,
        age_minutes: file.age_minutes === undefined ? null : file.age_minutes,
        safe_to_display: safeText(file.safe_to_display, "caution"),
        label: safeText(file.label, "Unknown"),
        note: safeText(file.note, "No note from diagnostics."),
        priority: file.exists ? (file.status === "fresh" ? "low" : "medium") : "high",
        action: file.exists ? "Verify freshness before beta reliance." : "Create or regenerate this data file before relying on it."
      }));
    }

    return [
      {
        name: "candidate_log",
        status: "fallback_only",
        exists: false,
        age_minutes: null,
        safe_to_display: "fallback_only",
        label: "Fallback only",
        note: "Candidate data is not confirmed fresh.",
        priority: "high",
        action: "Regenerate candidate_log.json from the real engine before tester reliance."
      },
      {
        name: "open_positions",
        status: "fallback_only",
        exists: false,
        age_minutes: null,
        safe_to_display: "fallback_only",
        label: "Fallback only",
        note: "Open position data is not confirmed fresh.",
        priority: "high",
        action: "Regenerate open_positions.json or connect the read-only snapshot producer."
      },
      {
        name: "ledger",
        status: "fallback_only",
        exists: false,
        age_minutes: null,
        safe_to_display: "fallback_only",
        label: "Fallback only",
        note: "Ledger data is not confirmed fresh.",
        priority: "medium",
        action: "Confirm ledger export path and receipt/review alignment."
      },
      {
        name: "market_universe",
        status: "fallback_only",
        exists: false,
        age_minutes: null,
        safe_to_display: "fallback_only",
        label: "Fallback only",
        note: "Market universe is not confirmed fresh.",
        priority: "medium",
        action: "Regenerate market universe and sector/source labels."
      },
      {
        name: "pipeline_status",
        status: "fallback_only",
        exists: false,
        age_minutes: null,
        safe_to_display: "fallback_only",
        label: "Fallback only",
        note: "Pipeline status is not confirmed fresh.",
        priority: "medium",
        action: "Update pipeline_status.json after the next engine/snapshot run."
      }
    ];
  }

  function buildActionPlan(files) {
    const plan = [];
    const missing = files.filter(file => !file.exists || file.safe_to_display === "fallback_only");
    const stale = files.filter(file => file.status === "stale" || file.status === "old" || file.safe_to_display === "caution" || file.safe_to_display === "fallback_recommended");
    const fresh = files.filter(file => file.status === "fresh" || file.safe_to_display === "safe");

    if (missing.length) {
      plan.push({
        priority: "high",
        title: "Fix missing / fallback-only sources",
        detail: `${missing.map(file => file.name).join(", ")} need generation or read-only snapshot wiring before testers rely on them.`,
        action: "Run engine snapshot/export flow, then rerun V33/V34/V35 diagnostics.",
        status: "owner action"
      });
    }

    if (stale.length) {
      plan.push({
        priority: "medium",
        title: "Refresh stale sources",
        detail: `${stale.map(file => file.name).join(", ")} are stale or caution-labeled.`,
        action: "Regenerate these files and verify freshness score before beta tester expansion.",
        status: "owner action"
      });
    }

    if (!missing.length && !stale.length && fresh.length) {
      plan.push({
        priority: "low",
        title: "Sources are display-ready",
        detail: "All tracked sources are fresh enough for read-only private beta display.",
        action: "Keep monitoring freshness before each tester session.",
        status: "monitor"
      });
    }

    plan.push({
      priority: "required",
      title: "Keep permissions unchanged",
      detail: "Source audit can recommend data refresh, but cannot grant execution permission.",
      action: "Keep no broker wiring, no broker API, no auto execution, and Live Auto Locked.",
      status: "boundary"
    });

    plan.push({
      priority: "required",
      title: "Label tester-facing rooms",
      detail: "Any stale, missing, guarded, or fallback feed must remain visibly labeled in every room.",
      action: "Use V34 trust labels and V35 room mapping before tester reliance.",
      status: "boundary"
    });

    return plan;
  }

  function fallbackPayload() {
    const diagnostics = diagnosticsPayload();
    const trust = trustPayload();
    const mapping = mappingPayload();
    const files = fallbackFiles();
    const plan = buildActionPlan(files);

    return {
      version: VERSION,
      source: "v36_safe_owner_source_audit_fallback",
      audit_status: "fallback",
      trust_label: safeText((trust.trust || {}).label, diagnostics.display_label || "Fallback / guarded"),
      safe_to_display: safeText((trust.trust || {}).safeToDisplay, mapping.safe_to_display || "fallback_only"),
      freshness_score: trust.freshness_score || diagnostics.freshness_score || 72,
      summary: {
        total_files: files.length,
        present: files.filter(file => file.exists).length,
        fresh: files.filter(file => file.status === "fresh").length,
        stale: files.filter(file => file.status === "stale" || file.status === "old").length,
        missing: files.filter(file => !file.exists).length,
        fallback_only: files.filter(file => file.safe_to_display === "fallback_only").length,
        actions: plan.length
      },
      files,
      action_plan: plan,
      room_impact: {
        dashboard: "Account/focus/market panels must show trust label before relying on feed.",
        market_map: "Constellation labels must show source/freshness before beta tester interpretation.",
        symbol_page: "One-symbol context must show stale/fallback warning when applicable.",
        trade_center: "Candidate queue must show caution labels and remain review-only.",
        review_center: "Ledger/receipts must stay private and freshness-labeled.",
        owner_console: "Owner must review missing/stale/fallback sources before expanding beta reliance."
      },
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        source_audit_does_not_create_permission: true,
        stale_data_cannot_create_permission: true
      },
      warnings: [
        "Owner source audit is read-only.",
        "Missing or stale data cannot create permission.",
        "Beta testers should not rely on fallback-only engine feed.",
        "No broker wiring."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = fallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      audit_status: safe.audit_status || "normalized",
      trust_label: safe.trust_label || fallback.trust_label,
      safe_to_display: safe.safe_to_display || fallback.safe_to_display,
      freshness_score: Number.isFinite(Number(safe.freshness_score)) ? Number(safe.freshness_score) : fallback.freshness_score,
      summary: {
        ...(fallback.summary || {}),
        ...(safe.summary || {})
      },
      files: Array.isArray(safe.files) ? safe.files : fallback.files,
      action_plan: Array.isArray(safe.action_plan) ? safe.action_plan : fallback.action_plan,
      room_impact: {
        ...(fallback.room_impact || {}),
        ...(safe.room_impact || {})
      },
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        source_audit_does_not_create_permission: true,
        stale_data_cannot_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_OWNER_SOURCE_AUDIT_V36 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_source_audit_v36: normalized,
      owner_source_action_plan: normalized.action_plan
    };

    window.dispatchEvent(new CustomEvent("obOwnerSourceAuditUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchSourceAudit() {
    auditState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      auditState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        auditState.status = "ready";
        auditState.source = normalized.source || "owner_source_audit_snapshot";
        auditState.payload = normalized;
        auditState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(fallbackPayload());

        auditState.status = "guarded_fallback";
        auditState.source = "guarded_source_audit_route_fallback";
        auditState.payload = fallback;
        auditState.fallbackActive = true;
        auditState.error = "Owner source audit route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(fallbackPayload());

        auditState.status = "http_fallback";
        auditState.source = "http_" + response.status + "_fallback";
        auditState.payload = fallback;
        auditState.fallbackActive = true;
        auditState.error = "Owner source audit route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(fallbackPayload());

      auditState.status = "error_fallback";
      auditState.source = "fetch_error_fallback";
      auditState.payload = fallback;
      auditState.fallbackActive = true;
      auditState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return auditState;
  }

  function statusKind(value) {
    const text = safeText(value, "").toLowerCase();

    if (text.includes("fresh") || text.includes("safe") || text.includes("low")) return "green";
    if (text.includes("stale") || text.includes("caution") || text.includes("medium") || text.includes("old")) return "gold";
    if (text.includes("missing") || text.includes("fallback") || text.includes("high")) return "red";
    return "gold";
  }

  function card(label, value) {
    return `
      <div class="ob-owner-source-audit-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function fileRow(file) {
    const age = file.age_minutes === null || file.age_minutes === undefined ? "unknown" : `${file.age_minutes}m`;

    return `
      <div class="ob-owner-source-audit-row">
        <strong>${safeText(file.name, "source")}</strong>
        <span>${safeText(file.label, file.status || "unknown")}</span>
        <span>age ${age}</span>
        <span>${safeText(file.action || file.note, "Review source before beta reliance.")}</span>
        <div class="ob-owner-source-audit-status ${statusKind(file.safe_to_display || file.status)}">${safeText(file.safe_to_display, "caution")}</div>
      </div>
    `;
  }

  function planRow(item, index) {
    return `
      <div class="ob-owner-source-audit-plan-row">
        <div class="ob-owner-source-audit-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.title, "Owner action")}</strong>
          <span>${safeText(item.priority, "medium")} · ${safeText(item.status, "review")}</span>
        </div>
        <span>${safeText(item.detail, "Review this before tester reliance.")}<br>${safeText(item.action, "")}</span>
        <div class="ob-owner-source-audit-status ${statusKind(item.priority)}">${safeText(item.priority, "medium")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = auditState.payload || fallbackPayload();
    const summary = payload.summary || {};
    const files = Array.isArray(payload.files) ? payload.files : [];
    const plan = Array.isArray(payload.action_plan) ? payload.action_plan : [];

    return `
      <div class="ob-owner-source-audit-panel" id="obOwnerSourceAuditPanel" data-ob-v36-owner-source-audit="true">
        <div class="ob-owner-source-audit-head">
          <div>
            <div class="ob-label">Owner Console Source Audit · V36</div>
            <div class="ob-owner-source-audit-title">Missing Data Action Plan</div>
            <div class="ob-owner-source-audit-subtitle">
              ${safeText(payload.trust_label, "Fallback / guarded")} · ${safeText(auditState.status, "booting")} · owner fixes data sources before beta testers rely on engine feed.
            </div>
          </div>

          <div class="ob-owner-source-audit-chip-row">
            <span class="ob-owner-source-audit-chip ${auditState.fallbackActive ? "gold" : "green"}">${auditState.fallbackActive ? "Safe fallback" : "Audit active"}</span>
            <span class="ob-owner-source-audit-chip gold">${safeText(payload.safe_to_display, "caution")}</span>
            <span class="ob-owner-source-audit-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-owner-source-audit-grid">
          ${card("Files", safeText(summary.total_files, files.length))}
          ${card("Present", safeText(summary.present, "0"))}
          ${card("Fresh", safeText(summary.fresh, "0"))}
          ${card("Stale", safeText(summary.stale, "0"))}
          ${card("Missing", safeText(summary.missing, "0"))}
          ${card("Actions", safeText(summary.actions, plan.length))}
        </div>

        <div class="ob-owner-source-audit-section">
          <div class="ob-owner-source-audit-section-title">Source audit</div>
          <div class="ob-owner-source-audit-list">
            ${files.map(fileRow).join("")}
          </div>
        </div>

        <div class="ob-owner-source-audit-section">
          <div class="ob-owner-source-audit-section-title">Owner fix-next plan</div>
          <div class="ob-owner-source-audit-plan">
            ${plan.map(planRow).join("")}
          </div>
        </div>

        <div class="ob-owner-source-audit-note">
          <strong>Soulaana:</strong><br>
          Before testers lean on the engine feed, the owner needs to know what is real, what is old, what is missing, and what is only fallback.
        </div>

        <div class="ob-owner-source-audit-boundary">
          <strong>Boundary:</strong><br>
          Source audit is read-only. It can tell you what to fix next. It cannot create permission. No broker wiring. No broker API. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerSourceAuditPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const mapping = document.getElementById("obEngineRoomMappingPanel");
    const trust = document.getElementById("obEngineTrustLabelsPanel");
    const diagnostics = document.getElementById("obEngineFeedDiagnosticsPanel");
    const expanded = document.getElementById("obEngineFeedExpandedPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (mapping && mapping.parentNode) {
      mapping.insertAdjacentElement("afterend", panel);
    } else if (trust && trust.parentNode) {
      trust.insertAdjacentElement("afterend", panel);
    } else if (diagnostics && diagnostics.parentNode) {
      diagnostics.insertAdjacentElement("afterend", panel);
    } else if (expanded && expanded.parentNode) {
      expanded.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = auditState.payload || fallbackPayload();

    document.body.setAttribute("data-ob-v36-owner-source-audit", "ready");
    window.OB_V36_OWNER_SOURCE_AUDIT_STATE = {
      version: VERSION,
      status: auditState.status,
      fallbackActive: auditState.fallbackActive,
      trustLabel: payload.trust_label,
      safeToDisplay: payload.safe_to_display,
      actionCount: Array.isArray(payload.action_plan) ? payload.action_plan.length : 0,
      readOnly: true,
      ownerSourceAudit: true,
      missingDataActionPlan: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(fallbackPayload());

    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchSourceAudit();
    }, 1620);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineRoomMappingUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_OWNER_SOURCE_AUDIT_V36_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return auditState; },
    fallbackPayload,
    normalizePayload,
    expose,
    fetchSourceAudit,
    renderPanel,
    setFlags
  };
})();
