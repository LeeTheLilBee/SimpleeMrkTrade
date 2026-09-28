// OBSERVATORY_OBUX059_GLOBAL_SESSION_TOWER_RETURN_SHELL

(function (global) {
  "use strict";

  const TOWER_RETURN =
    "/tower/return/observatory";

  const IDLE_MS =
    15 * 60 * 1000;

  let lastInteraction =
    Date.now();

  let feedbackModal =
    null;

  let privacyModal =
    null;


  function state() {
    return global
      .OBSessionState
      || null;
  }


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


  function currentRoom(
    path
  ) {
    if (
      path.includes(
        "/symbol/"
      )
    ) {
      return "Symbol Room";
    }

    if (
      path.includes(
        "market-map"
      )
    ) {
      return "Market Map";
    }

    if (
      path.includes(
        "trade-center"
      )
    ) {
      return "Trade Center";
    }

    if (
      path.includes(
        "review-center"
      )
    ) {
      return "Review Center";
    }

    if (
      path.includes(
        "owner-dashboard"
      )
    ) {
      return "Owner Dashboard";
    }

    if (
      path.includes(
        "owner-console"
      )
    ) {
      return "Owner Console";
    }

    return "Dashboard";
  }


  function installStyles() {
    if (
      document.getElementById(
        "obGlobalSessionShellStyle"
      )
    ) {
      return;
    }

    const style =
      document.createElement(
        "style"
      );

    style.id =
      "obGlobalSessionShellStyle";

    style.textContent = `
      .ob-global-session-bar {
        position: fixed;
        top: 16px;
        right: 18px;
        z-index: 7600;
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 7px;
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 999px;
        background: rgba(8,6,14,.87);
        backdrop-filter: blur(16px);
        box-shadow: 0 16px 50px rgba(0,0,0,.28);
      }

      .ob-global-chip,
      .ob-global-action {
        padding: 8px 11px;
        border: 0;
        border-radius: 999px;
        background: transparent;
        color: #aaa2b8;
        font-size: 11px;
        text-decoration: none;
      }

      .ob-global-chip {
        background: rgba(255,255,255,.045);
      }

      .ob-global-chip.mode {
        color: #e1ca86;
      }

      .ob-global-chip.locked {
        color: #ffabb4;
      }

      .ob-global-action {
        cursor: pointer;
      }

      .ob-global-action:hover {
        background: rgba(255,255,255,.06);
        color: #fff;
      }

      .ob-global-action.exit {
        color: #e1ca86;
      }

      .ob-global-modal {
        position: fixed;
        inset: 0;
        z-index: 15000;
        display: grid;
        place-items: center;
        padding: 24px;
        background: rgba(1,1,5,.84);
        backdrop-filter: blur(14px);
      }

      .ob-global-modal-card {
        width: min(620px,95vw);
        padding: 24px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 24px;
        background: #0b0912;
        color: #f4efff;
        box-shadow: 0 30px 100px rgba(0,0,0,.65);
      }

      .ob-global-modal-card h2 {
        margin: 5px 0 10px;
        font-size: 30px;
        letter-spacing: -.03em;
      }

      .ob-global-modal-card p {
        color: #aaa2b8;
        line-height: 1.55;
      }

      .ob-global-modal-actions {
        display: flex;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
      }

      .ob-global-button {
        padding: 10px 14px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 999px;
        background: rgba(255,255,255,.05);
        color: #f4efff;
        cursor: pointer;
        text-decoration: none;
      }

      .ob-global-button.primary {
        border-color: #9672e8;
        background: #7957c8;
      }

      .ob-global-button.danger {
        border-color: rgba(255,157,168,.3);
        color: #ffb4bc;
      }

      .ob-feedback-categories {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin: 14px 0;
      }

      .ob-feedback-categories label input {
        position: absolute;
        opacity: 0;
      }

      .ob-feedback-categories label span {
        display: block;
        padding: 8px 10px;
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 999px;
        color: #aaa2b8;
        cursor: pointer;
      }

      .ob-feedback-categories label input:checked + span {
        border-color: #9f7bea;
        background: rgba(132,90,210,.16);
        color: #fff;
      }

      .ob-feedback-text {
        width: 100%;
        min-height: 110px;
        resize: vertical;
        padding: 12px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 15px;
        background: rgba(255,255,255,.035);
        color: #fff;
      }

      .ob-privacy-cover {
        position: fixed;
        inset: 0;
        z-index: 20000;
        display: grid;
        place-items: center;
        padding: 30px;
        background: #05040a;
        color: #f4efff;
        text-align: center;
      }

      .ob-privacy-cover > div {
        max-width: 560px;
      }

      .ob-privacy-cover h2 {
        margin: 8px 0;
        font-size: 40px;
      }

      .ob-privacy-cover p {
        color: #aaa2b8;
        line-height: 1.6;
      }

      .ob-cross-room-guide {
        position: fixed;
        left: 76px;
        bottom: 24px;
        z-index: 8500;
        width: min(430px, calc(100vw - 108px));
        padding: 18px;
        border: 1px solid rgba(211,183,255,.23);
        border-radius: 22px;
        background: rgba(12,9,22,.97);
        color: #f4efff;
        box-shadow: 0 24px 80px rgba(0,0,0,.48);
      }

      .ob-cross-room-guide small {
        color: #e1ca86;
        font-weight: 800;
        letter-spacing: .14em;
      }

      .ob-cross-room-guide strong {
        display: block;
        margin: 7px 0;
      }

      .ob-cross-room-guide p {
        color: #aaa2b8;
        font-size: 13px;
        line-height: 1.5;
      }

      .ob-cross-room-guide-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      @media (max-width: 760px) {
        .ob-global-session-bar {
          top: 8px;
          right: 8px;
          max-width: calc(100vw - 64px);
          overflow-x: auto;
        }

        .ob-global-chip {
          display: none;
        }

        .ob-cross-room-guide {
          left: 12px;
          bottom: 12px;
          width: calc(100vw - 24px);
        }
      }
    `;

    document.head.appendChild(
      style
    );
  }


  function buildSessionBar() {
    if (
      document.getElementById(
        "obGlobalSessionBar"
      )
    ) {
      return;
    }

    const current =
      state()
        ? state().snapshot()
        : null;

    const mode =
      current
      && current.persistent
        ? (
            current
              .persistent
              .selectedMode
            || "Survey"
          )
        : "Survey";

    const bar =
      document.createElement(
        "div"
      );

    bar.id =
      "obGlobalSessionBar";

    bar.className =
      "ob-global-session-bar";

    bar.setAttribute(
      "aria-label",
      "Observatory session controls"
    );

    bar.innerHTML = `
      <span
        class="ob-global-chip mode"
      >
        ${esc(mode)} Mode
      </span>

      <span
        class="ob-global-chip locked"
      >
        Live Auto Locked
      </span>

      <button
        type="button"
        class="ob-global-action"
        data-global-action="feedback"
      >
        ◇ Feedback
      </button>

      <button
        type="button"
        class="ob-global-action"
        data-global-action="tower"
      >
        Back to Tower
      </button>

      <button
        type="button"
        class="ob-global-action exit"
        data-global-action="signout"
      >
        Sign out of OB
      </button>
    `;

    document.body.appendChild(
      bar
    );
  }


  function modal(
    content
  ) {
    const shell =
      document.createElement(
        "div"
      );

    shell.className =
      "ob-global-modal";

    shell.innerHTML = `
      <section
        class="ob-global-modal-card"
        role="dialog"
        aria-modal="true"
      >
        ${content}
      </section>
    `;

    document.body.appendChild(
      shell
    );

    return shell;
  }


  function closeFeedback() {
    if (
      feedbackModal
    ) {
      feedbackModal.remove();
    }

    feedbackModal = null;
  }


  function openFeedback(
    context
  ) {
    closeFeedback();

    const room =
      currentRoom(
        global.location.pathname
      );

    const current =
      state()
        ? state().snapshot()
        : null;

    const mode =
      current
      && current.persistent
        ? (
            current
              .persistent
              .selectedMode
            || "unknown"
          )
        : "unknown";

    const symbol =
      current
      && current.ephemeral
        ? (
            current
              .ephemeral
              .selectedSymbol
            || null
          )
        : null;

    const build =
      document.body
        ? (
            document.body
              .dataset
              .obBuild
            || "unknown"
          )
        : "unknown";

    feedbackModal =
      modal(
        `
          <span
            style="
              color:#e1ca86;
              font-size:10px;
              letter-spacing:.16em;
              font-weight:800;
            "
          >
            PRIVATE BETA FEEDBACK
          </span>

          <h2>
            Tell us what happened.
          </h2>

          <p>
            I already know you’re in
            <strong>${esc(room)}</strong>
            · ${esc(mode)}
            ${symbol ? " · " + esc(symbol) : ""}
            · ${esc(build)}.

            You don’t have to reconstruct
            the whole scene.
          </p>

          <form
            id="obGlobalFeedbackForm"
          >
            <div
              class="ob-feedback-categories"
            >
              ${
                [
                  "Confusing",
                  "Looks wrong",
                  "Didn't work",
                  "Hard to find",
                  "I like this",
                  "Other",
                ]
                  .map(
                    function (
                      category
                    ) {
                      return `
                        <label>
                          <input
                            type="radio"
                            name="category"
                            value="${esc(category)}"
                          />

                          <span>
                            ${esc(category)}
                          </span>
                        </label>
                      `;
                    }
                  )
                  .join(
                    ""
                  )
              }
            </div>

            <textarea
              class="ob-feedback-text"
              name="message"
              placeholder="What did you notice?"
            ></textarea>

            <div
              class="ob-global-modal-actions"
            >
              <button
                type="button"
                class="ob-global-button"
                data-feedback-cancel
              >
                Cancel
              </button>

              <button
                type="submit"
                class="ob-global-button primary"
              >
                Save feedback
              </button>
            </div>
          </form>

          <p
            style="
              font-size:11px;
              color:#716a7c;
            "
          >
            Until a canonical server submission sink is connected,
            this control says exactly what it does:
            the feedback is saved to your OB beta queue
            in this browser and emitted as a structured browser event
            for existing beta tooling.
          </p>
        `
      );

    feedbackModal
      .querySelector(
        "[data-feedback-cancel]"
      )
      .addEventListener(
        "click",
        closeFeedback
      );

    feedbackModal
      .querySelector(
        "#obGlobalFeedbackForm"
      )
      .addEventListener(
        "submit",
        function (
          event
        ) {
          event.preventDefault();

          const form =
            new FormData(
              event.currentTarget
            );

          const item =
            state()
              ? state()
                  .captureFeedback(
                    {
                      category:
                        form.get(
                          "category"
                        )
                        || "Other",

                      message:
                        form.get(
                          "message"
                        )
                        || "",

                      component:
                        context
                        && context.component
                          ? context.component
                          : room,

                      sourceState:
                        context
                        && context.sourceState
                          ? context.sourceState
                          : null,
                    }
                  )
              : null;

          global.dispatchEvent(
            new CustomEvent(
              "ob:private-beta-feedback-captured",
              {
                detail:
                  item,
              }
            )
          );

          feedbackModal
            .querySelector(
              ".ob-global-modal-card"
            )
            .innerHTML = `
              <span
                style="
                  color:#e1ca86;
                  font-size:10px;
                  letter-spacing:.16em;
                  font-weight:800;
                "
              >
                SAVED
              </span>

              <h2>
                Got it.
              </h2>

              <p>
                This note is in your local OB beta feedback queue
                for handoff.

                I did not pretend it reached
                a server endpoint.
              </p>

              <div
                class="ob-global-modal-actions"
              >
                <button
                  class="ob-global-button primary"
                  data-feedback-done
                >
                  Done
                </button>
              </div>
            `;

          feedbackModal
            .querySelector(
              "[data-feedback-done]"
            )
            .addEventListener(
              "click",
              closeFeedback
            );
        }
      );
  }


  function privacyCover(
    title,
    body,
    showReturn
  ) {
    if (
      privacyModal
    ) {
      privacyModal.remove();
    }

    privacyModal =
      document.createElement(
        "div"
      );

    privacyModal.className =
      "ob-privacy-cover";

    privacyModal.innerHTML = `
      <div>
        <span
          style="
            color:#e1ca86;
            font-size:10px;
            letter-spacing:.17em;
            font-weight:800;
          "
        >
          THE OBSERVATORY
        </span>

        <h2>
          ${esc(title)}
        </h2>

        <p>
          ${esc(body)}
        </p>

        ${
          showReturn
            ? `
                <a
                  class="ob-global-button primary"
                  href="/tower/return/observatory"
                  style="
                    display:inline-block;
                    text-decoration:none;
                  "
                >
                  Return through Tower →
                </a>
              `
            : ""
        }
      </div>
    `;

    document.body.appendChild(
      privacyModal
    );
  }


  function backToTower() {
    if (
      state()
    ) {
      state().close(
        "return_to_tower",
        true
      );
    }

    privacyCover(
      "Returning to Tower",
      "Your OB screen is covered. Tower remains the identity and permission authority.",
      false
    );

    global.location.assign(
      TOWER_RETURN
      + "?ob_action=return"
    );
  }


  function performSignOut() {
    if (
      state()
    ) {
      state().close(
        "sign_out_of_ob",
        false
      );

      state()
        .clearEphemeral();
    }

    privacyCover(
      "Closing your OB session",
      "Sensitive OB session state is being cleared before Tower receives you.",
      false
    );

    global.location.assign(
      TOWER_RETURN
      + "?ob_action=signout"
    );
  }


  function signOut() {
    const current =
      state()
        ? state().snapshot()
        : null;

    const active =
      Number(
        current
        && current.ephemeral
          ? (
              current
                .ephemeral
                .activeTrackedPositions
              || 0
            )
          : 0
      );

    if (
      active <= 0
    ) {
      performSignOut();
      return;
    }

    const shell =
      modal(
        `
          <span
            style="
              color:#ffb4bc;
              font-size:10px;
              letter-spacing:.16em;
              font-weight:800;
            "
          >
            ACTIVE TRACKING
          </span>

          <h2>
            You have
            ${active}
            trade${active === 1 ? "" : "s"}
            being tracked by OB.
          </h2>

          <p>
            Signing out of OB does
            <strong>not</strong>
            close a brokerage position.

            External brokerage action remains external.
          </p>

          <div
            class="ob-global-modal-actions"
          >
            <button
              class="ob-global-button"
              data-signout-cancel
            >
              Return to OB
            </button>

            <button
              class="ob-global-button danger"
              data-signout-confirm
            >
              Sign out of OB
            </button>
          </div>
        `
      );

    shell
      .querySelector(
        "[data-signout-cancel]"
      )
      .addEventListener(
        "click",
        function () {
          shell.remove();
        }
      );

    shell
      .querySelector(
        "[data-signout-confirm]"
      )
      .addEventListener(
        "click",
        function () {
          shell.remove();
          performSignOut();
        }
      );
  }


  function reflectThen(
    action
  ) {
    const current =
      state()
        ? state().snapshot()
        : null;

    if (
      !current
    ) {
      action();
      return;
    }

    const started =
      Date.parse(
        current
          .ephemeral
          .startedAt
        || new Date()
          .toISOString()
      );

    const feedbackCount =
      current
        .ephemeral
        .feedbackThisSession
        .length;

    const meaningful =
      (
        Date.now()
        - started
      ) > (
        5
        * 60
        * 1000
      )
      || feedbackCount > 0;

    if (
      !meaningful
    ) {
      action();
      return;
    }

    const shell =
      modal(
        `
          <span
            style="
              color:#e1ca86;
              font-size:10px;
              letter-spacing:.16em;
              font-weight:800;
            "
          >
            OPTIONAL SESSION REFLECTION
          </span>

          <h2>
            Before you go —
            how did OB feel?
          </h2>

          <p>
            This is beta feedback,
            not a diagnosis.
          </p>

          <div
            class="ob-feedback-categories"
          >
            ${
              [
                "Smooth",
                "Easy",
                "Confusing",
                "Overwhelming",
                "Something felt wrong",
              ]
                .map(
                  function (
                    choice
                  ) {
                    return `
                      <label>
                        <input
                          type="radio"
                          name="reflection"
                          value="${esc(choice)}"
                        />

                        <span>
                          ${esc(choice)}
                        </span>
                      </label>
                    `;
                  }
                )
                .join(
                  ""
                )
            }
          </div>

          <div
            class="ob-global-modal-actions"
          >
            <button
              class="ob-global-button"
              data-reflect-skip
            >
              Skip
            </button>

            <button
              class="ob-global-button primary"
              data-reflect-save
            >
              Save & continue
            </button>
          </div>
        `
      );

    shell
      .querySelector(
        "[data-reflect-skip]"
      )
      .addEventListener(
        "click",
        function () {
          shell.remove();
          action();
        }
      );

    shell
      .querySelector(
        "[data-reflect-save]"
      )
      .addEventListener(
        "click",
        function () {
          const selected =
            shell.querySelector(
              'input[name="reflection"]:checked'
            );

          if (
            selected
            && state()
          ) {
            state()
              .setReflection(
                selected.value
              );
          }

          shell.remove();
          action();
        }
      );
  }


  function showCrossRoomGuide() {
    const current =
      state()
        ? state().snapshot()
        : null;

    if (
      !current
      || !current
        .ephemeral
        .guidance
        .enabled
    ) {
      return;
    }

    const room =
      currentRoom(
        global.location.pathname
      );

    if (
      room === "Dashboard"
    ) {
      /*
        Dashboard owns its prettier
        account-home guide prompt.
      */
      return;
    }

    const old =
      document.getElementById(
        "obCrossRoomGuide"
      );

    if (
      old
    ) {
      old.remove();
    }

    const prompt =
      document.createElement(
        "aside"
      );

    prompt.id =
      "obCrossRoomGuide";

    prompt.className =
      "ob-cross-room-guide";

    let title =
      "";

    let body =
      "";

    let nextHtml =
      "";

    if (
      room === "Market Map"
    ) {
      title =
        "Look at the real sky.";

      body =
        "Choose a real symbol that makes you curious. "
        + "Symbol Room opens from a real selection — "
        + "I won’t fabricate one for the tutorial.";

      nextHtml =
        "";
    } else if (
      room === "Symbol Room"
    ) {
      title =
        "Study one name.";

      body =
        "Read the source-backed symbol and option context. "
        + "When you have something worth working, "
        + "Trade Center owns the lifecycle.";

      nextHtml = `
        <a
          class="ob-global-button primary"
          href="/trade-center"
        >
          Go to Trade Center →
        </a>
      `;
    } else if (
      room === "Trade Center"
    ) {
      title =
        "Work the lifecycle.";

      body =
        "Research → Contract → Preflight → Entry → Manage → Exit. "
        + "Then Review Center studies both outcome and process.";

      nextHtml = `
        <a
          class="ob-global-button primary"
          href="/review-center"
        >
          Go to Review Center →
        </a>
      `;
    } else if (
      room === "Review Center"
    ) {
      title =
        "Close the loop.";

      body =
        "Review what happened, why it happened, "
        + "and whether the process was clean — "
        + "including losses, overtime, and Negative Dive evidence.";

      nextHtml = `
        <button
          type="button"
          class="ob-global-button primary"
          data-guide-complete
        >
          Finish guide ✓
        </button>
      `;
    } else {
      return;
    }

    prompt.innerHTML = `
      <small>
        SOULAANA · GUIDE
      </small>

      <strong>
        ${esc(title)}
      </strong>

      <p>
        ${esc(body)}
      </p>

      <div
        class="ob-cross-room-guide-actions"
      >
        <button
          type="button"
          class="ob-global-button"
          data-guide-stop
        >
          Stop guide
        </button>

        ${nextHtml}
      </div>
    `;

    document.body.appendChild(
      prompt
    );

    prompt
      .querySelector(
        "[data-guide-stop]"
      )
      .addEventListener(
        "click",
        function () {
          state()
            .setGuidance(
              false,
              "complete"
            );

          prompt.remove();
        }
      );

    const complete =
      prompt.querySelector(
        "[data-guide-complete]"
      );

    if (
      complete
    ) {
      complete.addEventListener(
        "click",
        function () {
          state()
            .setGuidance(
              false,
              "complete"
            );

          prompt.remove();
        }
      );
    }
  }


  function recordCurrentRoute() {
    if (
      !state()
    ) {
      return;
    }

    const room =
      currentRoom(
        global.location.pathname
      );

    /*
      Do not overwrite a recoverable
      non-Dashboard route before
      the Dashboard arrival system
      asks whether to resume it.
    */
    if (
      room === "Dashboard"
      && state()
        .resumeCandidate()
    ) {
      return;
    }

    state()
      .recordRoute(
        global.location.pathname,
        room
      );

    const symbolMatch =
      global
        .location
        .pathname
        .match(
          /\/ob\/symbol\/([^/]+)/i
        );

    if (
      symbolMatch
    ) {
      state()
        .recordSymbol(
          decodeURIComponent(
            symbolMatch[1]
          )
        );
    }
  }


  function checkIdle() {
    if (
      Date.now()
      - lastInteraction
      < IDLE_MS
    ) {
      return;
    }

    if (
      privacyModal
    ) {
      return;
    }

    privacyCover(
      "Privacy lock",
      "OB was idle, so the sensitive screen is covered. Re-enter through Tower rather than through an OB-local password prompt.",
      true
    );
  }


  function updateExistingRouteModeChip() {
    const current =
      state()
        ? state().snapshot()
        : null;

    const mode =
      current
      && current.persistent
        ? (
            current
              .persistent
              .selectedMode
            || "Survey"
          )
        : "Survey";

    /*
      Preserve the existing canonical nav shell,
      but stop its old hard-coded Paper label
      from lying about the current session.
    */

    const candidates =
      document.querySelectorAll(
        "#obRouteBar .gold, "
        + "#obRouteBar .ob-route-chip.gold"
      );

    candidates.forEach(
      function (
        chip
      ) {
        chip.textContent =
          mode
          + " Mode";
      }
    );
  }


  function attach() {
    installStyles();

    if (
      state()
    ) {
      state()
        .claimTab(
          false
        );
    }

    buildSessionBar();

    recordCurrentRoute();

    updateExistingRouteModeChip();

    showCrossRoomGuide();

    document.addEventListener(
      "click",
      function (
        event
      ) {
        const node =
          event.target.closest(
            "[data-global-action]"
          );

        if (
          !node
        ) {
          return;
        }

        const action =
          node
            .dataset
            .globalAction;

        if (
          action === "feedback"
        ) {
          openFeedback(
            {
              component:
                currentRoom(
                  global.location.pathname
                ),
            }
          );
        }

        if (
          action === "tower"
        ) {
          reflectThen(
            backToTower
          );
        }

        if (
          action === "signout"
        ) {
          reflectThen(
            signOut
          );
        }
      }
    );

    global.addEventListener(
      "ob:open-feedback",
      function (
        event
      ) {
        openFeedback(
          event.detail
          || {}
        );
      }
    );

    global.addEventListener(
      "ob:session-persistent-change",
      function () {
        const current =
          state()
            ? state().snapshot()
            : null;

        const mode =
          current
          && current.persistent
            ? (
                current
                  .persistent
                  .selectedMode
                || "Survey"
              )
            : "Survey";

        const chip =
          document.querySelector(
            "#obGlobalSessionBar .ob-global-chip.mode"
          );

        if (
          chip
        ) {
          chip.textContent =
            mode
            + " Mode";
        }

        updateExistingRouteModeChip();
      }
    );

    [
      "pointerdown",
      "keydown",
      "touchstart",
      "scroll",
    ].forEach(
      function (
        name
      ) {
        global.addEventListener(
          name,
          function () {
            lastInteraction =
              Date.now();
          },
          {
            passive: true,
          }
        );
      }
    );

    global.setInterval(
      checkIdle,
      30000
    );
  }


  if (
    document.readyState
      === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      attach
    );
  } else {
    attach();
  }


  global.OBGlobalSessionShell =
    Object.freeze(
      {
        backToTower:
          function () {
            reflectThen(
              backToTower
            );
          },

        signOut:
          function () {
            reflectThen(
              signOut
            );
          },

        openFeedback,
      }
    );

})(window);
