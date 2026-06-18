// OBSERVATORY_V44_PRIVATE_BETA_FIX_VERIFICATION_CHECKLIST_JS

(function () {
  const VERSION = "OB_V44_PRIVATE_BETA_FIX_VERIFICATION_CHECKLIST";
  const ENDPOINT = "/ob/private-beta-fix-verification.json";

  // V44 SMOKE MARKERS
  // Private Beta Fix Verification Checklist
  // must-fix verification
  // blocker fix verification
  // high-priority fix verification
  // owner verification status
  // evidence notes
  // rerun V40 V41 V42 V43
  // verify before next tester
  // fix verification does not create permission
  // private beta only
  // no public proof
  // no public launch
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let verifyState = {
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

  function triagePayload() {
    if (window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API && window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API.getState) {
      const state = window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42) return window.OB_PRIVATE_BETA_ISSUE_TRIAGE_V42;

    return {
      next_tester_status: "NO-GO",
      issues: [
        {
          id: "TRIAGE-FB-QUEUE-002",
          feedback_id: "FB-QUEUE-002",
          room: "Trade Center",
          issue_type: "safety issue",
          priority: "high",
          must_fix_before_next_tester: true,
          summary: "Tester may feel pressure to trade instead of review.",
          owner_action: "Strengthen review-only language before next tester."
        },
        {
          id: "TRIAGE-FB-QUEUE-003",
          feedback_id: "FB-QUEUE-003",
          room: "Market Map",
          issue_type: "data issue",
          priority: "high",
          must_fix_before_next_tester: true,
          summary: "Tester may not understand snapshot/stale/guarded/fallback data.",
          owner_action: "Run V36 source audit and refresh stale/fallback feed labels."
        },
        {
          id: "TRIAGE-FB-QUEUE-004",
          feedback_id: "FB-QUEUE-004",
          room: "Trade Center",
          issue_type: "safety issue",
          priority: "blocker",
          must_fix_before_next_tester: true,
          summary: "Tester must find Tower state, Live Auto Locked, and no-execution boundaries.",
          owner_action: "Pause tester expansion until safety wording and Tower boundaries are verified."
        }
      ]
    };
  }

  function buildVerificationItems() {
    const triage = triagePayload();
    const issues = Array.isArray(triage.issues) ? triage.issues : [];

    return issues
      .filter(issue => issue.must_fix_before_next_tester || issue.priority === "blocker" || issue.priority === "high")
      .map((issue, index) => ({
        id: "VERIFY-" + safeText(issue.feedback_id || issue.id, String(index + 1)).replace(/[^A-Z0-9-]/gi, "").toUpperCase(),
        issue_id: safeText(issue.id, "TRIAGE-" + (index + 1)),
        feedback_id: safeText(issue.feedback_id, "FB-" + (index + 1)),
        room: safeText(issue.room, "All Rooms"),
        issue_type: safeText(issue.issue_type, "issue"),
        priority: safeText(issue.priority, "high"),
        fix_required: true,
        verification_status: "pending-owner-verification",
        evidence_note: "Owner must verify fix, rerun related checks, and confirm tester wording before next invite.",
        rerun_required: ["V40", "V41", "V42", "V43"],
        original_summary: safeText(issue.summary, "Must-fix issue."),
        owner_action: safeText(issue.owner_action, "Verify this fix before next tester."),
        private: true
      }));
  }

  function buildFallbackPayload() {
    const items = buildVerificationItems();
    const blocker = items.filter(item => item.priority === "blocker").length;
    const high = items.filter(item => item.priority === "high").length;
    const pending = items.filter(item => item.verification_status !== "verified").length;

    let verificationStatus = "FIX VERIFICATION REQUIRED";
    if (!items.length) verificationStatus = "NO MUST-FIX ITEMS";
    else if (pending > 0) verificationStatus = "PENDING OWNER VERIFICATION";
    else verificationStatus = "VERIFIED";

    return {
      version: VERSION,
      source: "v44_safe_fix_verification_fallback",
      verification_status: verificationStatus,
      next_tester_fix_gate: pending > 0 ? "blocked_until_verified" : "verification_clear",
      items,
      summary: {
        total_items: items.length,
        blocker,
        high,
        pending,
        verified: items.filter(item => item.verification_status === "verified").length,
        rerun_required: items.filter(item => item.rerun_required && item.rerun_required.length).length
      },
      verification_checklist: [
        "Confirm the issue was fixed in the room where it appeared.",
        "Confirm wording no longer feels like trading pressure.",
        "Confirm stale/guarded/fallback data labels are visible.",
        "Confirm Live Auto Locked and no-execution boundaries are visible.",
        "Rerun V40, V41, V42, and V43 after fixes.",
        "Document owner evidence notes before the next tester."
      ],
      owner_evidence_fields: [
        "fix_summary",
        "room_checked",
        "before_after_note",
        "rerun_receipt",
        "owner_decision",
        "next_tester_allowed"
      ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        fix_verification_private: true,
        owner_verification_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        fix_verification_does_not_create_permission: true
      },
      warnings: [
        "Fix verification is private.",
        "Pending verification blocks next tester clearance.",
        "No public proof.",
        "No broker wiring.",
        "No execution permission changed."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      verification_status: safe.verification_status || fallback.verification_status,
      next_tester_fix_gate: safe.next_tester_fix_gate || fallback.next_tester_fix_gate,
      items: Array.isArray(safe.items) ? safe.items : fallback.items,
      summary: { ...(fallback.summary || {}), ...(safe.summary || {}) },
      verification_checklist: Array.isArray(safe.verification_checklist) ? safe.verification_checklist : fallback.verification_checklist,
      owner_evidence_fields: Array.isArray(safe.owner_evidence_fields) ? safe.owner_evidence_fields : fallback.owner_evidence_fields,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        fix_verification_private: true,
        owner_verification_required: true,
        no_public_proof: true,
        no_public_launch: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        fix_verification_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_fix_verification_v44: normalized,
      private_beta_fix_gate: normalized.next_tester_fix_gate
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaFixVerificationUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchVerification() {
    verifyState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      verifyState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        verifyState.status = "ready";
        verifyState.source = normalized.source || "fix_verification_snapshot";
        verifyState.payload = normalized;
        verifyState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        verifyState.status = "guarded_fallback";
        verifyState.source = "guarded_fix_verification_fallback";
        verifyState.payload = fallback;
        verifyState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      verifyState.status = "error_fallback";
      verifyState.source = "fetch_error_fallback";
      verifyState.payload = fallback;
      verifyState.fallbackActive = true;
      verifyState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return verifyState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("pending") || text.includes("required") || text.includes("blocker")) return "red";
    if (text.includes("high") || text.includes("rerun")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-beta-fix-verification-card"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function itemRow(item, index) {
    return `
      <div class="ob-beta-fix-verification-row">
        <div class="ob-beta-fix-verification-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.feedback_id, item.issue_id)}</strong>
          <span>${safeText(item.room, "Room")} · ${safeText(item.issue_type, "issue")}</span>
        </div>
        <span>${safeText(item.original_summary, "Must-fix issue.")}<br>${safeText(item.evidence_note, "")}</span>
        <div class="ob-beta-fix-verification-status ${statusClass(item.verification_status || item.priority)}">${safeText(item.verification_status, "pending")}</div>
      </div>
    `;
  }

  function checklistRow(item, index) {
    return `
      <div class="ob-beta-fix-verification-row">
        <div class="ob-beta-fix-verification-dot">✓</div>
        <div>
          <strong>Verification step ${index + 1}</strong>
          <span>owner evidence required</span>
        </div>
        <span>${safeText(item, "Verification step.")}</span>
        <div class="ob-beta-fix-verification-status gold">check</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = verifyState.payload || buildFallbackPayload();
    const summary = payload.summary || {};
    const items = Array.isArray(payload.items) ? payload.items : [];
    const checklist = Array.isArray(payload.verification_checklist) ? payload.verification_checklist : [];

    return `
      <div class="ob-beta-fix-verification-panel" id="obPrivateBetaFixVerificationPanel" data-ob-v44-fix-verification="true">
        <div class="ob-beta-fix-verification-head">
          <div>
            <div class="ob-label">Private Beta Fix Verification · V44</div>
            <div class="ob-beta-fix-verification-title">Fix Verification Checklist</div>
            <div class="ob-beta-fix-verification-subtitle">${safeText(payload.verification_status, "Owner verification required")} · ${safeText(verifyState.status, "booting")} · must-fix items must be verified before next tester.</div>
          </div>
          <div class="ob-beta-fix-verification-chip-row">
            <span class="ob-beta-fix-verification-chip ${statusClass(payload.next_tester_fix_gate)}">${safeText(payload.next_tester_fix_gate, "review")}</span>
            <span class="ob-beta-fix-verification-chip gold">Evidence notes</span>
            <span class="ob-beta-fix-verification-chip red">No permission</span>
          </div>
        </div>

        <div class="ob-beta-fix-verification-grid">
          ${card("Items", safeText(summary.total_items, items.length))}
          ${card("Blocker", safeText(summary.blocker, "0"))}
          ${card("High", safeText(summary.high, "0"))}
          ${card("Pending", safeText(summary.pending, "0"))}
          ${card("Verified", safeText(summary.verified, "0"))}
          ${card("Rerun", safeText(summary.rerun_required, "0"))}
          ${card("Gate", safeText(payload.next_tester_fix_gate, "review"))}
        </div>

        <div class="ob-beta-fix-verification-section">
          <div class="ob-beta-fix-verification-section-title">Must-fix verification items</div>
          <div class="ob-beta-fix-verification-list">
            ${items.length ? items.map(itemRow).join("") : `
              <div class="ob-beta-fix-verification-row">
                <div class="ob-beta-fix-verification-dot">✓</div>
                <div><strong>No must-fix items</strong><span>owner review</span></div>
                <span>No must-fix items are listed in the current verification payload.</span>
                <div class="ob-beta-fix-verification-status green">clear</div>
              </div>
            `}
          </div>
        </div>

        <div class="ob-beta-fix-verification-section">
          <div class="ob-beta-fix-verification-section-title">Verification checklist</div>
          <div class="ob-beta-fix-verification-list">${checklist.map(checklistRow).join("")}</div>
        </div>

        <div class="ob-beta-fix-verification-callout">
          <strong>Owner evidence fields</strong><br>
          ${(payload.owner_evidence_fields || []).map((item, idx) => `${idx + 1}. ${item}`).join("<br>")}
        </div>

        <div class="ob-beta-fix-verification-note"><strong>Soulaana:</strong><br>A fix is not real until the owner can point to what changed, where it changed, and why the next tester is safer.</div>
        <div class="ob-beta-fix-verification-boundary"><strong>Boundary:</strong><br>Fix verification is private. It cannot create permission. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.</div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaFixVerificationPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const closeout = document.getElementById("obPrivateBetaSessionCloseoutPanel");
    const triage = document.getElementById("obPrivateBetaIssueTriagePanel");
    const runbook = document.getElementById("obPrivateBetaSessionRunbookPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (closeout && closeout.parentNode) closeout.insertAdjacentElement("afterend", panel);
    else if (triage && triage.parentNode) triage.insertAdjacentElement("afterend", panel);
    else if (runbook && runbook.parentNode) runbook.insertAdjacentElement("afterend", panel);
    else layer.appendChild(panel);
  }

  function setFlags() {
    const payload = verifyState.payload || buildFallbackPayload();
    document.body.setAttribute("data-ob-v44-fix-verification", "ready");
    window.OB_V44_PRIVATE_BETA_FIX_VERIFICATION_STATE = {
      version: VERSION,
      status: verifyState.status,
      fallbackActive: verifyState.fallbackActive,
      verificationStatus: payload.verification_status,
      nextTesterFixGate: payload.next_tester_fix_gate,
      ownerVerificationRequired: true,
      privateBetaOnly: true,
      noPublicProof: true,
      noPublicLaunch: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchVerification();
    }, 2580);
  }

  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("obPrivateBetaIssueTriageUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_FIX_VERIFICATION_V44_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return verifyState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchVerification,
    renderPanel,
    setFlags
  };
})();
