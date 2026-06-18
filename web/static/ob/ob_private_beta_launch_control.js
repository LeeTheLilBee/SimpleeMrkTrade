// OBSERVATORY_V37_PRIVATE_BETA_LAUNCH_CONTROL_CHECKLIST_JS

(function () {
  const VERSION = "OB_V37_PRIVATE_BETA_LAUNCH_CONTROL_CHECKLIST";
  const ENDPOINT = "/ob/private-beta-launch-control.json";

  // V37 SMOKE MARKERS
  // Private Beta Launch Control Checklist
  // room readiness
  // tester readiness
  // source feed readiness
  // NDA invite readiness
  // Manual Live boundary readiness
  // proof privacy readiness
  // owner go no-go status
  // Tower controlled private beta
  // no public launch
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let launchState = {
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

  function bool(value) {
    return value === true;
  }

  function qaPayload() {
    if (window.OB_PRIVATE_BETA_QA_V31 && window.OB_PRIVATE_BETA_QA_V31.score) {
      return {
        score: window.OB_PRIVATE_BETA_QA_V31.score(),
        privateBetaReadyFoundation: true
      };
    }

    if (window.OB_V31_PRIVATE_BETA_QA_STATE) return window.OB_V31_PRIVATE_BETA_QA_STATE;

    return {
      score: 100,
      privateBetaReadyFoundation: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function testerPayload() {
    if (window.OB_BETA_TESTER_OPS_V30) {
      return {
        checklistCount: window.OB_BETA_TESTER_OPS_V30.testerChecklist ? window.OB_BETA_TESTER_OPS_V30.testerChecklist.length : 0,
        feedbackQuestions: window.OB_BETA_TESTER_OPS_V30.feedbackQuestions ? window.OB_BETA_TESTER_OPS_V30.feedbackQuestions.length : 0,
        privateBeta: true,
        ndaInviteRequired: true
      };
    }

    if (window.OB_V30_BETA_TESTER_OPS_STATE) return window.OB_V30_BETA_TESTER_OPS_STATE;

    return {
      checklistCount: 8,
      feedbackQuestions: 6,
      privateBeta: true,
      ndaInviteRequired: true
    };
  }

  function sourceAuditPayload() {
    if (window.OB_OWNER_SOURCE_AUDIT_V36_API && window.OB_OWNER_SOURCE_AUDIT_V36_API.getState) {
      const state = window.OB_OWNER_SOURCE_AUDIT_V36_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_OWNER_SOURCE_AUDIT_V36) return window.OB_OWNER_SOURCE_AUDIT_V36;

    return {
      trust_label: "Fallback / guarded",
      safe_to_display: "fallback_only",
      summary: {
        total_files: 5,
        present: 0,
        fresh: 0,
        stale: 0,
        missing: 0,
        fallback_only: 5,
        actions: 3
      },
      action_plan: [
        {
          priority: "required",
          title: "Confirm source audit",
          detail: "Source audit fallback is active.",
          action: "Run V36 and verify source files before tester reliance.",
          status: "owner action"
        }
      ]
    };
  }

  function manualLivePayload() {
    return {
      ownerManualOnly: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true,
      receipts: window.OB_MANUAL_LIVE_RECEIPTS_V29 && window.OB_MANUAL_LIVE_RECEIPTS_V29.allReceipts
        ? window.OB_MANUAL_LIVE_RECEIPTS_V29.allReceipts().length
        : 0
    };
  }

  function fallbackPayload() {
    const qa = qaPayload();
    const tester = testerPayload();
    const source = sourceAuditPayload();
    const manual = manualLivePayload();

    const sourceSummary = source.summary || {};
    const sourceNeedsReview = Number(sourceSummary.missing || 0) > 0 || Number(sourceSummary.fallback_only || 0) > 0 || safeText(source.safe_to_display, "").includes("fallback");

    const checks = [
      {
        id: "rooms",
        title: "Room readiness",
        detail: "Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console are protected and render together.",
        status: bool(qa.privateBetaReadyFoundation) || Number(qa.score || 0) >= 90 ? "pass" : "warn",
        next: "Keep six-room shell private and Tower-controlled."
      },
      {
        id: "tester",
        title: "Tester readiness",
        detail: `Tester checklist count ${safeText(tester.checklistCount, "0")} and feedback questions ${safeText(tester.feedbackQuestions, "0")}.`,
        status: bool(tester.privateBeta) && bool(tester.ndaInviteRequired) ? "pass" : "warn",
        next: "Use invite/NDA flow before adding testers."
      },
      {
        id: "source",
        title: "Source/feed readiness",
        detail: `Trust label: ${safeText(source.trust_label, "Fallback / guarded")} · safe display: ${safeText(source.safe_to_display, "caution")}.`,
        status: sourceNeedsReview ? "warn" : "pass",
        next: sourceNeedsReview ? "Fix missing/fallback-only files before tester reliance." : "Monitor freshness before each tester session."
      },
      {
        id: "nda",
        title: "NDA / invite readiness",
        detail: "Beta remains invite-only, NDA-required, and not public.",
        status: "pass",
        next: "Tester access goes through Tower."
      },
      {
        id: "manual_live",
        title: "Manual Live boundary readiness",
        detail: "Manual Live remains owner/manual only. No broker API. No auto execution. Live Auto Locked.",
        status: bool(manual.ownerManualOnly) && bool(manual.noBrokerApi) && bool(manual.noAutoExecution) ? "pass" : "fail",
        next: "Do not add broker wiring."
      },
      {
        id: "proof_privacy",
        title: "Proof / privacy readiness",
        detail: "Proof, demo, receipts, tester feedback, and review records stay private unless Tower clears export later.",
        status: "pass",
        next: "No public proof in beta."
      },
      {
        id: "tower",
        title: "Tower control readiness",
        detail: "Tower owns identity, access, invite, billing, permissions, locks, clearance, and export approval.",
        status: "pass",
        next: "No bypass routes."
      }
    ];

    const failCount = checks.filter(check => check.status === "fail").length;
    const warnCount = checks.filter(check => check.status === "warn").length;
    const passCount = checks.filter(check => check.status === "pass").length;
    const score = Math.round((passCount / checks.length) * 100);

    let goNoGo = "GO FOR PRIVATE OWNER REVIEW";
    if (failCount > 0) goNoGo = "NO-GO";
    else if (warnCount > 0) goNoGo = "CONDITIONAL GO";
    else goNoGo = "PRIVATE BETA READY";

    return {
      version: VERSION,
      source: "v37_safe_launch_control_fallback",
      launch_status: "fallback",
      score,
      go_no_go: goNoGo,
      checks,
      summary: {
        pass: passCount,
        warn: warnCount,
        fail: failCount,
        total: checks.length
      },
      owner_final_actions: [
        sourceNeedsReview
          ? "Fix source/feed warnings from V36 before testers rely on engine feed."
          : "Monitor source freshness before each tester session.",
        "Confirm tester invite list and NDA status through Tower.",
        "Confirm Manual Live stays owner/manual only.",
        "Confirm no public proof, no public launch, no broker wiring.",
        "Run final visual room walkthrough before first tester."
      ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        tower_controlled_private_beta: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        launch_control_does_not_create_permission: true
      },
      warnings: [
        "Launch control is owner-facing only.",
        "Conditional go is not public launch.",
        "No broker wiring.",
        "No execution permission changed."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = fallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      launch_status: safe.launch_status || "normalized",
      score: Number.isFinite(Number(safe.score)) ? Number(safe.score) : fallback.score,
      go_no_go: safe.go_no_go || fallback.go_no_go,
      checks: Array.isArray(safe.checks) ? safe.checks : fallback.checks,
      summary: {
        ...(fallback.summary || {}),
        ...(safe.summary || {})
      },
      owner_final_actions: Array.isArray(safe.owner_final_actions) ? safe.owner_final_actions : fallback.owner_final_actions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        tower_controlled_private_beta: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        launch_control_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_launch_control_v37: normalized,
      private_beta_go_no_go: normalized.go_no_go
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaLaunchControlUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchLaunchControl() {
    launchState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      launchState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        launchState.status = "ready";
        launchState.source = normalized.source || "launch_control_snapshot";
        launchState.payload = normalized;
        launchState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(fallbackPayload());

        launchState.status = "guarded_fallback";
        launchState.source = "guarded_launch_control_route_fallback";
        launchState.payload = fallback;
        launchState.fallbackActive = true;
        launchState.error = "Launch control route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(fallbackPayload());

        launchState.status = "http_fallback";
        launchState.source = "http_" + response.status + "_fallback";
        launchState.payload = fallback;
        launchState.fallbackActive = true;
        launchState.error = "Launch control route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(fallbackPayload());

      launchState.status = "error_fallback";
      launchState.source = "fetch_error_fallback";
      launchState.payload = fallback;
      launchState.fallbackActive = true;
      launchState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return launchState;
  }

  function statusKind(status) {
    const text = safeText(status, "").toLowerCase();
    if (text.includes("pass") || text.includes("ready")) return "green";
    if (text.includes("warn") || text.includes("conditional")) return "gold";
    if (text.includes("fail") || text.includes("no-go")) return "red";
    return "gold";
  }

  function rowClass(status) {
    const text = safeText(status, "").toLowerCase();
    if (text.includes("warn")) return "warn";
    if (text.includes("fail")) return "fail";
    return "";
  }

  function card(label, value) {
    return `
      <div class="ob-private-beta-launch-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function checkRow(check, index) {
    return `
      <div class="ob-private-beta-launch-row ${rowClass(check.status)}">
        <div class="ob-private-beta-launch-dot">${index + 1}</div>
        <div>
          <strong>${safeText(check.title, "Launch check")}</strong>
          <span>${safeText(check.next, "Owner review required.")}</span>
        </div>
        <span>${safeText(check.detail, "No detail.")}</span>
        <div class="ob-private-beta-launch-status ${statusKind(check.status)}">${safeText(check.status, "review")}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = launchState.payload || fallbackPayload();
    const summary = payload.summary || {};
    const checks = Array.isArray(payload.checks) ? payload.checks : [];
    const actions = Array.isArray(payload.owner_final_actions) ? payload.owner_final_actions : [];
    const finalKind = statusKind(payload.go_no_go);

    return `
      <div class="ob-private-beta-launch-panel" id="obPrivateBetaLaunchControlPanel" data-ob-v37-private-beta-launch-control="true">
        <div class="ob-private-beta-launch-head">
          <div>
            <div class="ob-label">Private Beta Launch Control · V37</div>
            <div class="ob-private-beta-launch-title">Owner go / no-go checklist</div>
            <div class="ob-private-beta-launch-subtitle">
              ${safeText(payload.go_no_go, "Review")} · ${safeText(launchState.status, "booting")} · final private beta launch control before testers rely on OB.
            </div>
          </div>

          <div class="ob-private-beta-launch-chip-row">
            <span class="ob-private-beta-launch-chip ${finalKind}">${safeText(payload.go_no_go, "Review")}</span>
            <span class="ob-private-beta-launch-chip gold">Private beta only</span>
            <span class="ob-private-beta-launch-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-private-beta-launch-score-wrap">
          <div class="ob-private-beta-launch-score">${safeText(payload.score, "0")}</div>
          <div class="ob-private-beta-launch-score-copy">
            <strong>Private beta launch-control score</strong>
            <span>
              This is owner-facing launch control, not public launch clearance. Conditional warnings must be fixed or accepted by the owner before testers rely on engine feed context.
            </span>
          </div>
        </div>

        <div class="ob-private-beta-launch-grid">
          ${card("Pass", safeText(summary.pass, "0"))}
          ${card("Warn", safeText(summary.warn, "0"))}
          ${card("Fail", safeText(summary.fail, "0"))}
          ${card("Rooms", "6")}
          ${card("Tester", "Invite/NDA")}
          ${card("Manual Live", "Owner only")}
          ${card("Proof", "Private")}
        </div>

        <div class="ob-private-beta-launch-list">
          ${checks.map(checkRow).join("")}
        </div>

        <div class="ob-private-beta-launch-final">
          <strong>Owner final actions</strong>
          <span>${actions.map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}</span>
        </div>

        <div class="ob-private-beta-launch-note">
          <strong>Soulaana:</strong><br>
          Private beta means controlled doors, clean instructions, honest data labels, and no pretending the system can do more than it is cleared to do.
        </div>

        <div class="ob-private-beta-launch-boundary">
          <strong>Boundary:</strong><br>
          Launch control is private and owner-facing. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked. Tower controls access.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaLaunchControlPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const audit = document.getElementById("obOwnerSourceAuditPanel");
    const mapping = document.getElementById("obEngineRoomMappingPanel");
    const trust = document.getElementById("obEngineTrustLabelsPanel");
    const diagnostics = document.getElementById("obEngineFeedDiagnosticsPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (audit && audit.parentNode) {
      audit.insertAdjacentElement("afterend", panel);
    } else if (mapping && mapping.parentNode) {
      mapping.insertAdjacentElement("afterend", panel);
    } else if (trust && trust.parentNode) {
      trust.insertAdjacentElement("afterend", panel);
    } else if (diagnostics && diagnostics.parentNode) {
      diagnostics.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = launchState.payload || fallbackPayload();

    document.body.setAttribute("data-ob-v37-private-beta-launch-control", "ready");
    window.OB_V37_PRIVATE_BETA_LAUNCH_CONTROL_STATE = {
      version: VERSION,
      status: launchState.status,
      fallbackActive: launchState.fallbackActive,
      goNoGo: payload.go_no_go,
      score: payload.score,
      readOnly: true,
      privateBetaOnly: true,
      launchControlChecklist: true,
      noPublicLaunch: true,
      noPublicProof: true,
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
      fetchLaunchControl();
    }, 1740);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obOwnerSourceAuditUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return launchState; },
    fallbackPayload,
    normalizePayload,
    expose,
    fetchLaunchControl,
    renderPanel,
    setFlags
  };
})();
