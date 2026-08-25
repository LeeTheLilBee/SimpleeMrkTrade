
(function (global) {
  "use strict";

  const VERSION =
    "OBUX071-075";

  const NORMAL_DASHBOARD =
    "/ob/dashboard";

  const OWNER_DASHBOARD =
    "/ob/owner-dashboard";


  function normalizedPath() {
    const value =
      String(
        global.location.pathname
        || "/"
      )
        .toLowerCase()
        .replace(
          /\/+$/,
          ""
        );

    return value || "/";
  }


  function isObProductRoute() {
    return normalizedPath()
      .startsWith(
        "/ob/"
      );
  }


  function missionUiAllowed() {
    return (
      normalizedPath()
      === OWNER_DASHBOARD
    );
  }


  function v27UiAllowed() {
    /*
      V27 is historical/proof UI.

      No real /ob/* product room
      is allowed to render it.
    */
    return !isObProductRoute();
  }


  const MISSION_SELECTORS = [
    "#obMissionBar",
    ".ob-mission-bar",
    "#obMissionDrawer",
    "#obMissionDrawerBackdrop",
    ".ob-mission-drawer-backdrop",
  ];


  const V27_SELECTORS = [
    "#obRoomDataPolishPanel",
    ".ob-room-polish-panel",
    "[data-ob-v27-room-data-polish]",
    "[data-ob-v27-proof]",
  ];


  function removeMatches(
    selectors
  ) {
    selectors.forEach(
      function (
        selector
      ) {
        document
          .querySelectorAll(
            selector
          )
          .forEach(
            function (
              node
            ) {
              node.remove();
            }
          );
      }
    );
  }


  function removeLegacyFlags() {
    if (
      !document.body
    ) {
      return;
    }

    if (
      !missionUiAllowed()
    ) {
      document.body
        .removeAttribute(
          "data-ob-mission"
        );
    }

    if (
      !v27UiAllowed()
    ) {
      document.body
        .removeAttribute(
          "data-ob-v27-room-data-polish"
        );
    }
  }


  function purge() {
    if (
      !missionUiAllowed()
    ) {
      removeMatches(
        MISSION_SELECTORS
      );
    }

    if (
      !v27UiAllowed()
    ) {
      removeMatches(
        V27_SELECTORS
      );
    }

    removeLegacyFlags();
  }


  function installHardStyle() {
    if (
      document.getElementById(
        "obProductSurfaceHardPolicyStyle"
      )
    ) {
      return;
    }

    const rules = [];

    if (
      !missionUiAllowed()
    ) {
      rules.push(`
        #obMissionBar,
        .ob-mission-bar,
        #obMissionDrawer,
        #obMissionDrawerBackdrop,
        .ob-mission-drawer-backdrop {
          display: none !important;
          visibility: hidden !important;
          pointer-events: none !important;
        }
      `);
    }

    if (
      !v27UiAllowed()
    ) {
      rules.push(`
        #obRoomDataPolishPanel,
        .ob-room-polish-panel,
        [data-ob-v27-room-data-polish],
        [data-ob-v27-proof] {
          display: none !important;
          visibility: hidden !important;
          pointer-events: none !important;
        }
      `);
    }

    if (
      !rules.length
    ) {
      return;
    }

    const style =
      document.createElement(
        "style"
      );

    style.id =
      "obProductSurfaceHardPolicyStyle";

    style.textContent =
      rules.join(
        "\n"
      );

    (
      document.head
      || document.documentElement
    ).appendChild(
      style
    );
  }


  installHardStyle();


  const observer =
    new MutationObserver(
      function () {
        purge();
      }
    );


  observer.observe(
    document.documentElement,
    {
      childList:
        true,

      subtree:
        true,
    }
  );


  document.addEventListener(
    "DOMContentLoaded",
    function () {
      purge();

      /*
        Short defensive pulses cover
        historical delayed renderers.
      */
      [
        0,
        100,
        600,
        1200,
        2500,
        4000,
      ].forEach(
        function (
          delay
        ) {
          global.setTimeout(
            purge,
            delay
          );
        }
      );
    }
  );


  global.addEventListener(
    "obEngineFeedAdapterUpdated",
    purge
  );


  global.addEventListener(
    "ob:arrival-complete",
    purge
  );


  global.OBProductSurfacePolicy =
    Object.freeze(
      {
        version:
          VERSION,

        path:
          normalizedPath,

        isObProductRoute,

        missionUiAllowed,

        v27UiAllowed,

        purge,
      }
    );

})(window);
