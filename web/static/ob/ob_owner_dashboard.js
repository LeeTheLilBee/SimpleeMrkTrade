// OBUX086–090 — OWNER CAPITAL LANES
// ADHD-friendly rule:
//   one focus
//   one drawer
//   one explicit switch
//   deeper information collapsed
(() => {
  "use strict";

  const VERSION =
    "OBUX086_090_OWNER_CAPITAL_LANES_SURFACE";

  const STORAGE_KEY =
    "ob.owner.capital-lane.v1";

  let currentContract =
    null;


  const esc = (
    value
  ) => (
    String(
      value == null
        ? ""
        : value
    )
      .replaceAll(
        "&",
        "&amp;"
      )
      .replaceAll(
        "<",
        "&lt;"
      )
      .replaceAll(
        ">",
        "&gt;"
      )
      .replaceAll(
        '"',
        "&quot;"
      )
      .replaceAll(
        "'",
        "&#039;"
      )
  );


  const money = (
    value
  ) => {
    if (
      !Number.isFinite(
        Number(
          value
        )
      )
    ) {
      return "Unavailable";
    }

    return new Intl
      .NumberFormat(
        "en-US",
        {
          style:
            "currency",

          currency:
            "USD",

          maximumFractionDigits:
            0
        }
      )
      .format(
        Number(
          value
        )
      );
  };


  const readSelectedLane = () => {
    try {
      return (
        window
          .localStorage
          .getItem(
            STORAGE_KEY
          )
        || ""
      );
    } catch (_) {
      return "";
    }
  };


  const writeSelectedLane = (
    laneId
  ) => {
    try {
      window
        .localStorage
        .setItem(
          STORAGE_KEY,
          laneId
        );
    } catch (_) {}
  };


  const lanes = (
    contract
  ) => (
    Array.isArray(
      contract
      && contract.capital_lanes
    )
      ? contract.capital_lanes
      : []
  );


  const findLane = (
    contract,
    laneId
  ) => (
    lanes(
      contract
    ).find(
      function (
        lane
      ) {
        return (
          lane.lane_id
          === laneId
        );
      }
    )
    || null
  );


  const selectedLane = (
    contract
  ) => {
    const stored =
      readSelectedLane();

    return stored
      ? findLane(
          contract,
          stored
        )
      : null;
  };


  const truthLabel = (
    lane
  ) => {
    if (
      lane.actual_capital_known
    ) {
      return (
        money(
          lane.actual_capital_value
        )
        + " verified"
      );
    }

    if (
      lane.capital_progress_known
    ) {
      return (
        `${Math.round(
          Number(
            lane.capital_progress_percent
          )
        )}% verified progress`
      );
    }

    return (
      "Capital truth unavailable"
    );
  };


  const attentionTone = (
    value
  ) => {
    if (
      value === "high"
    ) {
      return "danger";
    }

    if (
      value === "medium"
    ) {
      return "watch";
    }

    return "calm";
  };


  const sourceChip = (
    verified,
    label
  ) => `
    <span
      class="ob-owner-chip ${
        verified
          ? "verified"
          : "guarded"
      }"
    >
      ${
        verified
          ? "Verified"
          : "Guarded"
      }
      ·
      ${esc(label)}
    </span>
  `;


  const laneNode = (
    lane,
    selected
  ) => `
    <button
      type="button"
      class="ob-capital-lane-node ${
        selected
          ? "selected"
          : ""
      }"
      data-capital-lane-open="${esc(
        lane.lane_id
      )}"
      aria-pressed="${
        selected
          ? "true"
          : "false"
      }"
    >
      <span
        class="ob-capital-lane-star"
        aria-hidden="true"
      ></span>

      <span
        class="ob-capital-lane-node-copy"
      >
        <strong>
          ${esc(
            lane.label
          )}
        </strong>

        <small>
          ${esc(
            lane.risk_profile
          )}
        </small>
      </span>

      <span
        class="ob-capital-lane-node-state"
      >
        ${
          selected
            ? "Current"
            : "Review"
        }
      </span>
    </button>
  `;


  const focusedLaneHtml = (
    lane
  ) => {
    if (
      !lane
    ) {
      return `
        <article
          class="ob-capital-focus empty"
        >
          <div>
            <span
              class="ob-owner-kicker"
            >
              CURRENT CAPITAL LANE
            </span>

            <h2>
              No lane selected
            </h2>

            <p>
              Pick one lane when you need its context.
              Nothing changes until you explicitly enter it.
            </p>
          </div>

          <div
            class="ob-capital-focus-empty-rule"
          >
            <strong>
              One lane at a time.
            </strong>

            <span>
              Clicking a lane below opens details only.
            </span>
          </div>
        </article>
      `;
    }

    return `
      <article
        class="ob-capital-focus"
      >
        <div
          class="ob-capital-focus-main"
        >
          <span
            class="ob-owner-kicker"
          >
            CURRENT CAPITAL LANE
          </span>

          <div
            class="ob-capital-focus-title-row"
          >
            <h2>
              ${esc(
                lane.display_label
              )}
            </h2>

            <span
              class="ob-capital-active-chip"
            >
              Active owner context
            </span>
          </div>

          <p>
            ${esc(
              lane.purpose
            )}
          </p>

          <div
            class="ob-capital-focus-chips"
          >
            <span>
              ${esc(
                lane.risk_profile
              )}
            </span>

            <span>
              ${esc(
                truthLabel(
                  lane
                )
              )}
            </span>

            <span>
              ${
                lane.needs_attention
                  ? "Needs attention"
                  : "No verified alert"
              }
            </span>
          </div>
        </div>

        <div
          class="ob-capital-next"
        >
          <span>
            SOULAANA · NEXT
          </span>

          <strong>
            ${esc(
              lane.next_action
            )}
          </strong>

          <button
            type="button"
            data-capital-lane-open="${esc(
              lane.lane_id
            )}"
          >
            Review this lane
          </button>
        </div>
      </article>
    `;
  };


  const closeLaneDrawer = () => {
    const existing =
      document
        .getElementById(
          "obCapitalLaneDrawerBackdrop"
        );

    if (
      existing
    ) {
      existing.remove();
    }
  };


  const trapFocus = (
    shell
  ) => {
    const focusable =
      Array.from(
        shell.querySelectorAll(
          [
            "button:not([disabled])",
            "[href]",
            "[tabindex]:not([tabindex='-1'])"
          ].join(
            ","
          )
        )
      );

    if (
      !focusable.length
    ) {
      return;
    }

    const first =
      focusable[0];

    const last =
      focusable[
        focusable.length - 1
      ];

    shell.addEventListener(
      "keydown",
      function (
        event
      ) {
        if (
          event.key
          === "Escape"
        ) {
          closeLaneDrawer();
          return;
        }

        if (
          event.key
          !== "Tab"
        ) {
          return;
        }

        if (
          event.shiftKey
          && document.activeElement
            === first
        ) {
          event.preventDefault();
          last.focus();
          return;
        }

        if (
          !event.shiftKey
          && document.activeElement
            === last
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    );

    window.setTimeout(
      function () {
        first.focus();
      },
      0
    );
  };


  const openLaneDrawer = (
    laneId
  ) => {
    closeLaneDrawer();

    const lane =
      findLane(
        currentContract,
        laneId
      );

    if (
      !lane
    ) {
      return;
    }

    const backdrop =
      document.createElement(
        "div"
      );

    backdrop.id =
      "obCapitalLaneDrawerBackdrop";

    backdrop.className =
      "ob-capital-drawer-backdrop";

    const drawer =
      document.createElement(
        "aside"
      );

    drawer.className =
      "ob-capital-drawer";

    drawer.setAttribute(
      "role",
      "dialog"
    );

    drawer.setAttribute(
      "aria-modal",
      "true"
    );

    drawer.setAttribute(
      "aria-labelledby",
      "obCapitalLaneDrawerTitle"
    );

    drawer.innerHTML = `
      <div
        class="ob-capital-drawer-head"
      >
        <div>
          <span
            class="ob-owner-kicker"
          >
            OWNER CAPITAL LANE
          </span>

          <h2
            id="obCapitalLaneDrawerTitle"
          >
            ${esc(
              lane.display_label
            )}
          </h2>
        </div>

        <button
          type="button"
          class="ob-capital-drawer-close"
          id="obCapitalLaneDrawerClose"
          aria-label="Close Capital Lane details"
        >
          ×
        </button>
      </div>

      <div
        class="ob-capital-drawer-summary"
      >
        <p>
          ${esc(
            lane.purpose
          )}
        </p>
      </div>

      <div
        class="ob-capital-drawer-grid"
      >
        <div>
          <span>
            Risk
          </span>

          <strong>
            ${esc(
              lane.risk_profile
            )}
          </strong>
        </div>

        <div>
          <span>
            Capital truth
          </span>

          <strong>
            ${esc(
              truthLabel(
                lane
              )
            )}
          </strong>
        </div>

        <div>
          <span>
            Status
          </span>

          <strong>
            ${esc(
              lane.current_status
            )}
          </strong>
        </div>

        <div>
          <span>
            Goal
          </span>

          <strong>
            ${esc(
              lane.capital_goal
            )}
          </strong>
        </div>
      </div>

      <div
        class="ob-capital-drawer-section"
      >
        <span
          class="ob-owner-kicker"
        >
          ALLOWED CONTEXT
        </span>

        <div
          class="ob-capital-mode-list"
        >
          ${
            lane
              .allowed_modes
              .map(
                function (
                  mode
                ) {
                  return `
                    <span>
                      ${esc(
                        mode
                      )}
                    </span>
                  `;
                }
              )
              .join(
                ""
              )
          }
        </div>
      </div>

      <div
        class="ob-capital-drawer-section"
      >
        <span
          class="ob-owner-kicker"
        >
          SOULAANA · NEXT
        </span>

        <strong
          class="ob-capital-drawer-next"
        >
          ${esc(
            lane.next_action
          )}
        </strong>
      </div>

      <div
        class="ob-capital-context-boundary"
      >
        <strong>
          Entering a lane changes owner context only.
        </strong>

        <span>
          It does not move capital, place an order,
          select a contract, or unlock execution.
        </span>
      </div>

      <div
        class="ob-capital-drawer-actions"
      >
        <button
          type="button"
          class="primary"
          id="obCapitalLaneEnter"
        >
          Enter this lane
        </button>

        <button
          type="button"
          id="obCapitalLaneCancel"
        >
          Close
        </button>
      </div>
    `;

    backdrop.appendChild(
      drawer
    );

    document.body.appendChild(
      backdrop
    );

    /*
      OBUX088:
      Clicking a lane never switches owner context.
      Selection changes ONLY after "Enter this lane".
    */

    document
      .getElementById(
        "obCapitalLaneDrawerClose"
      )
      .addEventListener(
        "click",
        closeLaneDrawer
      );

    document
      .getElementById(
        "obCapitalLaneCancel"
      )
      .addEventListener(
        "click",
        closeLaneDrawer
      );

    document
      .getElementById(
        "obCapitalLaneEnter"
      )
      .addEventListener(
        "click",
        function () {
          writeSelectedLane(
            lane.lane_id
          );

          closeLaneDrawer();

          render(
            currentContract
          );

          window.dispatchEvent(
            new CustomEvent(
              "ob:owner-capital-lane-change",
              {
                detail: {
                  lane_id:
                    lane.lane_id,

                  context_only:
                    true,

                  capital_movement:
                    false,

                  broker_action:
                    false,

                  execution_permission:
                    false
                }
              }
            )
          );
        }
      );

    backdrop.addEventListener(
      "click",
      function (
        event
      ) {
        if (
          event.target
          === backdrop
        ) {
          closeLaneDrawer();
        }
      }
    );

    trapFocus(
      drawer
    );
  };


  const attentionCard = (
    item,
    index
  ) => `
    <article
      class="ob-owner-attention-card ${
        attentionTone(
          item.priority
        )
      }"
    >
      <span
        class="ob-owner-attention-number"
      >
        ${String(
          index + 1
        ).padStart(
          2,
          "0"
        )}
      </span>

      <div>
        <span
          class="ob-owner-kicker"
        >
          ${esc(
            item.source
            || "owner intelligence"
          )}
        </span>

        <h3>
          ${esc(
            item.title
          )}
        </h3>

        <p>
          ${esc(
            item.detail
          )}
        </p>
      </div>
    </article>
  `;


  const render = (
    contract
  ) => {
    currentContract =
      contract
      || {};

    closeLaneDrawer();

    const mount =
      document
        .getElementById(
          "ownerDashboardMount"
        );

    if (
      !mount
    ) {
      return;
    }

    const soulaanaApi =
      window
        .OB_OWNER_DASHBOARD_SOULAANA_V22;

    const briefing =
      (
        soulaanaApi
        && soulaanaApi
          .buildBriefing
      )
        ? soulaanaApi
            .buildBriefing(
              currentContract
            )
        : {
            eyebrow:
              "SOULAANA · OWNER BRIEFING",

            headline:
              "Owner intelligence is loading.",

            what_i_see:
              "I am waiting for guarded owner truth.",

            capital_read:
              "",

            what_needs_you:
              "",

            next_best_move:
              "",

            no_action_needed:
              false
          };

    const laneList =
      lanes(
        currentContract
      );

    const active =
      selectedLane(
        currentContract
      );

    const attention =
      Array.isArray(
        currentContract.owner_attention
      )
        ? currentContract
            .owner_attention
            .slice(
              0,
              3
            )
        : [];

    const trust =
      currentContract.trust
      || {};

    const readiness =
      currentContract.readiness
      || {};

    const beta =
      currentContract.beta
      || {};

    const history =
      (
        currentContract
          .since_you_were_here
        && Array.isArray(
          currentContract
            .since_you_were_here
            .items
        )
      )
        ? currentContract
            .since_you_were_here
            .items
            .slice(
              0,
              5
            )
        : [];

    const patterns =
      (
        currentContract.patterns
        && Array.isArray(
          currentContract
            .patterns
            .items
        )
      )
        ? currentContract
            .patterns
            .items
            .slice(
              0,
              3
            )
        : [];

    mount.innerHTML = `
      <main
        class="ob-owner-dashboard"
        data-owner-dashboard-role="owner-only"
        data-owner-capital-lanes="true"
      >
        <section
          class="ob-owner-hero"
        >
          <div>
            <div
              class="ob-owner-hero-top"
            >
              <span
                class="ob-owner-kicker"
              >
                ${esc(
                  briefing.eyebrow
                )}
              </span>

              <div
                class="ob-owner-chip-row"
              >
                <span
                  class="ob-owner-chip owner"
                >
                  Owner only
                </span>

                <span
                  class="ob-owner-chip locked"
                >
                  Live Auto Locked
                </span>
              </div>
            </div>

            <h1>
              ${esc(
                briefing.headline
              )}
            </h1>

            <p
              class="ob-owner-lead"
            >
              ${esc(
                briefing.what_i_see
              )}
            </p>

            <div
              class="ob-owner-brief-grid"
            >
              <div>
                <span>
                  CAPITAL
                </span>

                <strong>
                  ${esc(
                    briefing.capital_read
                  )}
                </strong>
              </div>

              <div>
                <span>
                  WHAT NEEDS YOU
                </span>

                <strong>
                  ${esc(
                    briefing.what_needs_you
                  )}
                </strong>
              </div>

              <div>
                <span>
                  NEXT
                </span>

                <strong>
                  ${esc(
                    briefing.next_best_move
                  )}
                </strong>
              </div>
            </div>
          </div>
        </section>

        <section
          class="ob-capital-lanes-section"
          aria-labelledby="obCapitalLanesTitle"
        >
          <div
            class="ob-owner-section-head"
          >
            <div>
              <span
                class="ob-owner-kicker"
              >
                CAPITAL LANES
              </span>

              <h2
                id="obCapitalLanesTitle"
              >
                One lane at a time.
              </h2>
            </div>

            <p>
              Your capital has different jobs.
              Review a lane first.
              Enter it only when you want that owner context.
            </p>
          </div>

          ${
            focusedLaneHtml(
              active
            )
          }

          <div
            class="ob-capital-lane-nodes"
            aria-label="Owner Capital Lanes"
          >
            ${
              laneList
                .map(
                  function (
                    lane
                  ) {
                    return laneNode(
                      lane,
                      (
                        active
                        && active.lane_id
                          === lane.lane_id
                      )
                    );
                  }
                )
                .join(
                  ""
                )
            }
          </div>
        </section>

        <section
          class="ob-owner-attention-section"
        >
          <div
            class="ob-owner-section-head compact"
          >
            <div>
              <span
                class="ob-owner-kicker"
              >
                WHAT NEEDS YOU
              </span>

              <h2>
                Only the top three.
              </h2>
            </div>

            <p>
              No giant queue.
              Lower-priority owner intelligence stays collapsed.
            </p>
          </div>

          <div
            class="ob-owner-attention-grid"
          >
            ${
              attention
                .map(
                  attentionCard
                )
                .join(
                  ""
                )
            }
          </div>
        </section>

        <details
          class="ob-owner-more"
        >
          <summary>
            More owner intelligence
          </summary>

          <div
            class="ob-owner-more-grid"
          >
            <article>
              <span
                class="ob-owner-kicker"
              >
                SYSTEM TRUST
              </span>

              <div>
                ${
                  sourceChip(
                    !!trust.verified,
                    trust.label
                    || "engine trust"
                  )
                }
              </div>

              <p>
                ${
                  trust.verified
                    ? (
                        trust.freshness_score
                          != null
                          ? (
                              "Freshness "
                              + esc(
                                  trust.freshness_score
                                )
                            )
                          : "Verified trust state available."
                      )
                    : "Trust truth is guarded."
                }
              </p>
            </article>

            <article>
              <span
                class="ob-owner-kicker"
              >
                MANUAL LIVE READINESS
              </span>

              <div>
                ${
                  sourceChip(
                    !!readiness.verified,
                    readiness.label
                    || "readiness"
                  )
                }
              </div>

              <p>
                ${
                  readiness.verified
                    && readiness.score
                      != null
                    ? (
                        esc(
                          readiness.score
                        )
                        + "% evidence score"
                      )
                    : "Readiness remains guarded."
                }
              </p>
            </article>

            <article>
              <span
                class="ob-owner-kicker"
              >
                PRIVATE BETA
              </span>

              <div>
                ${
                  sourceChip(
                    !!beta.verified,
                    beta.label
                    || "private beta"
                  )
                }
              </div>

              <p>
                Private stays private.
              </p>
            </article>
          </div>

          <div
            class="ob-owner-more-two"
          >
            <article>
              <span
                class="ob-owner-kicker"
              >
                SINCE YOU WERE HERE
              </span>

              ${
                history
                  .map(
                    function (
                      item
                    ) {
                      return `
                        <div
                          class="ob-owner-mini-item"
                        >
                          <strong>
                            ${esc(
                              item.title
                            )}
                          </strong>

                          <span>
                            ${esc(
                              item.detail
                            )}
                          </span>
                        </div>
                      `;
                    }
                  )
                  .join(
                    ""
                  )
              }
            </article>

            <article>
              <span
                class="ob-owner-kicker"
              >
                WHAT I'M LEARNING
              </span>

              ${
                patterns
                  .map(
                    function (
                      item
                    ) {
                      return `
                        <div
                          class="ob-owner-mini-item"
                        >
                          <strong>
                            ${esc(
                              item.title
                            )}
                          </strong>

                          <span>
                            ${esc(
                              item.detail
                            )}
                          </span>
                        </div>
                      `;
                    }
                  )
                  .join(
                    ""
                  )
              }
            </article>
          </div>
        </details>

        <details
          class="ob-owner-evidence"
        >
          <summary>
            Show me why
          </summary>

          <div
            class="ob-owner-evidence-body"
          >
            <p>
              ${esc(
                briefing.evidence_rule
                || (
                  "Short answer first. "
                  + "Deeper evidence stays here."
                )
              )}
            </p>

            <pre>${
              esc(
                JSON.stringify(
                  {
                    source_state:
                      currentContract
                        .source_state,

                    interpretation_state:
                      currentContract
                        .interpretation_state,

                    boundaries:
                      currentContract
                        .boundaries
                  },
                  null,
                  2
                )
              )
            }</pre>
          </div>
        </details>
      </main>
    `;

    document
      .querySelectorAll(
        "[data-capital-lane-open]"
      )
      .forEach(
        function (
          button
        ) {
          button.addEventListener(
            "click",
            function () {
              /*
                DETAIL ONLY.
                No automatic context switch.
              */
              openLaneDrawer(
                this.getAttribute(
                  "data-capital-lane-open"
                )
              );
            }
          );
        }
      );

    document.body.setAttribute(
      "data-ob-owner-dashboard-surface",
      "capital-lanes"
    );

    document.body.setAttribute(
      "data-ob-owner-dashboard-owner-only",
      "true"
    );

    document.body.setAttribute(
      "data-ob-owner-capital-lanes",
      "true"
    );

    document.body.setAttribute(
      "data-ob-owner-dashboard-live-auto-locked",
      "true"
    );

    if (
      active
    ) {
      document.body.setAttribute(
        "data-ob-owner-capital-lane",
        active.lane_id
      );
    } else {
      document.body.removeAttribute(
        "data-ob-owner-capital-lane"
      );
    }
  };


  const boot = async () => {
    const contractApi =
      window
        .OB_OWNER_DASHBOARD_CONTRACT_V21;

    if (
      !contractApi
    ) {
      throw new Error(
        "Owner Capital Lanes contract did not load."
      );
    }

    render(
      contractApi
        .getContract()
    );

    try {
      const hydrated =
        await contractApi.hydrate();

      render(
        hydrated
      );

    } catch (_) {
      /*
        Fail closed.
        Guarded local owner policy remains visible.
      */
      render(
        contractApi
          .getContract()
      );
    }
  };


  document.addEventListener(
    "DOMContentLoaded",
    boot
  );


  window
    .OB_OWNER_DASHBOARD_SURFACE_V23_25 =
      Object.freeze({
        version:
          VERSION,

        storage_key:
          STORAGE_KEY,

        render,

        boot,

        openLaneDrawer,

        closeLaneDrawer,

        owner_only:
          true,

        capital_lanes:
          true,

        lane_selection_context_only:
          true,

        broker_action_performed:
          false,

        capital_action_performed:
          false,

        automatic_contract_selection:
          false,

        automatic_execution:
          false,

        live_auto_locked:
          true
      });

})();
