
// OB_GIANT_PACK_047_PROTECTED_LAUNCH_SESSION_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP047";

  const STATUS_ENDPOINT =
    "/ob/tower-protected-launch-sessions/status.json";

  const state = {
    version: VERSION,
    status: null,
    ready: false,
    activeSessionCount: 0,
    error: null
  };

  function updateBody() {
    if (!document.body) return;

    document.body.dataset.obProtectedLaunchSessionPack =
      VERSION;

    document.body.dataset.obProtectedLaunchSessionState =
      state.ready ? "ready" : "hold";

    document.body.dataset.obProtectedLaunchActiveSessions =
      String(state.activeSessionCount);

    document.body.dataset.obProtectedLaunchRoomSwitch =
      "disabled";

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
          "Protected launch session status failed: " +
          response.status
        );
      }

      const payload = await response.json();

      state.status = payload;
      state.ready = Boolean(
        payload &&
        payload.ok === true &&
        payload.single_active_room_per_owner === true &&
        payload.room_switch_allowed === false &&
        payload.expiration_extension_allowed === false
      );

      state.activeSessionCount =
        Number(payload.active || 0);

      state.error = null;

    } catch (error) {
      state.status = null;
      state.ready = false;
      state.activeSessionCount = 0;
      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    updateBody();

    window.dispatchEvent(
      new CustomEvent(
        "ob:protected-launch-session-state",
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

  window.OB_PROTECTED_LAUNCH_SESSION_GP047 = {
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
