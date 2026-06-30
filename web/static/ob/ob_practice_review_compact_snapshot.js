// OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT";
  const ENDPOINT = "/ob/practice-review-compact-snapshot.json";

  // SMOKE MARKERS
  // Practice Review Compact Snapshot
  // practice review compact snapshot
  // compact owner snapshot
  // metrics compact summary
  // guidance compact summary
  // focus queue compact summary
  // lock wall compact summary
  // next action compact summary
  // owner-readable snapshot
  // practice-only snapshot
  // not real Manual Live snapshot
  // dashboard-ready compact snapshot
  // review center compact handoff
  // owner console compact handoff
  // snapshot source map
  // snapshot readiness
  // no database write
  // no file write
  // no save endpoint
  // no real record creation
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let snapshotState = {
    status: "booting",
    httpStatus: null,
    source: "fallback",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_029_safe_fallback",
      snapshot_state: {
        snapshot_id: "ob_practice_review_compact_snapshot_001",
        label: "Practice Review Compact Snapshot",
        status: "practice_review_compact_snapshot_ready",
        section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        purpose: "Compress metrics, guidance, focus queue, locks, and next action into one owner-readable practice snapshot.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        metrics_source: "/ob/practice-repetition-metrics-board.json",
        guidance_source: "/ob/owner-review-polish-guidance.json",
        focus_queue_source: "/ob/owner-practice-focus-queue.json"
      },
      compact_summary: {
        headline: "Practice is getting cleaner, but checklist/fill still needs reps.",
        owner_readable_status: "Owner practice ready — real Manual Live still locked.",
        top_metric: "12 practice runs · 7 complete · 74% average completion",
        top_guidance: "Repeat is not failure. It means drill the step until it becomes automatic.",
        top_focus: "Repeat checklist/fill path in Proof/Demo with option-style fake candidate.",
        lock_summary: "No broker, bank, database, save endpoint, or direct Vault action is enabled.",
        next_action: "Run one more Proof/Demo checklist/fill practice loop.",
        status: "ready"
      },
      compact_cards: [
        {
          card_id: "compact_metrics",
          label: "Metrics",
          headline: "Completion up, blockers down.",
          body: "Practice loops are finishing more often, and blockers are lower than before.",
          source: "practice_repetition_metrics_board",
          status: "ready"
        },
        {
          card_id: "compact_guidance",
          label: "Guidance",
          headline: "Repeat means drill, not failure.",
          body: "The next repeat is about making the checklist/fill path automatic.",
          source: "owner_review_polish_guidance",
          status: "ready"
        },
        {
          card_id: "compact_focus",
          label: "Focus",
          headline: "Start with checklist/fill.",
          body: "Use Proof/Demo and option-style fake candidate. Done means no missing checklist fields and one clear lesson note.",
          source: "owner_practice_focus_queue",
          status: "ready"
        },
        {
          card_id: "compact_locks",
          label: "Locks",
          headline: "Real Manual Live still locked.",
          body: "Hybrid, Automated, broker, bank, database, save endpoint, and direct Vault actions are blocked.",
          source: "pre_live_lock_wall",
          status: "locked"
        },
        {
          card_id: "compact_next_action",
          label: "Next action",
          headline: "Do one clean Proof/Demo rep.",
          body: "Repeat the checklist/fill path and explain why dry-run save is not a real save.",
          source: "focus_queue",
          status: "recommended"
        }
      ],
      source_map: [
        {
          source_id: "metrics_board",
          label: "Practice Repetition Metrics Board",
          route: "/ob/practice-repetition-metrics-board.json",
          contributes: "runs, completion, blockers, trends, distributions",
          status: "ready"
        },
        {
          source_id: "owner_guidance",
          label: "Owner Review Polish Guidance",
          route: "/ob/owner-review-polish-guidance.json",
          contributes: "plain-language explanations and practice-only reminders",
          status: "ready"
        },
        {
          source_id: "focus_queue",
          label: "Owner Practice Focus Queue",
          route: "/ob/owner-practice-focus-queue.json",
          contributes: "ordered next-practice task and done criteria",
          status: "ready"
        },
        {
          source_id: "lock_wall",
          label: "Pre-Live Lock Wall",
          route: "/ob/manual-live-pre-live-lock-wall.json",
          contributes: "real Manual Live, Hybrid, Automated, broker, bank, persistence, and Vault locks",
          status: "locked"
        }
      ],
      compact_snapshot_slots: [
        {
          slot_id: "dashboard_slot",
          label: "Dashboard compact slot",
          purpose: "Show the owner the current practice status and next action.",
          target_room: "dashboard",
          status: "ready"
        },
        {
          slot_id: "review_center_slot",
          label: "Review Center compact handoff",
          purpose: "Send owner to practice lessons and review details.",
          target_room: "review_center",
          status: "ready"
        },
        {
          slot_id: "owner_console_slot",
          label: "Owner Console compact handoff",
          purpose: "Show practice/readiness boundary in owner command room.",
          target_room: "owner_console",
          status: "ready"
        },
        {
          slot_id: "trade_center_slot",
          label: "Trade Center practice-only reminder",
          purpose: "Remind owner that this is not real trade execution.",
          target_room: "trade_center",
          status: "locked"
        }
      ],
      snapshot_readiness: {
        total_sources: 4,
        ready_sources: 3,
        locked_sources: 1,
        compact_cards: 5,
        dashboard_ready: true,
        review_center_ready: true,
        owner_console_ready: true,
        readiness_label: "compact_snapshot_ready",
        status: "ready"
      },
      blocked_actions: [
        "write_compact_snapshot_database_now",
        "write_compact_snapshot_file_now",
        "create_compact_snapshot_save_endpoint_now",
        "persist_compact_snapshot_now",
        "create_real_snapshot_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_compact_snapshot",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_snapshot_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_review_compact_snapshot_only: true,
        dry_run_only: true,
        compact_snapshot_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};
    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      snapshot_state: { ...(fallback.snapshot_state || {}), ...(safe.snapshot_state || {}) },
      compact_summary: { ...(fallback.compact_summary || {}), ...(safe.compact_summary || {}) },
      compact_cards: Array.isArray(safe.compact_cards) ? safe.compact_cards : fallback.compact_cards,
      source_map: Array.isArray(safe.source_map) ? safe.source_map : fallback.source_map,
      compact_snapshot_slots: Array.isArray(safe.compact_snapshot_slots) ? safe.compact_snapshot_slots : fallback.compact_snapshot_slots,
      snapshot_readiness: { ...(fallback.snapshot_readiness || {}), ...(safe.snapshot_readiness || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_review_compact_snapshot_only: true,
        dry_run_only: true,
        compact_snapshot_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRACTICE_REVIEW_COMPACT_SNAPSHOT_GP029 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      practice_review_compact_snapshot_gp029: normalized,
      practiceReviewCompactSnapshotOnly: true,
      dryRunOnly: true,
      compactSnapshotPreviewOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obPracticeReviewCompactSnapshotUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchSnapshot() {
    snapshotState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      snapshotState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        snapshotState.status = "ready";
        snapshotState.source = normalized.source || "server";
        snapshotState.payload = normalized;
        snapshotState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        snapshotState.status = "guarded_fallback";
        snapshotState.source = "guarded_fallback";
        snapshotState.payload = fallback;
        snapshotState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      snapshotState.status = "error_fallback";
      snapshotState.source = "error_fallback";
      snapshotState.payload = fallback;
      snapshotState.fallbackActive = true;
      snapshotState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return snapshotState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked")) return "red";
    if (text.includes("ready") || text.includes("recommended")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-practice-review-compact-snapshot-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-practice-review-compact-snapshot-row">
        <div class="ob-practice-review-compact-snapshot-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.source_id || item.slot_id || item.card_id, "Item")}</strong>
          <span>${safeText(item.status || item.target_room || "snapshot", "snapshot")}</span>
        </div>
        <span>${safeText(item.body || item.contributes || item.purpose || item.headline || "detail", "detail")}</span>
        <div class="ob-practice-review-compact-snapshot-status ${tone(item.status)}">${safeText(item.status || "ready", "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-practice-review-compact-snapshot-row">
        <div class="ob-practice-review-compact-snapshot-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP029 compact snapshot boundaries.</span>
        <div class="ob-practice-review-compact-snapshot-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = snapshotState.payload || buildFallbackPayload();
    const state = payload.snapshot_state || {};
    const summary = payload.compact_summary || {};
    const cards = Array.isArray(payload.compact_cards) ? payload.compact_cards : [];
    const sources = Array.isArray(payload.source_map) ? payload.source_map : [];
    const slots = Array.isArray(payload.compact_snapshot_slots) ? payload.compact_snapshot_slots : [];
    const readiness = payload.snapshot_readiness || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-practice-review-compact-snapshot-panel" id="obPracticeReviewCompactSnapshotPanel" data-ob-giant-pack-029="true">
        <div class="ob-practice-review-compact-snapshot-head">
          <div>
            <div class="ob-label">OB Giant Pack 029 · Compact Snapshot</div>
            <div class="ob-practice-review-compact-snapshot-title">Practice Review Compact Snapshot</div>
            <div class="ob-practice-review-compact-snapshot-subtitle">
              ${safeText(snapshotState.status, "booting")} · ${safeText(state.status, "practice_review_compact_snapshot_ready")} · owner-readable snapshot.
            </div>
          </div>
          <div class="ob-practice-review-compact-snapshot-chip-row">
            <span class="ob-practice-review-compact-snapshot-chip green">Compact summary</span>
            <span class="ob-practice-review-compact-snapshot-chip gold">Next action</span>
            <span class="ob-practice-review-compact-snapshot-chip red">Practice-only</span>
            <span class="ob-practice-review-compact-snapshot-chip red">No save endpoint</span>
          </div>
        </div>

        <div class="ob-practice-review-compact-snapshot-stat-grid">
          ${card("Sources", safeText(readiness.ready_sources, "0") + "/" + safeText(readiness.total_sources, "0"))}
          ${card("Cards", safeText(readiness.compact_cards, "0"))}
          ${card("Dashboard", safeText(readiness.dashboard_ready, "false"))}
          ${card("Review", safeText(readiness.review_center_ready, "false"))}
          ${card("Label", safeText(readiness.readiness_label, "compact_snapshot_ready"))}
        </div>

        <div class="ob-practice-review-compact-snapshot-grid">
          <div>
            <div class="ob-practice-review-compact-snapshot-card">
              <span>Snapshot headline</span>
              <strong>${safeText(summary.headline, "Practice snapshot ready.")}</strong>
              <div class="ob-practice-review-compact-snapshot-callout">
                <strong>Status:</strong><br>
                ${safeText(summary.owner_readable_status, "Owner practice ready — real Manual Live still locked.")}
              </div>
              <div class="ob-practice-review-compact-snapshot-callout">
                <strong>Next action:</strong><br>
                ${safeText(summary.next_action, "Run the next Proof/Demo practice loop.")}
              </div>
              <div class="ob-practice-review-compact-snapshot-boundary">
                <strong>Lock summary:</strong><br>
                ${safeText(summary.lock_summary, "No live action is enabled.")}
              </div>
            </div>

            <div class="ob-practice-review-compact-snapshot-card" style="margin-top: 11px;">
              <span>Compact rollup</span>
              <strong>${safeText(summary.top_metric, "Metrics unavailable")}</strong>
              <div class="ob-practice-review-compact-snapshot-callout">
                ${safeText(summary.top_guidance, "Repeat is not failure.")}<br><br>
                ${safeText(summary.top_focus, "Repeat checklist/fill path.")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-practice-review-compact-snapshot-section">
              <div class="ob-practice-review-compact-snapshot-section-title">Compact cards</div>
              <div class="ob-practice-review-compact-snapshot-list">${cards.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-practice-review-compact-snapshot-section">
              <div class="ob-practice-review-compact-snapshot-section-title">Snapshot source map</div>
              <div class="ob-practice-review-compact-snapshot-list">${sources.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-practice-review-compact-snapshot-section">
              <div class="ob-practice-review-compact-snapshot-section-title">Room slots / handoffs</div>
              <div class="ob-practice-review-compact-snapshot-list">${slots.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-practice-review-compact-snapshot-section">
              <div class="ob-practice-review-compact-snapshot-section-title">Blocked actions</div>
              <div class="ob-practice-review-compact-snapshot-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-practice-review-compact-snapshot-callout">
          <strong>Next handoff:</strong><br>
          GP030 can close the mini-section with Practice Review Polish Readiness + save-batch checkpoint.
        </div>

        <div class="ob-practice-review-compact-snapshot-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPracticeReviewCompactSnapshotPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const focusQueue = document.getElementById("obOwnerPracticeFocusQueuePanel");
    const guidance = document.getElementById("obOwnerReviewPolishGuidancePanel");
    const metrics = document.getElementById("obPracticeRepetitionMetricsBoardPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (focusQueue && focusQueue.parentNode) focusQueue.insertAdjacentElement("afterend", panel);
    else if (guidance && guidance.parentNode) guidance.insertAdjacentElement("afterend", panel);
    else if (metrics && metrics.parentNode) metrics.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = snapshotState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-029-practice-review-compact-snapshot", "ready");
    document.body.setAttribute("data-ob-practice-review-compact-snapshot-only", "true");
    document.body.setAttribute("data-ob-compact-snapshot-preview-only", "true");
    document.body.setAttribute("data-ob-dry-run-only", "true");
    document.body.setAttribute("data-ob-no-database-write", "true");
    document.body.setAttribute("data-ob-no-file-write", "true");
    document.body.setAttribute("data-ob-no-save-endpoint", "true");
    document.body.setAttribute("data-ob-no-real-record-creation", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_029_PRACTICE_REVIEW_COMPACT_SNAPSHOT_STATE = {
      version: VERSION,
      status: snapshotState.status,
      fallbackActive: snapshotState.fallbackActive,
      compactCardCount: payload.compact_cards.length,
      readySources: payload.snapshot_readiness.ready_sources,
      readinessLabel: payload.snapshot_readiness.readiness_label,
      practiceReviewCompactSnapshotOnly: true,
      compactSnapshotPreviewOnly: true,
      dryRunOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchSnapshot();
    }, 6780);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_PRACTICE_REVIEW_COMPACT_SNAPSHOT_GP029_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return snapshotState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchSnapshot,
    renderPanel,
    setFlags
  };
})();
