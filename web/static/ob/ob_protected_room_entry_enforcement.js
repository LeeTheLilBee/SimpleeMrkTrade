
// OB_GIANT_PACK_048_PROTECTED_ROOM_ENTRY_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP048";

  const STATUS_ENDPOINT =
    "/ob/protected-room-entry/status.json";

  const state = {
    version: VERSION,
    status: null,
    ready: false,
    defaultDeny: true,
    error: null
  };

  function updateBody() {
    if (!document.body) return;

    document.body.dataset.obProtectedRoomEntryPack =
      VERSION;

    document.body.dataset.obProtectedRoomEntryState =
      state.ready ? "ready" : "hold";

    document.body.dataset.obProtectedRoomEntryDefaultDeny =
      "true";

    document.body.dataset.obProtectedRoomSwitch =
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
          "Protected-room entry status failed: " +
          response.status
        );
      }

      const payload = await response.json();

      state.status = payload;

      state.ready = Boolean(
        payload &&
        payload.ok === true &&
        payload.default_deny === true &&
        payload.one_active_context_per_session === true &&
        payload.room_switch_allowed === false &&
        payload.context_can_outlive_session === false
      );

      state.defaultDeny = true;
      state.error = null;

    } catch (error) {
      state.status = null;
      state.ready = false;
      state.defaultDeny = true;

      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    updateBody();

    window.dispatchEvent(
      new CustomEvent(
        "ob:protected-room-entry-state",
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

  window.OB_PROTECTED_ROOM_ENTRY_GP048 = {
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
