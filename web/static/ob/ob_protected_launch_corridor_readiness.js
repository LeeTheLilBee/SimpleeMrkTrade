
// OB_GIANT_PACK_050_PROTECTED_LAUNCH_CORRIDOR_READINESS_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP050";

  const STATUS_ENDPOINT =
    "/ob/protected-launch-corridor/status.json";

  const state = {
    version: VERSION,
    status: null,
    ready: false,
    assessmentTotal: 0,
    error: null
  };

  function updateBody() {
    if (!document.body) return;

    document.body.dataset.obProtectedLaunchCorridorPack =
      VERSION;

    document.body.dataset.obProtectedLaunchCorridorState =
      state.ready ? "ready" : "hold";

    document.body.dataset.obReadinessAssessmentTotal =
      String(state.assessmentTotal);

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
          "Protected launch corridor status failed: " +
          response.status
        );
      }

      const payload = await response.json();

      state.status = payload;

      state.ready = Boolean(
        payload &&
        payload.ok === true &&
        payload.ready_means_local_ob_readiness_only === true &&
        payload.tower_launch_authorized === false &&
        payload.tower_remains_launch_authority === true
      );

      state.assessmentTotal =
        Number(payload.assessment_total || 0);

      state.error = null;

    } catch (error) {
      state.status = null;
      state.ready = false;
      state.assessmentTotal = 0;

      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    updateBody();

    window.dispatchEvent(
      new CustomEvent(
        "ob:protected-launch-corridor-readiness",
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

  window.OB_PROTECTED_LAUNCH_CORRIDOR_GP050 = {
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
