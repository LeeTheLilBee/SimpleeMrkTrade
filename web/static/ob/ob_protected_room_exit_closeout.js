
// OB_GIANT_PACK_049_PROTECTED_ROOM_EXIT_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP049";

  const STATUS_ENDPOINT =
    "/ob/protected-room-exit/status.json";

  const state = {
    version: VERSION,
    status: null,
    ready: false,
    pendingLockbacks: 0,
    acknowledgedLockbacks: 0,
    error: null
  };

  function updateBody() {
    if (!document.body) return;

    document.body.dataset.obProtectedRoomExitPack =
      VERSION;

    document.body.dataset.obProtectedRoomExitState =
      state.ready ? "ready" : "hold";

    document.body.dataset.obPendingTowerLockbacks =
      String(state.pendingLockbacks);

    document.body.dataset.obAcknowledgedTowerLockbacks =
      String(state.acknowledgedLockbacks);

    document.body.dataset.obSelfLockbackAllowed =
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
          "Protected-room exit status failed: " +
          response.status
        );
      }

      const payload = await response.json();

      state.status = payload;

      state.ready = Boolean(
        payload &&
        payload.ok === true &&
        payload.context_revocation_required === true &&
        payload.session_close_required === true &&
        payload.tower_lockback_authority === true &&
        payload.ob_self_lockback_allowed === false
      );

      state.pendingLockbacks =
        Number(payload.lockback_required || 0);

      state.acknowledgedLockbacks =
        Number(payload.lockback_acknowledged || 0);

      state.error = null;

    } catch (error) {
      state.status = null;
      state.ready = false;
      state.pendingLockbacks = 0;
      state.acknowledgedLockbacks = 0;

      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    updateBody();

    window.dispatchEvent(
      new CustomEvent(
        "ob:protected-room-exit-state",
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

  window.OB_PROTECTED_ROOM_EXIT_GP049 = {
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
