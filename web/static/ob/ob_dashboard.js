
// OBUX091–095 — CALM USER DASHBOARD
//
// ADHD RULE:
//   one dominant focus
//   max three market-glance cards
//   no default list wall
//   secondary information collapsed
//
(function (global) {
  "use strict";

  const VERSION =
    "OBUX091_095_USER_DASHBOARD";


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


  function renderGlance(
    items
  ) {
    const mount =
      document.getElementById(
        "obUserMarketGlance"
      );

    if (
      !mount
    ) {
      return;
    }

    const safe =
      Array.isArray(items)
        ? items.slice(
            0,
            3
          )
        : [];

    if (
      !safe.length
    ) {
      mount.innerHTML = `
        <article
          class="ob-user-glance-card empty"
        >
          <span>
            QUIET SKY
          </span>

          <strong>
            No verified symbol needs the front page.
          </strong>

          <p>
            Market Map remains available
            whenever you want to explore.
          </p>

          <a
            href="/ob/market-map"
          >
            Open Market Map →
          </a>
        </article>
      `;

      return;
    }

    mount.innerHTML =
      safe
        .map(
          function (
            item,
            index
          ) {
            return `
              <article
                class="ob-user-glance-card"
              >
                <span>
                  STUDY ${String(index + 1).padStart(2, "0")}
                </span>

                <strong>
                  ${esc(item.symbol)}
                </strong>

                <p>
                  ${esc(item.detail)}
                </p>

                <small>
                  ${esc(item.source)}
                </small>

                <a
                  href="${esc(item.href)}"
                >
                  Study symbol →
                </a>
              </article>
            `;
          }
        )
        .join(
          ""
        );
  }


  function renderMore(
    items
  ) {
    const mount =
      document.getElementById(
        "obUserMoreContent"
      );

    if (
      !mount
    ) {
      return;
    }

    const safe =
      Array.isArray(items)
        ? items.slice(
            0,
            3
          )
        : [];

    mount.innerHTML =
      safe
        .map(
          function (
            item
          ) {
            return `
              <article
                class="ob-user-more-card"
              >
                <span>
                  ${esc(
                    String(
                      item.kind
                      || "context"
                    )
                      .replaceAll(
                        "_",
                        " "
                      )
                      .toUpperCase()
                  )}
                </span>

                <strong>
                  ${esc(item.label)}
                </strong>

                <p>
                  ${esc(item.detail)}
                </p>

                ${
                  item.href
                    ? `
                        <a
                          href="${esc(item.href)}"
                        >
                          Open →
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


  function render() {
    const api =
      global
        .OB_USER_DASHBOARD_PROJECTION;

    if (
      !api
      || typeof api.project
        !== "function"
    ) {
      return;
    }

    const projection =
      api.project();

    const title =
      document.getElementById(
        "obUserBriefingTitle"
      );

    const summary =
      document.getElementById(
        "obUserBriefingSummary"
      );

    if (
      title
    ) {
      title.textContent =
        projection
          .briefing
          .title;
    }

    if (
      summary
    ) {
      summary.textContent =
        projection
          .briefing
          .summary;
    }

    renderGlance(
      projection.market_glance
    );

    renderMore(
      projection.more
    );

    document.body.setAttribute(
      "data-ob-user-mode",
      projection.mode
    );

    document.body.setAttribute(
      "data-ob-market-projection-state",
      projection
        .source_state
        .projection_status
    );
  }


  /*
    The guide points toward self-directed exploration.
    No account snapshot. No owner candidate screen.
  */
  function showDashboardGuide() {
    if (
      !global.OBSessionState
    ) {
      return;
    }

    let enabled = false;

    try {
      const current =
        global
          .OBSessionState
          .snapshot();

      enabled =
        Boolean(
          current
          && current.ephemeral
          && current.ephemeral.guidance
          && current.ephemeral.guidance.enabled
        );

    } catch (_) {
      enabled = false;
    }

    if (
      !enabled
    ) {
      return;
    }

    if (
      document.getElementById(
        "obGuidePrompt"
      )
    ) {
      return;
    }

    const prompt =
      document.createElement(
        "aside"
      );

    prompt.id =
      "obGuidePrompt";

    prompt.className =
      "ob-guide-prompt";

    prompt.innerHTML = `
      <span
        class="ob-kicker"
      >
        SOULAANA · GUIDE
      </span>

      <strong>
        Start with the market,
        not a wall of information.
      </strong>

      <p>
        Read the briefing.
        Scan the three-item Market Glance.
        Then choose what you want to study.
      </p>

      <div>
        <button
          type="button"
          data-guide-stop
        >
          Stop guide
        </button>

        <a
          href="/ob/market-map"
        >
          Take me to Market Map →
        </a>
      </div>
    `;

    document.body.appendChild(
      prompt
    );

    const stop =
      prompt.querySelector(
        "[data-guide-stop]"
      );

    if (
      stop
    ) {
      stop.addEventListener(
        "click",
        function () {
          try {
            global
              .OBSessionState
              .setGuidance(
                false,
                "complete"
              );
          } catch (_) {}

          prompt.remove();
        }
      );
    }
  }


  function boot() {
    render();

    window.setTimeout(
      showDashboardGuide,
      60
    );
  }


  window.addEventListener(
    "obEngineFeedAdapterUpdated",
    render
  );

  window.addEventListener(
    "obSessionStateUpdated",
    render
  );


  if (
    document.readyState
    === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot,
      {
        once:
          true
      }
    );
  } else {
    boot();
  }


  global.OB_USER_DASHBOARD_V91 =
    Object.freeze({
      version:
        VERSION,

      render
    });

})(window);
