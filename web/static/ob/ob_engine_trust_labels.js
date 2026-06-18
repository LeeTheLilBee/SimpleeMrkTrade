// OBSERVATORY_V34_ENGINE_FEED_TRUST_LABELS_ROOM_WARNINGS_JS

(function () {
  const VERSION = "OB_V34_ENGINE_FEED_TRUST_LABELS_ROOM_WARNINGS";
  const ENDPOINT = "/ob/engine-feed-trust-labels.json";

  // V34 SMOKE MARKERS
  // Engine Feed Trust Labels
  // Room Warnings
  // Dashboard warning if engine feed is stale or fallback
  // Market Map fresh stale fallback sky label
  // Symbol Page stale-data warning strip
  // Trade Center candidate caution labels
  // Review Center receipt feed freshness label
  // Owner Console diagnostic warning summary
  // fresh stale missing guarded fallback labels
  // safe-to-display room labels
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let trustState = {
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

    if (window.OB_ENGINE_FEED_DIAGNOSTICS_V33) {
      return window.OB_ENGINE_FEED_DIAGNOSTICS_V33;
    }

    return {
      source: "v34_diagnostics_fallback",
      freshness_score: 72,
      display_label: "Fallback / guarded",
      summary: {
        present: 0,
        fresh: 0,
        stale: 0,
        missing: 0,
        fallback_only: 1,
        caution: 1
      },
      files: [],
      tower_boundaries: {
        read_only: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true
      }
    };
  }

  function classifyTrust(payload) {
    const score = Number(payload.freshness_score || 0);
    const summary = payload.summary || {};
    const label = safeText(payload.display_label, "").toLowerCase();

    if (summary.missing > 0 || summary.fallback_only > 0 || label.includes("missing") || label.includes("fallback")) {
      return {
        level: "fallback",
        kind: "danger",
        label: "Fallback / missing",
        roomAction: "Show warning before trusting room data.",
        safeToDisplay: "fallback_only"
      };
    }

    if (summary.stale > 0 || summary.caution > 0 || label.includes("stale") || score < 75) {
      return {
        level: "stale",
        kind: "gold",
        label: "Stale / caution",
        roomAction: "Display with caution labels.",
        safeToDisplay: "caution"
      };
    }

    return {
      level: "fresh",
      kind: "green",
      label: "Fresh read-only",
      roomAction: "Safe to display as read-only context.",
      safeToDisplay: "safe"
    };
  }

  function fallbackPayload() {
    const diagnostics = diagnosticsPayload();
    const trust = classifyTrust(diagnostics);

    return {
      version: VERSION,
      source: "v34_safe_trust_label_fallback",
      trust_status: "fallback",
      trust: trust,
      freshness_score: diagnostics.freshness_score || 72,
      display_label: diagnostics.display_label || trust.label,
      room_warnings: buildRoomWarnings(trust, diagnostics),
      summary: diagnostics.summary || {},
      tower_boundaries: {
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        stale_data_cannot_create_permission: true
      },
      warnings: [
        "Trust labels are active.",
        "Fallback or stale data must be visibly labeled.",
        "No execution permissions changed."
      ]
    };
  }

  function buildRoomWarnings(trust, diagnostics) {
    const base = {
      dashboard: {
        title: "Dashboard engine trust",
        detail: "Dashboard must show whether engine feed is fresh, stale, missing, guarded, or fallback before account/focus panels trust it.",
        label: trust.label
      },
      market_map: {
        title: "Market Map sky trust",
        detail: "Market Map should label the sky as fresh, stale, or fallback so constellation counts are not over-trusted.",
        label: trust.label
      },
      symbol_page: {
        title: "Symbol Page stale-data warning",
        detail: "Symbol Page should show a warning strip if source data is stale, missing, guarded, or fallback-only.",
        label: trust.label
      },
      trade_center: {
        title: "Trade Center candidate caution",
        detail: "Trade Center candidate cards should carry caution labels when feed freshness is stale, missing, or fallback.",
        label: trust.label
      },
      review_center: {
        title: "Review Center receipt/feed freshness",
        detail: "Review Center should label whether receipts/review feed context is fresh, stale, private, or fallback.",
        label: trust.label
      },
      owner_console: {
        title: "Owner Console diagnostic warning summary",
        detail: "Owner Console should summarize all feed trust warnings before owner expands testing or engine reliance.",
        label: trust.label
      }
    };

    return base;
  }

  function normalizePayload(raw) {
    const fallback = fallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};
    const trust = safe.trust || fallback.trust || classifyTrust(diagnosticsPayload());

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      trust_status: safe.trust_status || "normalized",
      trust: {
        ...(fallback.trust || {}),
        ...(trust || {})
      },
      freshness_score: Number.isFinite(Number(safe.freshness_score)) ? Number(safe.freshness_score) : fallback.freshness_score,
      display_label: safe.display_label || fallback.display_label,
      room_warnings: safe.room_warnings || fallback.room_warnings,
      summary: {
        ...(fallback.summary || {}),
        ...(safe.summary || {})
      },
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        stale_data_cannot_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_ENGINE_TRUST_LABELS_V34 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      engine_trust_labels_v34: normalized,
      engine_trust_label: normalized.trust.label,
      engine_safe_to_display: normalized.trust.safeToDisplay
    };

    window.dispatchEvent(new CustomEvent("obEngineTrustLabelsUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchTrustLabels() {
    trustState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      trustState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        trustState.status = "ready";
        trustState.source = normalized.source || "trust_labels_snapshot";
        trustState.payload = normalized;
        trustState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(fallbackPayload());

        trustState.status = "guarded_fallback";
        trustState.source = "guarded_trust_labels_route_fallback";
        trustState.payload = fallback;
        trustState.fallbackActive = true;
        trustState.error = "Trust labels route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(fallbackPayload());

        trustState.status = "http_fallback";
        trustState.source = "http_" + response.status + "_fallback";
        trustState.payload = fallback;
        trustState.fallbackActive = true;
        trustState.error = "Trust labels route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(fallbackPayload());

      trustState.status = "error_fallback";
      trustState.source = "fetch_error_fallback";
      trustState.payload = fallback;
      trustState.fallbackActive = true;
      trustState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return trustState;
  }

  function currentRoomKey() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes("/symbol/")) return "symbol_page";
    if (path.includes("market-map")) return "market_map";
    if (path.includes("trade-center")) return "trade_center";
    if (path.includes("review-center")) return "review_center";
    if (path.includes("owner-console")) return "owner_console";
    return "dashboard";
  }

  function card(label, value) {
    return `
      <div class="ob-engine-trust-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function warningKind(trust) {
    if (!trust) return "danger";
    if (trust.kind === "green" || trust.level === "fresh") return "safe";
    if (trust.kind === "red" || trust.level === "fallback" || trust.level === "missing") return "danger";
    return "";
  }

  function statusClass(trust) {
    if (!trust) return "red";
    if (trust.kind === "green" || trust.level === "fresh") return "green";
    if (trust.kind === "red" || trust.level === "fallback" || trust.level === "missing") return "red";
    return "";
  }

  function roomWarning(payload) {
    const room = currentRoomKey();
    const warnings = payload.room_warnings || {};
    return warnings[room] || warnings.dashboard || {
      title: "Engine trust label",
      detail: "Feed trust label is active for this room.",
      label: payload.display_label || "Unknown"
    };
  }

  function roomLine(room, trust) {
    if (room === "dashboard") return "Dashboard warning: account, market, and focus panels should not over-trust stale or fallback engine feed data.";
    if (room === "market_map") return "Market Map sky label: constellation counts must show fresh, stale, missing, guarded, or fallback state.";
    if (room === "symbol_page") return "Symbol Page warning strip: one-star context must say when data is stale, missing, guarded, or fallback-only.";
    if (room === "trade_center") return "Trade Center caution: candidate cards must carry feed trust labels before owner review.";
    if (room === "review_center") return "Review Center freshness: receipts and review feed context stay private and freshness-labeled.";
    if (room === "owner_console") return "Owner Console summary: diagnostics and trust labels must be visible before expanding beta reliance.";
    return "Trust labels are active for this protected OB room.";
  }

  function panelHtml() {
    const payload = trustState.payload || fallbackPayload();
    const trust = payload.trust || classifyTrust(diagnosticsPayload());
    const warning = roomWarning(payload);
    const kind = warningKind(trust);
    const room = currentRoomKey();
    const summary = payload.summary || {};

    return `
      <div class="ob-engine-trust-panel ${kind === "danger" ? "trust-danger" : kind === "" ? "trust-warn" : ""}" id="obEngineTrustLabelsPanel" data-ob-v34-engine-trust-labels="true">
        <div class="ob-engine-trust-head">
          <div>
            <div class="ob-label">Engine Feed Trust Labels · V34</div>
            <div class="ob-engine-trust-title">Room warnings + trust labels</div>
            <div class="ob-engine-trust-subtitle">
              ${safeText(payload.display_label, trust.label)} · ${safeText(trustState.status, "booting")} · ${safeText(warning.detail, "Trust label active.")}
            </div>
          </div>

          <div class="ob-engine-trust-chip-row">
            <span class="ob-engine-trust-chip ${statusClass(trust)}">${safeText(trust.label, "Unknown")}</span>
            <span class="ob-engine-trust-chip gold">Safe-to-display: ${safeText(trust.safeToDisplay, "caution")}</span>
            <span class="ob-engine-trust-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-engine-trust-strip">
          ${card("Trust", safeText(trust.label, "Unknown"))}
          ${card("Freshness", safeText(payload.freshness_score, "0"))}
          ${card("Fresh", safeText(summary.fresh, "0"))}
          ${card("Stale", safeText(summary.stale, "0"))}
          ${card("Fallback", safeText(summary.fallback_only, "0"))}
        </div>

        <div class="ob-engine-trust-warning ${kind}">
          <div class="ob-engine-trust-dot">${kind === "safe" ? "✓" : "!"}</div>
          <div class="ob-engine-trust-copy">
            <strong>${safeText(warning.title, "Engine trust warning")}</strong>
            <span>${safeText(warning.detail, "Feed trust label is active.")}</span>
          </div>
          <div class="ob-engine-trust-status ${statusClass(trust)}">${safeText(warning.label, trust.label)}</div>
        </div>

        <div class="ob-engine-trust-room-line">
          <strong>Room-specific warning:</strong><br>
          ${roomLine(room, trust)}
        </div>

        <div class="ob-engine-trust-boundary">
          <strong>Boundary:</strong><br>
          Trust labels are warnings only. Read-only. No broker wiring. No broker API. No auto execution. Live Auto Locked. Stale or fallback data cannot create permission.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obEngineTrustLabelsPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const diagnostics = document.getElementById("obEngineFeedDiagnosticsPanel");
    const expanded = document.getElementById("obEngineFeedExpandedPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");
    const testerOps = document.getElementById("obBetaTesterOpsPanel");
    const receipts = document.getElementById("obManualLiveReceiptsPanel");
    const candidate = document.getElementById("obCandidateCardsPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (diagnostics && diagnostics.parentNode) {
      diagnostics.insertAdjacentElement("afterend", panel);
    } else if (expanded && expanded.parentNode) {
      expanded.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else if (testerOps && testerOps.parentNode) {
      testerOps.insertAdjacentElement("afterend", panel);
    } else if (receipts && receipts.parentNode) {
      receipts.insertAdjacentElement("afterend", panel);
    } else if (candidate && candidate.parentNode) {
      candidate.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = trustState.payload || fallbackPayload();
    const trust = payload.trust || classifyTrust(diagnosticsPayload());

    document.body.setAttribute("data-ob-v34-engine-trust-labels", "ready");
    document.body.setAttribute("data-ob-engine-trust-level", safeText(trust.level, "unknown"));

    window.OB_V34_ENGINE_TRUST_LABELS_STATE = {
      version: VERSION,
      status: trustState.status,
      fallbackActive: trustState.fallbackActive,
      trustLevel: trust.level,
      safeToDisplay: trust.safeToDisplay,
      readOnly: true,
      roomWarnings: true,
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
      fetchTrustLabels();
    }, 1380);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obEngineFeedDiagnosticsUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_ENGINE_TRUST_LABELS_V34_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return trustState; },
    classifyTrust,
    buildRoomWarnings,
    fallbackPayload,
    normalizePayload,
    expose,
    fetchTrustLabels,
    renderPanel,
    setFlags
  };
})();
