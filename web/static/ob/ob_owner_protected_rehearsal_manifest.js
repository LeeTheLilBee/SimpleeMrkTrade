
// OB_GIANT_PACK_051_OWNER_PROTECTED_REHEARSAL_MANIFEST_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP051";

  const STATUS_ENDPOINT =
    "/ob/owner-rehearsal-runs/status.json";

  const state = {
    version: VERSION,
    status: null,
    ready: false,
    activeRuns: 0,
    heldRuns: 0,
    completedRuns: 0,
    error: null
  };

  function updateBody() {
    if (!document.body) return;

    document.body.dataset.obOwnerRehearsalPack =
      VERSION;

    document.body.dataset.obOwnerRehearsalState =
      state.ready ? "ready" : "hold";

    document.body.dataset.obOwnerRehearsalActiveRuns =
      String(state.activeRuns);

    document.body.dataset.obOwnerRehearsalHeldRuns =
      String(state.heldRuns);

    document.body.dataset.obOwnerRehearsalCompletedRuns =
      String(state.completedRuns);

    document.body.dataset.obOwnerRehearsalDryRunOnly =
      "true";

    document.body.dataset.obTowerLaunchAuthorized =
      "false";

    document.body.dataset.obProductionManualLive =
      "unauthorized";

    document.body.dataset.obLiveAuto =
      "locked";
  }

  async function refresh() {
    try {
      const response = await fetch(
        STATUS_ENDPOINT,
        {
          method: "GET",
          credentials: "same-origin",
          headers: {
            "Accept": "application/json"
          }
        }
      );

      if (!response.ok) {
        throw new Error(
          "Owner rehearsal status failed: " +
          response.status
        );
      }

      const payload = await response.json();

      state.status = payload;

      state.ready = Boolean(
        payload &&
        payload.ok === true &&
        payload.canonical_step_count === 10 &&
        payload.gp050_ready_assessment_required === true &&
        payload.strict_step_order_required === true &&
        payload.step_evidence_required === true &&
        payload.dry_run_only === true &&
        payload.tower_launch_authorized === false
      );

      state.activeRuns =
        Number(payload.run_active || 0);

      state.heldRuns =
        Number(payload.run_on_hold || 0);

      state.completedRuns =
        Number(payload.run_completed || 0);

      state.error = null;

    } catch (error) {
      state.status = null;
      state.ready = false;
      state.activeRuns = 0;
      state.heldRuns = 0;
      state.completedRuns = 0;

      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    updateBody();

    window.dispatchEvent(
      new CustomEvent(
        "ob:owner-protected-rehearsal-state",
        {
          detail: Object.assign(
            {},
            state
          )
        }
      )
    );

    return Object.assign(
      {},
      state
    );
  }

  window.OB_OWNER_PROTECTED_REHEARSAL_GP051 = {
    version: VERSION,

    getState: function () {
      return Object.assign(
        {},
        state
      );
    },

    refresh: refresh
  };

  document.addEventListener(
    "DOMContentLoaded",
    function () {
      updateBody();
      refresh();
    }
  );
})();
