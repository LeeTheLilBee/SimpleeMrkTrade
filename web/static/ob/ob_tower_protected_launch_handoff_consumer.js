
// OB_GIANT_PACK_046_TOWER_PROTECTED_LAUNCH_HANDOFF_CONSUMER_BROWSER_ADAPTER

(function () {
  "use strict";

  const VERSION = "GP046";
  const STATUS_ENDPOINT =
    "/ob/tower-protected-launch-handoffs/status.json";
  const REGISTRY_ENDPOINT =
    "/ob/tower-protected-launch-room-registry.json";

  const state = {
    version: VERSION,
    status: null,
    registry: null,
    ready: false,
    error: null
  };

  function setBodyFlags() {
    if (!document.body) return;

    document.body.dataset.obTowerLaunchConsumer =
      state.ready ? "ready" : "hold";

    document.body.dataset.obTowerLaunchPack =
      VERSION;

    document.body.dataset.obProductionManualLive =
      "unauthorized";

    document.body.dataset.obLiveAuto =
      "locked";
  }

  async function readJson(url) {
    const response = await fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      throw new Error(
        "Tower launch consumer request failed: " +
        response.status
      );
    }

    return response.json();
  }

  async function refresh() {
    try {
      const results = await Promise.all([
        readJson(STATUS_ENDPOINT),
        readJson(REGISTRY_ENDPOINT)
      ]);

      state.status = results[0];
      state.registry = results[1];
      state.ready = Boolean(
        state.status &&
        state.status.ok === true &&
        state.registry &&
        state.registry.ok === true &&
        state.registry.room_count === 6
      );
      state.error = null;
    } catch (error) {
      state.ready = false;
      state.error = String(
        error && error.message
          ? error.message
          : error
      );
    }

    setBodyFlags();

    window.dispatchEvent(
      new CustomEvent(
        "ob:tower-launch-consumer-state",
        {
          detail: Object.assign({}, state)
        }
      )
    );

    return Object.assign({}, state);
  }

  window.OB_TOWER_PROTECTED_LAUNCH_GP046 = {
    version: VERSION,
    getState: function () {
      return Object.assign({}, state);
    },
    refresh: refresh
  };

  document.addEventListener(
    "DOMContentLoaded",
    function () {
      setBodyFlags();
      refresh();
    }
  );
})();
