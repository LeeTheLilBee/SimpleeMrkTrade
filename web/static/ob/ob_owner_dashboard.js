
// OBUX091–095 — IMMACULATE OWNER INTELLIGENCE COCKPIT
//
// ATTENTION ARCHITECTURE:
//   1. Soulaana
//   2. Today's Edge: NOW / WATCH / NOT YET
//   3. three compact owner context tiles
//   4. everything else collapsed
//   5. Capital Lanes are secondary owner context
//
// NO TABLE WALL.
// NO GIANT LIST.
// ONE DRAWER AT A TIME.
//
(() => {
  "use strict";

  const VERSION =
    "OBUX091_095_OWNER_INTELLIGENCE_COCKPIT";

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


  const fmtNumber = (
    value,
    digits = 2
  ) => {
    const number =
      Number(
        value
      );

    return Number.isFinite(number)
      ? number.toFixed(
          digits
        )
      : "—";
  };


  const fmtWhole = (
    value
  ) => {
    const number =
      Number(
        value
      );

    return Number.isFinite(number)
      ? Math.round(
          number
        ).toLocaleString()
      : "—";
  };


  const readSelectedLane = () => {
    try {
      return (
        window.localStorage
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
      window.localStorage
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
    laneId
  ) => (
    lanes(
      currentContract
    ).find(
      lane =>
        lane.lane_id
        === laneId
    )
    || null
  );


  const selectedLane = () => {
    const stored =
      readSelectedLane();

    return stored
      ? findLane(
          stored
        )
      : null;
  };


  const sourceBadge = (
    item
  ) => (
    item
    && item.verified
      ? `
          <span
            class="ob-research-source verified"
          >
            VERIFIED
          </span>
        `
      : `
          <span
            class="ob-research-source guarded"
          >
            GUARDED
          </span>
        `
  );


  const closeDrawer = () => {
    const current =
      document.getElementById(
        "obOwnerDrawerBackdrop"
      );

    if (
      current
    ) {
      current.remove();
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
          event.key === "Escape"
        ) {
          closeDrawer();
          return;
        }

        if (
          event.key !== "Tab"
        ) {
          return;
        }

        if (
          event.shiftKey
          && document.activeElement === first
        ) {
          event.preventDefault();
          last.focus();
          return;
        }

        if (
          !event.shiftKey
          && document.activeElement === last
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    );

    window.setTimeout(
      () => first.focus(),
      0
    );
  };


  const optionCard = (
    option
  ) => `
    <article
      class="ob-option-research-card"
    >
      <div
        class="ob-option-research-head"
      >
        <strong>
          ${esc(option.option_type)}
          ${option.strike === null ? "" : esc(option.strike)}
        </strong>

        <span>
          ${esc(option.expiration)}
        </span>
      </div>

      <div
        class="ob-option-research-metrics"
      >
        <span>
          Bid
          <strong>
            ${fmtNumber(option.bid)}
          </strong>
        </span>

        <span>
          Ask
          <strong>
            ${fmtNumber(option.ask)}
          </strong>
        </span>

        <span>
          OI
          <strong>
            ${fmtWhole(option.open_interest)}
          </strong>
        </span>

        <span>
          Vol
          <strong>
            ${fmtWhole(option.volume)}
          </strong>
        </span>
      </div>

      <details>
        <summary>
          Greeks & volatility
        </summary>

        <div
          class="ob-option-greeks"
        >
          <span>
            Δ ${fmtNumber(option.delta, 3)}
          </span>

          <span>
            Γ ${fmtNumber(option.gamma, 3)}
          </span>

          <span>
            Θ ${fmtNumber(option.theta, 3)}
          </span>

          <span>
            Vega ${fmtNumber(option.vega, 3)}
          </span>

          <span>
            IV ${fmtNumber(option.implied_volatility, 3)}
          </span>
        </div>
      </details>

      <small>
        Research candidate only · owner chooses
      </small>
    </article>
  `;


  const openCandidateDrawer = (
    candidate
  ) => {
    closeDrawer();

    if (
      !candidate
    ) {
      return;
    }

    const backdrop =
      document.createElement(
        "div"
      );

    backdrop.id =
      "obOwnerDrawerBackdrop";

    backdrop.className =
      "ob-owner-drawer-backdrop";

    const drawer =
      document.createElement(
        "aside"
      );

    drawer.className =
      "ob-owner-drawer";

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
      "obOwnerCandidateTitle"
    );

    drawer.innerHTML = `
      <header
        class="ob-owner-drawer-head"
      >
        <div>
          <span
            class="ob-owner-kicker"
          >
            OWNER RESEARCH · ${esc(candidate.bucket.replaceAll("_", " ").toUpperCase())}
          </span>

          <h2
            id="obOwnerCandidateTitle"
          >
            ${esc(candidate.symbol)}
          </h2>
        </div>

        <button
          type="button"
          data-owner-drawer-close
          aria-label="Close analysis"
        >
          ×
        </button>
      </header>

      <div
        class="ob-owner-drawer-body"
      >
        <div
          class="ob-candidate-summary"
        >
          ${sourceBadge(candidate)}

          <span>
            ${esc(candidate.direction)}
          </span>

          ${
            candidate.score === null
              ? ""
              : `
                  <span>
                    Source score · ${esc(candidate.score)}
                  </span>
                `
          }
        </div>

        <section>
          <span
            class="ob-owner-kicker"
          >
            WHY IT SURFACED
          </span>

          <h3>
            ${esc(candidate.setup)}
          </h3>

          <p>
            ${esc(candidate.thesis)}
          </p>
        </section>

        <div
          class="ob-candidate-facts"
        >
          <article>
            <span>
              Catalyst
            </span>

            <strong>
              ${esc(candidate.catalyst)}
            </strong>
          </article>

          <article>
            <span>
              Entry evidence
            </span>

            <strong>
              ${esc(candidate.entry_zone)}
            </strong>
          </article>

          <article>
            <span>
              Invalidation
            </span>

            <strong>
              ${esc(candidate.invalidation)}
            </strong>
          </article>

          <article>
            <span>
              Hold window
            </span>

            <strong>
              ${esc(candidate.hold_window)}
            </strong>
          </article>
        </div>

        <section
          class="ob-candidate-risk"
        >
          <span
            class="ob-owner-kicker"
          >
            RISK
          </span>

          <p>
            ${esc(candidate.risk)}
          </p>
        </section>

        <section
          class="ob-option-research"
        >
          <div
            class="ob-option-research-title"
          >
            <div>
              <span
                class="ob-owner-kicker"
              >
                OPTIONS FIRST · RESEARCH ONLY
              </span>

              <h3>
                Verified contract research
              </h3>
            </div>

            <span>
              ${candidate.option_contract_count} available
            </span>
          </div>

          <div
            class="ob-option-research-grid"
          >
            ${
              candidate.option_contracts.length
                ? candidate.option_contracts
                    .map(
                      optionCard
                    )
                    .join("")
                : `
                    <div
                      class="ob-empty-research"
                    >
                      No source-backed option contract
                      is available for this symbol.
                    </div>
                  `
            }
          </div>
        </section>

        <div
          class="ob-owner-safety-note"
        >
          <strong>
            You choose the security and contract.
          </strong>

          <span>
            This analysis does not submit an order,
            move capital,
            select a contract automatically,
            or unlock execution.
          </span>
        </div>

        <details
          class="ob-owner-evidence"
        >
          <summary>
            Show me why
          </summary>

          <div>
            <span>
              Source · ${esc(candidate.source)}
            </span>

            <span>
              Freshness · ${esc(candidate.freshness)}
            </span>

            <span>
              Source order · ${esc(candidate.source_order)}
            </span>

            <span>
              Selection authority · OWNER
            </span>
          </div>
        </details>
      </div>
    `;

    backdrop.appendChild(
      drawer
    );

    document.body.appendChild(
      backdrop
    );

    drawer
      .querySelector(
        "[data-owner-drawer-close]"
      )
      .addEventListener(
        "click",
        closeDrawer
      );

    backdrop.addEventListener(
      "click",
      function (
        event
      ) {
        if (
          event.target === backdrop
        ) {
          closeDrawer();
        }
      }
    );

    trapFocus(
      drawer
    );
  };


  const truthLabel = (
    lane
  ) => {
    if (
      lane.actual_capital_known
    ) {
      return (
        "$"
        + Number(
            lane.actual_capital_value
          )
          .toLocaleString()
      );
    }

    if (
      lane.capital_progress_known
    ) {
      return (
        Math.round(
          Number(
            lane.capital_progress_percent
          )
        )
        + "% verified"
      );
    }

    return "Capital truth unavailable";
  };


  const openLaneDrawer = (
    laneId
  ) => {
    closeDrawer();

    const lane =
      findLane(
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
      "obOwnerDrawerBackdrop";

    backdrop.className =
      "ob-owner-drawer-backdrop";

    const drawer =
      document.createElement(
        "aside"
      );

    drawer.className =
      "ob-owner-drawer ob-capital-drawer";

    drawer.setAttribute(
      "role",
      "dialog"
    );

    drawer.setAttribute(
      "aria-modal",
      "true"
    );

    drawer.innerHTML = `
      <header
        class="ob-owner-drawer-head"
      >
        <div>
          <span
            class="ob-owner-kicker"
          >
            OWNER CAPITAL LANE
          </span>

          <h2>
            ${esc(lane.display_label)}
          </h2>
        </div>

        <button
          type="button"
          data-owner-drawer-close
          aria-label="Close Capital Lane"
        >
          ×
        </button>
      </header>

      <div
        class="ob-owner-drawer-body"
      >
        <p>
          ${esc(lane.purpose)}
        </p>

        <div
          class="ob-candidate-facts"
        >
          <article>
            <span>
              Risk
            </span>

            <strong>
              ${esc(lane.risk_profile)}
            </strong>
          </article>

          <article>
            <span>
              Capital
            </span>

            <strong>
              ${esc(truthLabel(lane))}
            </strong>
          </article>

          <article>
            <span>
              Status
            </span>

            <strong>
              ${esc(lane.current_status)}
            </strong>
          </article>

          <article>
            <span>
              Goal
            </span>

            <strong>
              ${esc(lane.capital_goal)}
            </strong>
          </article>
        </div>

        <section>
          <span
            class="ob-owner-kicker"
          >
            SOULAANA · NEXT
          </span>

          <p>
            ${esc(lane.next_action)}
          </p>
        </section>

        <div
          class="ob-owner-safety-note"
        >
          <strong>
            Entering a lane changes owner context only.
          </strong>

          <span>
            It does not move capital,
            submit an order,
            automatically select a contract,
            or unlock execution.
          </span>
        </div>

        <div
          class="ob-lane-actions"
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
            data-owner-drawer-close-secondary
          >
            Close
          </button>
        </div>
      </div>
    `;

    backdrop.appendChild(
      drawer
    );

    document.body.appendChild(
      backdrop
    );


    /*
      Clicking a lane never switches owner context.

      DETAIL ONLY.
                No automatic context switch.
    */


    drawer
      .querySelector(
        "[data-owner-drawer-close]"
      )
      .addEventListener(
        "click",
        closeDrawer
      );


    drawer
      .querySelector(
        "[data-owner-drawer-close-secondary]"
      )
      .addEventListener(
        "click",
        closeDrawer
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

          closeDrawer();

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
          event.target === backdrop
        ) {
          closeDrawer();
        }
      }
    );


    trapFocus(
      drawer
    );
  };


  const edgeCard = (
    label,
    candidate,
    tone
  ) => {
    if (
      !candidate
    ) {
      return `
        <article
          class="ob-edge-card ${tone} empty"
        >
          <div
            class="ob-edge-card-top"
          >
            <span>
              ${label}
            </span>

            <span
              class="ob-edge-dot"
              aria-hidden="true"
            ></span>
          </div>

          <strong>
            Nothing verified here.
          </strong>

          <p>
            OB will not fill this card with fake certainty.
          </p>
        </article>
      `;
    }

    return `
      <button
        type="button"
        class="ob-edge-card ${tone}"
        data-owner-candidate="${esc(candidate.bucket)}:${esc(candidate.source_order)}"
      >
        <div
          class="ob-edge-card-top"
        >
          <span>
            ${label}
          </span>

          ${sourceBadge(candidate)}
        </div>

        <strong
          class="ob-edge-symbol"
        >
          ${esc(candidate.symbol)}
        </strong>

        <span
          class="ob-edge-direction"
        >
          ${esc(candidate.direction)}
        </span>

        <p>
          ${esc(candidate.thesis)}
        </p>

        <small>
          ${
            candidate.option_contract_count
              ? (
                  candidate.option_contract_count
                  + " option contract"
                  + (
                      candidate.option_contract_count === 1
                        ? ""
                        : "s"
                    )
                  + " in research"
                )
              : "Stock research"
          }
        </small>

        <span
          class="ob-edge-open"
        >
          Open analysis →
        </span>
      </button>
    `;
  };


  const findCandidate = (
    key
  ) => {
    const parts =
      String(
        key
      ).split(
        ":"
      );

    const bucket =
      parts[0];

    const sourceOrder =
      Number(
        parts[1]
      );

    const items =
      (
        currentContract
        && currentContract.today_edge
        && Array.isArray(
          currentContract.today_edge[
            bucket
          ]
        )
      )
        ? currentContract.today_edge[
            bucket
          ]
        : [];

    return (
      items.find(
        item =>
          Number(
            item.source_order
          )
          === sourceOrder
      )
      || null
    );
  };


  const activeLaneChip = (
    lane
  ) => `
    <button
      type="button"
      class="ob-active-lane-chip"
      ${
        lane
          ? `data-capital-lane-open="${esc(lane.lane_id)}"`
          : "data-capital-lanes-more"
      }
    >
      <span>
        CAPITAL LANE
      </span>

      <strong>
        ${
          lane
            ? esc(lane.display_label)
            : "No lane selected"
        }
      </strong>

      <small>
        ${
          lane
            ? esc(lane.risk_profile)
            : "Choose only when you need capital context"
        }
      </small>
    </button>
  `;


  const contextTile = (
    kicker,
    value,
    detail
  ) => `
    <article
      class="ob-owner-context-tile"
    >
      <span>
        ${esc(kicker)}
      </span>

      <strong>
        ${esc(value)}
      </strong>

      <small>
        ${esc(detail)}
      </small>
    </article>
  `;


  const render = (
    contract
  ) => {
    currentContract =
      contract;

    const mount =
      document.getElementById(
        "ownerDashboardMount"
      );

    if (
      !mount
    ) {
      return;
    }

    const briefingApi =
      window
        .OB_OWNER_DASHBOARD_SOULAANA_V22;

    const briefing =
      briefingApi
      && typeof briefingApi.buildBriefing
        === "function"
          ? briefingApi.buildBriefing(
              contract
            )
          : {
              eyebrow:
                "SOULAANA · OWNER BRIEFING",

              headline:
                "Owner intelligence is loading.",

              what_i_see:
                "Verified truth stays verified.",

              why_it_matters:
                "Unavailable stays unavailable.",

              next_best_move:
                "No forced move."
            };

    const edge =
      contract.today_edge
      || {
        now: [],
        watch: [],
        not_yet: []
      };

    const lane =
      selectedLane();

    const context =
      contract.owner_context
      || {};

    const positions =
      context.positions
      || {
        count: 0
      };

    const alerts =
      context.alerts
      || {
        count: 0
      };

    const market =
      context.market
      || {
        label:
          "Unavailable"
      };

    const readiness =
      contract.readiness
      || {};

    const attention =
      Array.isArray(
        contract.owner_attention
      )
        ? contract.owner_attention
            .slice(
              0,
              3
            )
        : [];

    const laneNodes =
      lanes(
        contract
      )
        .map(
          item => `
            <button
              type="button"
              class="ob-capital-lane-node"
              data-capital-lane-open="${esc(item.lane_id)}"
            >
              <span
                class="ob-capital-lane-star"
                aria-hidden="true"
              ></span>

              <strong>
                ${esc(item.label)}
              </strong>

              <small>
                ${esc(item.risk_profile)}
              </small>
            </button>
          `
        )
        .join(
          ""
        );


    mount.innerHTML = `
      <main
        class="ob-owner-cockpit"
      >
        <section
          class="ob-owner-hero"
        >
          <div
            class="ob-owner-hero-copy"
          >
            <span
              class="ob-owner-kicker"
            >
              ${esc(briefing.eyebrow)}
            </span>

            <h2>
              ${esc(briefing.headline)}
            </h2>

            <p
              class="ob-owner-hero-read"
            >
              ${esc(briefing.what_i_see)}
            </p>

            <p
              class="ob-owner-hero-why"
            >
              ${esc(briefing.why_it_matters)}
            </p>

            <div
              class="ob-owner-next"
            >
              <span>
                NEXT
              </span>

              <strong>
                ${esc(briefing.next_best_move)}
              </strong>
            </div>
          </div>

          <div
            class="ob-owner-hero-context"
          >
            ${activeLaneChip(lane)}

            <div
              class="ob-owner-hero-truth"
            >
              <span>
                MARKET TRUTH
              </span>

              <strong>
                ${esc(
                  edge.source_state
                    .projection_status
                )}
              </strong>

              <small>
                ${esc(
                  edge.source_state
                    .source
                )}
              </small>
            </div>
          </div>
        </section>

        <section
          class="ob-owner-edge-section"
          aria-labelledby="obOwnerEdgeTitle"
        >
          <div
            class="ob-owner-section-head"
          >
            <div>
              <span
                class="ob-owner-kicker"
              >
                TODAY’S EDGE
              </span>

              <h2
                id="obOwnerEdgeTitle"
              >
                Now. Watch. Not yet.
              </h2>
            </div>

            <span
              class="ob-owner-three-rule"
            >
              Three things max.
            </span>
          </div>

          <div
            class="ob-owner-edge-grid"
          >
            ${edgeCard(
              "NOW",
              edge.now[0],
              "now"
            )}

            ${edgeCard(
              "WATCH",
              edge.watch[0],
              "watch"
            )}

            ${edgeCard(
              "NOT YET",
              edge.not_yet[0],
              "not-yet"
            )}
          </div>
        </section>

        <section
          class="ob-owner-context-grid"
        >
          ${contextTile(
            "MARKET STATE",
            market.label,
            market.verified
              ? "Current verified projection"
              : "Guarded"
          )}

          ${contextTile(
            "TRACKED POSITIONS",
            String(
              positions.count
              || 0
            ),
            (
              positions.count
                ? "Open Trade Center for lifecycle detail"
                : "No source-backed position needs the front page"
            )
          )}

          ${contextTile(
            "OWNER ALERTS",
            String(
              alerts.count
              || 0
            ),
            (
              alerts.count
                ? "Review the highest-priority alert"
                : "No source-backed owner alert"
            )
          )}
        </section>

        <section
          class="ob-owner-attention-section"
        >
          <div
            class="ob-owner-section-head"
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

            <span
              class="ob-owner-three-rule"
            >
              No giant queue.
            </span>
          </div>

          <div
            class="ob-owner-attention-grid"
          >
            ${
              attention.length
                ? attention
                    .map(
                      (item, index) => `
                        <article
                          class="ob-owner-attention-card"
                        >
                          <span>
                            0${index + 1}
                          </span>

                          <strong>
                            ${esc(item.title)}
                          </strong>

                          <p>
                            ${esc(item.detail)}
                          </p>
                        </article>
                      `
                    )
                    .join("")
                : `
                    <article
                      class="ob-owner-attention-card empty"
                    >
                      <strong>
                        Nothing verified is asking for you.
                      </strong>

                      <p>
                        Stay focused.
                      </p>
                    </article>
                  `
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
            class="ob-owner-more-content"
          >
            <div
              class="ob-owner-instrument-grid"
            >
              ${contextTile(
                "MANUAL LIVE READINESS",
                readiness.label
                || "Unavailable",
                (
                  readiness.blockers
                  && readiness.blockers.length
                    ? (
                        readiness.blockers.length
                        + " blocker"
                        + (
                            readiness.blockers.length === 1
                              ? ""
                              : "s"
                          )
                      )
                    : "No verified blocker count"
                )
              )}

              ${contextTile(
                "SYSTEM TRUST",
                contract.trust.label,
                (
                  contract.trust.verified
                    ? "Verified source"
                    : "Guarded"
                )
              )}

              ${contextTile(
                "PRIVATE BETA",
                contract.beta.label,
                "Private only"
              )}
            </div>

            <section
              class="ob-capital-lanes-section"
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

                  <h3>
                    Capital context — secondary.
                  </h3>
                </div>

                <span
                  class="ob-owner-three-rule"
                >
                  CURRENT CAPITAL LANE
                </span>
              </div>

              <div
                class="ob-capital-focus"
              >
                <strong>
                  ${
                    lane
                      ? esc(lane.display_label)
                      : "No lane selected"
                  }
                </strong>

                <span>
                  One lane at a time.
                </span>
              </div>

              <div
                class="ob-capital-lane-nodes"
              >
                ${laneNodes}
              </div>
            </section>

            <details
              class="ob-owner-evidence"
            >
              <summary>
                Show me why
              </summary>

              <div>
                <span>
                  source_state
                </span>

                <span>
                  interpretation_state
                </span>

                <span>
                  boundaries
                </span>

                <span>
                  Ranked contract ≠ selected contract
                </span>
              </div>
            </details>
          </div>
        </details>

        <div
          class="ob-owner-boundary"
        >
          <strong>
            Research is not execution.
          </strong>

          <span>
            No broker submission ·
            no capital movement ·
            no automatic contract selection ·
            no automatic execution ·
            Live Auto Locked
          </span>
        </div>
      </main>
    `;


    mount
      .querySelectorAll(
        "[data-owner-candidate]"
      )
      .forEach(
        function (
          button
        ) {
          button.addEventListener(
            "click",
            function () {
              const candidate =
                findCandidate(
                  button.dataset
                    .ownerCandidate
                );

              openCandidateDrawer(
                candidate
              );
            }
          );
        }
      );


    mount
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
                button.dataset
                  .capitalLaneOpen
              );
            }
          );
        }
      );


    const noLane =
      mount.querySelector(
        "[data-capital-lanes-more]"
      );

    if (
      noLane
    ) {
      noLane.addEventListener(
        "click",
        function () {
          const first =
            lanes(
              currentContract
            )[0];

          if (
            first
          ) {
            openLaneDrawer(
              first.lane_id
            );
          }
        }
      );
    }


    document.body.setAttribute(
      "data-ob-owner-intelligence-state",
      contract.status
    );
  };


  const hydrateAndRender = async () => {
    const api =
      window
        .OB_OWNER_DASHBOARD_CONTRACT_V21;

    if (
      !api
      || typeof api.hydrate
        !== "function"
    ) {
      return;
    }

    const contract =
      await api.hydrate();

    render(
      contract
    );
  };


  window.addEventListener(
    "obEngineFeedAdapterUpdated",
    function () {
      hydrateAndRender();
    }
  );


  if (
    document.readyState
    === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      hydrateAndRender,
      {
        once:
          true
      }
    );
  } else {
    hydrateAndRender();
  }


  window.OB_OWNER_DASHBOARD_V23 =
    Object.freeze({
      version:
        VERSION,

      render,

      hydrateAndRender,

      safety: {
        broker_submission:
          false,

        capital_movement:
          false,

        automatic_contract_selection:
          false,

        automatic_execution:
          false,

        live_auto_locked:
          true
      }
    });

})();
