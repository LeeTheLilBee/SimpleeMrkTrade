(function (global) {
  "use strict";


  const LEGACY_SELECTORS = [
    "#obRoomDataPolishPanel",
    ".ob-room-polish-panel",
    "#obMissionBar",
    ".ob-mission-bar",
    "#obEngineFeedBar",
    "#obDataStatusBar",
    "#obSnapshotDisplayPanel",
  ];


  function path() {
    return global
      .location
      .pathname
      .toLowerCase();
  }


  function isOwnerSurface() {
    return (
      path().includes(
        "owner-dashboard"
      )
      || path().includes(
        "owner-console"
      )
    );
  }


  function isBetaProductSurface() {
    return !isOwnerSurface();
  }


  function currentRoom() {
    const value =
      path();

    if (
      value.includes(
        "/symbol/"
      )
    ) {
      return "Symbol Room";
    }

    if (
      value.includes(
        "market-map"
      )
    ) {
      return "Market Map";
    }

    if (
      value.includes(
        "trade-center"
      )
    ) {
      return "Trade Center";
    }

    if (
      value.includes(
        "review-center"
      )
    ) {
      return "Review Center";
    }

    if (
      value.includes(
        "owner-dashboard"
      )
    ) {
      return "Owner Dashboard";
    }

    if (
      value.includes(
        "owner-console"
      )
    ) {
      return "Owner Console";
    }

    return "Dashboard";
  }


  function currentMode() {
    try {
      const snapshot =
        global.OBSessionState
        && global
          .OBSessionState
          .snapshot
          ? global
              .OBSessionState
              .snapshot()
          : null;

      return (
        snapshot
        && snapshot.persistent
        && snapshot
          .persistent
          .selectedMode
          ? snapshot
              .persistent
              .selectedMode
          : "Survey"
      );
    } catch (_) {
      return "Survey";
    }
  }


  function purgeLegacyProductNoise(
    root
  ) {
    if (
      !isBetaProductSurface()
    ) {
      return;
    }

    const scope =
      root
      && root.querySelectorAll
        ? root
        : document;

    LEGACY_SELECTORS
      .forEach(
        function (
          selector
        ) {
          scope
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

    if (
      document.body
    ) {
      document.body.removeAttribute(
        "data-ob-mission"
      );

      document.body.removeAttribute(
        "data-ob-mission-layout"
      );
    }
  }


  function removeDashboardHeaderButtons() {
    if (
      currentRoom()
        !== "Dashboard"
    ) {
      return;
    }

    document
      .querySelectorAll(
        ".ob-user-header-actions"
      )
      .forEach(
        function (
          node
        ) {
          node.remove();
        }
      );
  }


  function swatches(
    colors
  ) {
    return colors
      .slice(
        0,
        5
      )
      .map(
        function (
          color
        ) {
          return (
            '<i style="background:'
            + color
            + '"></i>'
          );
        }
      )
      .join(
        ""
      );
  }


  function themeChoices() {
    if (
      !global.OBThemeSwitcher
    ) {
      return "";
    }

    const active =
      global
        .OBThemeSwitcher
        .current();

    return global
      .OBThemeSwitcher
      .options()
      .map(
        function (
          theme
        ) {
          return `
            <button
              type="button"
              class="ob-theme-choice${theme.id === active ? " active" : ""}"
              data-theme-id="${theme.id}"
            >
              <span>
                <strong>
                  ${theme.label}
                </strong>

                <small>
                  ${
                    theme.id
                      === active
                      ? "Current theme"
                      : "Switch appearance"
                  }
                </small>
              </span>

              <span
                class="ob-theme-swatches"
                aria-hidden="true"
              >
                ${swatches(theme.colors)}
              </span>
            </button>
          `;
        }
      )
      .join(
        ""
      );
  }


  function closeDrawer() {
    const drawer =
      document
        .getElementById(
          "obControlDrawer"
        );

    if (
      !drawer
    ) {
      return;
    }

    drawer
      .classList
      .remove(
        "open"
      );

    drawer
      .setAttribute(
        "aria-hidden",
        "true"
      );
  }


  function openDrawer() {
    let drawer =
      document
        .getElementById(
          "obControlDrawer"
        );

    if (
      !drawer
    ) {
      drawer =
        buildDrawer();
    }

    refreshDrawer(
      drawer
    );

    drawer
      .classList
      .add(
        "open"
      );

    drawer
      .setAttribute(
        "aria-hidden",
        "false"
      );

    const close =
      drawer
        .querySelector(
          "[data-control-close]"
        );

    if (
      close
    ) {
      close.focus();
    }
  }


  function buildDrawer() {
    const drawer =
      document
        .createElement(
          "aside"
        );

    drawer.id =
      "obControlDrawer";

    drawer.className =
      "ob-control-drawer";

    drawer.setAttribute(
      "aria-hidden",
      "true"
    );


    drawer.innerHTML = `
      <div
        class="ob-control-drawer-scrim"
        data-control-close
      ></div>

      <section
        class="ob-control-drawer-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="obControlDrawerTitle"
      >
        <header
          class="ob-control-drawer-header"
        >
          <div>
            <span
              class="ob-kicker"
            >
              THE OBSERVATORY
            </span>

            <h2
              id="obControlDrawerTitle"
            >
              Your controls
            </h2>
          </div>

          <button
            type="button"
            class="ob-control-close"
            data-control-close
            aria-label="Close controls"
          >
            ×
          </button>
        </header>

        <section
          class="ob-control-section"
        >
          <h3>
            Right now
          </h3>

          <div
            class="ob-control-meta"
          >
            <span>Room</span>
            <strong
              data-control-room
            ></strong>

            <span>Mode</span>
            <strong
              data-control-mode
            ></strong>

            <span>Tower</span>
            <strong>Protected</strong>

            <span>Live Auto</span>
            <strong>Locked</strong>
          </div>
        </section>

        <section
          class="ob-control-section"
        >
          <h3>
            Appearance
          </h3>

          <div
            class="ob-theme-choice-grid"
            data-control-themes
          ></div>
        </section>

        <section
          class="ob-control-section"
        >
          <h3>
            OB
          </h3>

          <div
            class="ob-control-actions"
          >
            <a
              class="ob-control-action"
              href="/ob/dashboard"
            >
              Dashboard / My OB
            </a>

            <a
              class="ob-control-action"
              href="/ob/dashboard?ob_arrival=fresh"
            >
              Replay welcome & Soulaana check-in
            </a>

            <button
              type="button"
              class="ob-control-action"
              data-control-feedback
            >
              Send beta feedback
            </button>

            <button
              type="button"
              class="ob-control-action"
              data-ob-action="open-beta-guide"
            >
              Beta Guide
            </button>

            <button
              type="button"
              class="ob-control-action"
              data-ob-action="open-whats-new"
            >
              What Changed
            </button>
          </div>
        </section>

        <section
          class="ob-control-section"
        >
          <h3>
            Tower
          </h3>

          <div
            class="ob-control-actions"
          >
            <button
              type="button"
              class="ob-control-action exit"
              data-control-tower
            >
              Back to Tower
            </button>

            <button
              type="button"
              class="ob-control-action danger"
              data-control-signout
            >
              Sign out of OB
            </button>
          </div>
        </section>
      </section>
    `;


    document
      .body
      .appendChild(
        drawer
      );


    drawer
      .querySelectorAll(
        "[data-control-close]"
      )
      .forEach(
        function (
          node
        ) {
          node.addEventListener(
            "click",
            closeDrawer
          );
        }
      );


    drawer.addEventListener(
      "click",
      function (
        event
      ) {
        const themeButton =
          event.target.closest(
            "[data-theme-id]"
          );

        if (
          themeButton
          && global.OBThemeSwitcher
        ) {
          global
            .OBThemeSwitcher
            .apply(
              themeButton
                .dataset
                .themeId
            );

          refreshDrawer(
            drawer
          );

          return;
        }


        if (
          event.target.closest(
            "[data-control-feedback]"
          )
        ) {
          closeDrawer();

          if (
            global
              .OBGlobalSessionShell
            && global
              .OBGlobalSessionShell
              .openFeedback
          ) {
            global
              .OBGlobalSessionShell
              .openFeedback(
                {
                  component:
                    "compact-control-drawer",
                }
              );
          } else {
            global.dispatchEvent(
              new CustomEvent(
                "ob:open-feedback",
                {
                  detail: {
                    component:
                      "compact-control-drawer",
                  },
                }
              )
            );
          }

          return;
        }


        if (
          event.target.closest(
            "[data-control-tower]"
          )
        ) {
          closeDrawer();

          if (
            global
              .OBGlobalSessionShell
            && global
              .OBGlobalSessionShell
              .backToTower
          ) {
            global
              .OBGlobalSessionShell
              .backToTower();
          } else {
            global
              .location
              .assign(
                "/tower/return/observatory?ob_action=return"
              );
          }

          return;
        }


        if (
          event.target.closest(
            "[data-control-signout]"
          )
        ) {
          closeDrawer();

          if (
            global
              .OBGlobalSessionShell
            && global
              .OBGlobalSessionShell
              .signOut
          ) {
            global
              .OBGlobalSessionShell
              .signOut();
          } else {
            global
              .location
              .assign(
                "/tower/return/observatory?ob_action=signout"
              );
          }
        }
      }
    );


    drawer.addEventListener(
      "keydown",
      function (
        event
      ) {
        if (
          event.key
            === "Escape"
        ) {
          closeDrawer();
        }
      }
    );


    return drawer;
  }


  function refreshDrawer(
    drawer
  ) {
    const room =
      drawer
        .querySelector(
          "[data-control-room]"
        );

    const mode =
      drawer
        .querySelector(
          "[data-control-mode]"
        );

    const themes =
      drawer
        .querySelector(
          "[data-control-themes]"
        );


    if (
      room
    ) {
      room.textContent =
        currentRoom();
    }


    if (
      mode
    ) {
      mode.textContent =
        currentMode();
    }


    if (
      themes
    ) {
      themes.innerHTML =
        themeChoices();
    }
  }


  function buildCompactControl() {
    if (
      document
        .getElementById(
          "obCompactControl"
        )
    ) {
      return;
    }

    const wrap =
      document
        .createElement(
          "div"
        );

    wrap.id =
      "obCompactControl";

    wrap.className =
      "ob-compact-control";

    wrap.innerHTML = `
      <button
        type="button"
        class="ob-compact-menu-button"
        aria-label="Open Observatory controls"
        title="Observatory controls"
      >
        ⋯
      </button>
    `;

    document
      .body
      .appendChild(
        wrap
      );

    wrap
      .querySelector(
        "button"
      )
      .addEventListener(
        "click",
        openDrawer
      );
  }


  function boot() {
    if (
      isBetaProductSurface()
    ) {
      document
        .body
        .classList
        .add(
          "ob-beta-product-surface"
        );
    }


    purgeLegacyProductNoise(
      document
    );

    removeDashboardHeaderButtons();

    buildCompactControl();


    const observer =
      new MutationObserver(
        function (
          mutations
        ) {
          if (
            !isBetaProductSurface()
          ) {
            return;
          }

          mutations
            .forEach(
              function (
                mutation
              ) {
                mutation
                  .addedNodes
                  .forEach(
                    function (
                      node
                    ) {
                      if (
                        node.nodeType
                          !== 1
                      ) {
                        return;
                      }

                      LEGACY_SELECTORS
                        .forEach(
                          function (
                            selector
                          ) {
                            if (
                              node.matches
                              && node.matches(
                                selector
                              )
                            ) {
                              node.remove();
                              return;
                            }

                            if (
                              node.querySelectorAll
                            ) {
                              node
                                .querySelectorAll(
                                  selector
                                )
                                .forEach(
                                  function (
                                    child
                                  ) {
                                    child.remove();
                                  }
                                );
                            }
                          }
                        );
                    }
                  );
              }
            );
        }
      );


    observer.observe(
      document.body,
      {
        childList: true,
        subtree: true,
      }
    );


    global.addEventListener(
      "ob:theme-change",
      function () {
        const drawer =
          document
            .getElementById(
              "obControlDrawer"
            );

        if (
          drawer
        ) {
          refreshDrawer(
            drawer
          );
        }
      }
    );
  }


  if (
    document.readyState
      === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot
    );
  } else {
    boot();
  }


  global.OBBetaSurfaceCleanup =
    Object.freeze(
      {
        purgeLegacyProductNoise,
        openDrawer,
        closeDrawer,
      }
    );

})(window);
