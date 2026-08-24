// OBSERVATORY_OBUX056_060_CANONICAL_USER_DASHBOARD

(function (global) {
  "use strict";

  let currentProjection = null;


  function esc(
    value
  ) {
    return String(
      value == null
        ? ""
        : value
    )
      .replace(
        /&/g,
        "&amp;"
      )
      .replace(
        /</g,
        "&lt;"
      )
      .replace(
        />/g,
        "&gt;"
      )
      .replace(
        /"/g,
        "&quot;"
      );
  }


  function stateClass(
    value
  ) {
    return (
      "state-"
      + String(
          value || "unknown"
        )
          .toLowerCase()
          .replace(
            /[^a-z0-9]+/g,
            "-"
          )
    );
  }


  function emptyCard(
    title,
    detail
  ) {
    return `
      <div
        class="ob-info-card empty"
      >
        <div>
          <strong>
            ${esc(title)}
          </strong>

          <p>
            ${esc(detail)}
          </p>
        </div>
      </div>
    `;
  }


  function renderSnapshot(
    cards
  ) {
    const mount =
      document.getElementById(
        "obAccountSnapshot"
      );

    if (
      !mount
    ) {
      return;
    }

    mount.innerHTML =
      cards
        .map(
          function (
            card
          ) {
            return `
              <article
                class="ob-snapshot-card ${stateClass(card.state)}"
              >
                <span>
                  ${esc(card.label)}
                </span>

                <strong>
                  ${esc(card.value)}
                </strong>

                <p>
                  ${esc(card.detail)}
                </p>

                <small>
                  ${esc(card.source)}
                </small>
              </article>
            `;
          }
        )
        .join(
          ""
        );
  }


  function renderList(
    mountId,
    items
  ) {
    const mount =
      document.getElementById(
        mountId
      );

    if (
      !mount
    ) {
      return;
    }

    if (
      !items
      || !items.length
    ) {
      mount.innerHTML =
        emptyCard(
          "Nothing source-backed here yet",
          "Unavailable stays unavailable."
        );

      return;
    }

    mount.innerHTML =
      items
        .map(
          function (
            item
          ) {
            return `
              <article
                class="ob-info-card"
              >
                <div>
                  <strong>
                    ${esc(item.title)}
                  </strong>

                  <p>
                    ${esc(item.detail)}
                  </p>

                  <small>
                    ${esc(
                      item.source
                      || "source unavailable"
                    )}
                  </small>
                </div>

                ${
                  item.href
                    ? `
                        <a
                          href="${esc(item.href)}"
                          aria-label="Open ${esc(item.title)}"
                        >
                          →
                        </a>
                      `
                    : ""
                }
              </article>
            `;
          }
        )
        .join(
          ""
        );
  }


  function renderMarket(
    items
  ) {
    const mount =
      document.getElementById(
        "obMarketNow"
      );

    if (
      !mount
    ) {
      return;
    }

    if (
      !items
      || !items.length
    ) {
      mount.innerHTML =
        emptyCard(
          "Market intelligence unavailable",
          "Open Market Map. Dashboard will not invent symbols, prices, option contracts, or confidence."
        );

      return;
    }

    mount.innerHTML =
      items
        .map(
          function (
            item
          ) {
            return `
              <a
                class="ob-market-card"
                href="${esc(item.href)}"
              >
                <div>
                  <strong>
                    ${esc(item.symbol)}
                  </strong>

                  <span>
                    ${esc(item.thesis)}
                  </span>
                </div>

                <div
                  class="ob-market-meta"
                >
                  ${
                    item.options
                      ? `
                          <small>
                            ${esc(item.options)}
                          </small>
                        `
                      : ""
                  }

                  ${
                    item.liquidity
                      ? `
                          <small>
                            Liquidity · ${esc(item.liquidity)}
                          </small>
                        `
                      : ""
                  }

                  <small>
                    ${esc(item.source)}
                  </small>
                </div>

                <span
                  class="ob-market-arrow"
                >
                  Study →
                </span>
              </a>
            `;
          }
        )
        .join(
          ""
        );
  }


  function renderMyOb(
    projection,
    section
  ) {
    const drawer =
      document.getElementById(
        "obMyObDrawer"
      );

    const mount =
      document.getElementById(
        "obMyObContent"
      );

    if (
      !drawer
      || !mount
    ) {
      return;
    }

    const permissions =
      projection.permissions
      && projection.permissions.length
        ? projection.permissions
            .map(
              function (
                item
              ) {
                return `
                  <li>
                    <strong>
                      ${esc(item.name)}
                    </strong>

                    <span>
                      ${esc(item.state)}
                    </span>
                  </li>
                `;
              }
            )
            .join(
              ""
            )
        : `
            <li>
              <strong>
                Mode permissions
              </strong>

              <span>
                Unavailable
              </span>
            </li>
          `;

    const recentSessions =
      projection.recentSessions
      && projection.recentSessions.length
        ? projection.recentSessions
            .slice(
              0,
              5
            )
            .map(
              function (
                item
              ) {
                return `
                  <li>
                    <strong>
                      ${esc(
                        item.lastRoom
                        || "OB session"
                      )}
                    </strong>

                    <span>
                      ${esc(
                        item.mode
                        || "mode unavailable"
                      )}
                      ·
                      ${esc(
                        item.endedAt
                        || ""
                      )}
                    </span>
                  </li>
                `;
              }
            )
            .join(
              ""
            )
        : `
            <li>
              <strong>
                No closed sessions yet
              </strong>

              <span>
                Session history appears
                when an OB session closes.
              </span>
            </li>
          `;

    const feedback =
      projection.feedback
      && projection.feedback.length
        ? projection.feedback
            .slice(
              0,
              5
            )
            .map(
              function (
                item
              ) {
                return `
                  <li>
                    <strong>
                      ${esc(item.category)}
                    </strong>

                    <span>
                      ${
                        item.delivery
                          === "local_queue"
                            ? "Saved locally for beta handoff"
                            : esc(item.delivery)
                      }
                    </span>
                  </li>
                `;
              }
            )
            .join(
              ""
            )
        : `
            <li>
              <strong>
                No saved beta feedback
              </strong>

              <span>
                Use Send feedback anywhere in OB.
              </span>
            </li>
          `;

    mount.innerHTML = `
      <section
        data-my-ob-panel="access"
      >
        <h3>
          Profile & access
        </h3>

        <p>
          ${
            projection.profile
              ? esc(
                  projection
                    .profile
                    .subtitle
                  || projection
                    .profile
                    .title
                  || "OB user"
                )
              : "Canonical profile detail unavailable."
          }
        </p>

        <ul
          class="ob-detail-list"
        >
          ${permissions}
        </ul>
      </section>

      <section
        data-my-ob-panel="notifications"
      >
        <h3>
          Notification readiness
        </h3>

        <ul
          class="ob-detail-list"
        >
          <li>
            <strong>Browser</strong>
            <span>${esc(projection.notification.browser)}</span>
          </li>

          <li>
            <strong>In-app</strong>
            <span>${esc(projection.notification.inApp)}</span>
          </li>

          <li>
            <strong>Email</strong>
            <span>${esc(projection.notification.email)}</span>
          </li>

          <li>
            <strong>Last delivery</strong>
            <span>${esc(projection.notification.lastDelivery || "Unavailable")}</span>
          </li>
        </ul>

        <button
          type="button"
          class="ob-soft-button"
          data-ob-action="request-browser-alerts"
        >
          Check browser permission
        </button>
      </section>

      <section
        data-my-ob-panel="sessions"
      >
        <h3>
          Recent sessions
        </h3>

        <ul
          class="ob-detail-list"
        >
          ${recentSessions}
        </ul>
      </section>

      <section
        data-my-ob-panel="feedback"
      >
        <h3>
          Beta feedback
        </h3>

        <ul
          class="ob-detail-list"
        >
          ${feedback}
        </ul>

        <button
          type="button"
          class="ob-soft-button"
          data-ob-action="open-feedback"
        >
          Send feedback
        </button>
      </section>

      <section
        data-my-ob-panel="guide"
      >
        <h3>
          Beta Guide
        </h3>

        <p>
          Reopen the SOP
          or see what changed
          without forcing it every login.
        </p>

        <div
          class="ob-inline-actions"
        >
          <button
            type="button"
            class="ob-soft-button"
            data-ob-action="open-beta-guide"
          >
            Open SOP
          </button>

          <button
            type="button"
            class="ob-soft-button"
            data-ob-action="open-whats-new"
          >
            What changed
          </button>
        </div>
      </section>

      <section
        data-my-ob-panel="privacy"
      >
        <h3>
          Privacy & session
        </h3>

        <p>
          Check-in answers remain session-only
          unless you explicitly choose
          to use them in your private session review.
        </p>

        <p>
          Soulaana may simplify presentation,
          but your check-in never changes
          prices,
          rankings,
          source truth,
          or trade decisions.
        </p>
      </section>
    `;

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

    if (
      section
    ) {
      const target =
        [
          ...mount.querySelectorAll(
            "[data-my-ob-panel]"
          ),
        ].find(
          function (
            item
          ) {
            return (
              item.dataset
                .myObPanel
              === section
            );
          }
        );

      if (
        target
      ) {
        target.scrollIntoView(
          {
            block:
              "start",
          }
        );
      }
    }
  }


  function closeMyOb() {
    const drawer =
      document.getElementById(
        "obMyObDrawer"
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


  function applyCheckInPresentation() {
    if (
      !global.OBSessionState
    ) {
      return;
    }

    const current =
      global
        .OBSessionState
        .snapshot();

    const checkIn =
      current
        .ephemeral
        .checkIn;

    if (
      !checkIn
      || checkIn.status
        !== "completed"
      || !checkIn.response
    ) {
      return;
    }

    const values =
      checkIn.response;

    const lowEnergy =
      values.energy
        === "Low";

    const simplify =
      values.focus
        === "Scattered"
      || values.pace
        === "Rushed";

    document
      .body
      .classList
      .toggle(
        "ob-session-low-energy",
        lowEnergy
      );

    document
      .body
      .classList
      .toggle(
        "ob-session-simplify",
        simplify
      );
  }


  function showDashboardGuide() {
    if (
      !global.OBSessionState
    ) {
      return;
    }

    const current =
      global
        .OBSessionState
        .snapshot();

    if (
      !current
        .ephemeral
        .guidance
        .enabled
    ) {
      return;
    }

    let prompt =
      document.getElementById(
        "obGuidePrompt"
      );

    if (
      !prompt
    ) {
      prompt =
        document.createElement(
          "aside"
        );

      prompt.id =
        "obGuidePrompt";

      prompt.className =
        "ob-guide-prompt";

      document.body.appendChild(
        prompt
      );
    }

    prompt.innerHTML = `
      <span
        class="ob-kicker"
      >
        SOULAANA · GUIDE
      </span>

      <strong>
        Start here:
        this Dashboard is your OB account home.
      </strong>

      <p>
        Scan your account snapshot
        and Right Now.
        Then move into Market Map
        when you’re ready
        to study the market.
      </p>

      <div>
        <button
          type="button"
          class="ob-soft-button"
          data-guide-stop
        >
          Stop guide
        </button>

        <a
          class="ob-primary-button"
          href="/ob/market-map"
        >
          Take me to Market Map →
        </a>
      </div>
    `;

    prompt
      .querySelector(
        "[data-guide-stop]"
      )
      .addEventListener(
        "click",
        function () {
          global
            .OBSessionState
            .setGuidance(
              false,
              "complete"
            );

          prompt.remove();
        }
      );
  }


  async function requestBrowserAlerts() {
    if (
      !(
        "Notification"
        in global
      )
    ) {
      global
        .OBSessionState
        ?.updateNotificationReadiness(
          {
            browser:
              "unsupported",

            source:
              "browser",
          }
        );

      return;
    }

    let permission =
      global
        .Notification
        .permission;

    if (
      permission
        === "default"
    ) {
      permission =
        await global
          .Notification
          .requestPermission();
    }

    global
      .OBSessionState
      ?.updateNotificationReadiness(
        {
          browser:
            permission,

          source:
            "browser",
        }
      );

    await render();
  }


  async function render() {
    if (
      !global.OBDashboardProjection
    ) {
      return;
    }

    currentProjection =
      await global
        .OBDashboardProjection
        .project();

    renderSnapshot(
      currentProjection
        .snapshotCards
    );

    renderList(
      "obSinceYouWereHere",
      currentProjection
        .since
    );

    renderList(
      "obUserActivity",
      currentProjection
        .activity
    );

    renderMarket(
      currentProjection
        .market
    );

    const summary =
      document.getElementById(
        "obSoulaanaSummary"
      );

    if (
      summary
    ) {
      summary.textContent =
        currentProjection
          .summary;
    }

    const source =
      document.getElementById(
        "obAccountSource"
      );

    if (
      source
    ) {
      source.textContent =
        currentProjection.profile
          ? "Account source connected"
          : "Account source guarded";
    }

    const trackedItem =
      currentProjection
        .activity
        .find(
          function (
            item
          ) {
            return (
              item.kind
              === "positions"
            );
          }
        );

    global
      .OBSessionState
      ?.setTrackedPositions(
        trackedItem
          ? trackedItem.count
          : 0,

        trackedItem
          ? trackedItem.source
          : "no source-backed tracked positions"
      );

    applyCheckInPresentation();
  }


  document.addEventListener(
    "click",
    async function (
      event
    ) {
      const actionNode =
        event.target.closest(
          "[data-ob-action]"
        );

      if (
        !actionNode
      ) {
        return;
      }

      const action =
        actionNode
          .dataset
          .obAction;

      if (
        action
          === "open-my-ob"
      ) {
        event.preventDefault();

        if (
          !currentProjection
        ) {
          currentProjection =
            await global
              .OBDashboardProjection
              .project();
        }

        renderMyOb(
          currentProjection,
          actionNode
            .dataset
            .myObSection
        );
      }

      if (
        action
          === "close-my-ob"
      ) {
        event.preventDefault();
        closeMyOb();
      }

      if (
        action
          === "open-beta-guide"
      ) {
        event.preventDefault();

        global
          .OBSessionArrival
          ?.openSop();
      }

      if (
        action
          === "open-whats-new"
      ) {
        event.preventDefault();

        global
          .OBSessionArrival
          ?.openWhatsNew();
      }

      if (
        action
          === "open-feedback"
      ) {
        event.preventDefault();

        global.dispatchEvent(
          new CustomEvent(
            "ob:open-feedback",
            {
              detail: {
                component:
                  "dashboard",
              },
            }
          )
        );
      }

      if (
        action
          === "request-browser-alerts"
      ) {
        event.preventDefault();

        await requestBrowserAlerts();
      }

      if (
        action
          === "explain-dashboard"
      ) {
        event.preventDefault();

        if (
          !currentProjection
        ) {
          currentProjection =
            await global
              .OBDashboardProjection
              .project();
        }

        renderMyOb(
          currentProjection,
          "privacy"
        );
      }
    }
  );


  global.addEventListener(
    "ob:arrival-complete",
    function () {
      /*
        Only after arrival/resume decision
        do we make Dashboard
        the user's new safe route.
      */
      global
        .OBSessionState
        ?.recordRoute(
          global.location.pathname,
          "Dashboard"
        );

      applyCheckInPresentation();

      showDashboardGuide();
    }
  );


  global.addEventListener(
    "ob:guide-start",
    showDashboardGuide
  );


  document.addEventListener(
    "DOMContentLoaded",
    function () {
      render();

      /*
        Source adapters can finish after first paint.
        Re-project without inventing anything.
      */
      global.setTimeout(
        render,
        1000
      );

      global.setTimeout(
        render,
        2500
      );
    }
  );


  global.OBUserDashboard =
    Object.freeze(
      {
        render,
      }
    );

})(window);
