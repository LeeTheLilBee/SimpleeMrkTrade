// OBSERVATORY_OBUX058_SOULAANA_ARRIVAL

(function (global) {
  "use strict";

  let activeModal = null;
  let focusBeforeModal = null;
  let touchStartX = null;


  const SOP = [
    {
      eyebrow:
        "WELCOME TO THE OBSERVATORY",

      title:
        "You’re testing the real OB experience.",

      body:
        "Use it like a person, not like a proof page. "
        + "We want to know whether the product makes sense, "
        + "feels good, and helps you know what to do next.",

      foot:
        "Private Beta · Page 1",
    },

    {
      eyebrow:
        "HOW TO FLOW",

      title:
        "Move through the rooms instead of wandering.",

      body:
        "Dashboard gives your account snapshot. "
        + "Market Map shows the sky. "
        + "Symbol Room studies one name. "
        + "Trade Center works the lifecycle. "
        + "Review Center studies outcome and process.",

      foot:
        "Dashboard → Map → Symbol → Trade → Review",
    },

    {
      eyebrow:
        "WHAT TO LOOK FOR",

      title:
        "Notice anything that makes you hesitate.",

      body:
        "Confusing information, missing information, "
        + "hard-to-find actions, broken behavior, "
        + "visual clutter, awkward wording, "
        + "or a moment where you don’t know what to do next — "
        + "tell us.",

      foot:
        "Your hesitation is useful beta evidence.",
    },

    {
      eyebrow:
        "PAY ATTENTION TO SOULAANA",

      title:
        "Is she actually helping?",

      body:
        "Notice whether Soulaana explains what something means, "
        + "why it matters, what changed, "
        + "and where to move next — "
        + "without getting in your way.",

      foot:
        "Helpful, clear, timely. Not noise.",
    },

    {
      eyebrow:
        "MARKET TRUTH",

      title:
        "Weird data should feel weird.",

      body:
        "If a price looks stale, numbers conflict, "
        + "a source is unclear, an option looks strange, "
        + "or something is missing, flag it. "
        + "OB should show unavailable or guarded truth "
        + "instead of making something up.",

      foot:
        "Unknown stays unknown.",
    },

    {
      eyebrow:
        "HOW DOES IT FEEL?",

      title:
        "The experience matters too.",

      body:
        "Too crowded? Too empty? Beautiful? Annoying? "
        + "Smooth? Overwhelming? Easy? Tell us. "
        + "Beta is about the product experience, "
        + "not just whether a button technically fires.",

      foot:
        "Feedback is available everywhere in OB.",
    },

    {
      eyebrow:
        "YOU’RE READY",

      title:
        "Use OB normally.",

      body:
        "There’s no perfect way to test this. "
        + "If something makes you stop and think "
        + "“what the hell is this?” — "
        + "we want to know about it.",

      foot:
        "Enter when you’re ready.",

      final:
        true,
    },
  ];


  const WHATS_NEW = [
    {
      eyebrow:
        "WHAT CHANGED",

      title:
        "Tower now opens the real Observatory.",

      body:
        "The normal Tower launch now lands on the protected "
        + "Dashboard product surface instead of sending you "
        + "through an internal walkthrough page first.",

      foot:
        "OBUX066–070",
    },

    {
      eyebrow:
        "NEW",

      title:
        "The arrival sequence is finally on the real doorway.",

      body:
        "Versioned beta guidance, Soulaana check-in, "
        + "safe resume, and first-session guidance now run "
        + "on the Dashboard users actually enter.",

      foot:
        "SOP → Soulaana → Dashboard.",
    },

    {
      eyebrow:
        "NEW",

      title:
        "Your selected Observatory theme now owns the sky.",

      body:
        "Obsidian Plum, Velvet Night, and Eclipse Gold "
        + "now control the visible Observatory atmosphere. "
        + "The old V27 blue room-weather palette no longer "
        + "wins underneath the product theme.",

      foot:
        "Same Observatory. Your chosen night sky.",

      final:
        true,
    },
  ];


  function state() {
    return global
      .OBSessionState;
  }


  function root() {
    return document
      .getElementById(
        "obArrivalRoot"
      );
  }


  function escapeHtml(
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


  function lockPage() {
    document
      .documentElement
      .classList
      .add(
        "ob-modal-open"
      );

    document
      .body
      .classList
      .add(
        "ob-arrival-active"
      );
  }


  function unlockPage() {
    document
      .documentElement
      .classList
      .remove(
        "ob-modal-open"
      );

    document
      .documentElement
      .classList
      .remove(
        "ob-arrival-booting"
      );

    document
      .body
      .classList
      .remove(
        "ob-arrival-active"
      );
  }


  function closeModal() {
    if (
      activeModal
    ) {
      activeModal.remove();
    }

    activeModal = null;

    unlockPage();

    if (
      focusBeforeModal
      && typeof focusBeforeModal.focus
        === "function"
    ) {
      focusBeforeModal.focus();
    }
  }


  function trapFocus(
    modal,
    event
  ) {
    if (
      event.key
      !== "Tab"
    ) {
      return;
    }

    const focusable =
      [
        ...modal.querySelectorAll(
          'button:not([disabled]), '
          + '[href], '
          + 'input:not([disabled]), '
          + 'textarea:not([disabled]), '
          + '[tabindex]:not([tabindex="-1"])'
        ),
      ].filter(
        function (
          element
        ) {
          return (
            !element.hidden
            && element.offsetParent
              !== null
          );
        }
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

    if (
      event.shiftKey
      && document.activeElement
        === first
    ) {
      event.preventDefault();
      last.focus();
    } else if (
      !event.shiftKey
      && document.activeElement
        === last
    ) {
      event.preventDefault();
      first.focus();
    }
  }


  function mountModal(
    inner,
    options
  ) {
    closeModal();

    focusBeforeModal =
      document.activeElement;

    lockPage();

    const shell =
      document.createElement(
        "div"
      );

    shell.className =
      "ob-modal-shell";

    shell.dataset.modalKind =
      options
      && options.kind
        ? options.kind
        : "general";

    shell.innerHTML = `
      <div
        class="ob-modal-backdrop"
        aria-hidden="true"
      ></div>

      <section
        class="ob-modal-card"
        role="dialog"
        aria-modal="true"
        aria-label="${escapeHtml(
          options
          && options.label
            ? options.label
            : "Observatory dialog"
        )}"
      >
        ${inner}
      </section>
    `;

    root().appendChild(
      shell
    );

    activeModal =
      shell;

    shell.addEventListener(
      "keydown",
      function (
        event
      ) {
        trapFocus(
          shell,
          event
        );

        if (
          event.key
            === "Escape"
          && options
          && options.escapeAllowed
        ) {
          event.preventDefault();
          closeModal();
        }
      }
    );

    const first =
      shell.querySelector(
        "button, [href], input, [tabindex='0']"
      );

    if (
      first
    ) {
      window.setTimeout(
        function () {
          first.focus();
        },
        0
      );
    }

    return shell;
  }


  function carousel(
    slides,
    options
  ) {
    let index = 0;


    function render() {
      const slide =
        slides[index];

      const dots =
        slides
          .map(
            function (
              _,
              dotIndex
            ) {
              const active =
                dotIndex
                === index;

              return `
                <button
                  type="button"
                  class="ob-carousel-dot${active ? " active" : ""}"
                  data-carousel-index="${dotIndex}"
                  aria-label="Go to page ${dotIndex + 1}"
                  aria-current="${active ? "true" : "false"}"
                ></button>
              `;
            }
          )
          .join(
            ""
          );

      const inner = `
        <div
          class="ob-carousel"
        >
          <div
            class="ob-carousel-top"
          >
            <div
              class="ob-carousel-brand"
            >
              <span
                class="ob-orbit-mark"
              >
                ✦
              </span>

              <span>
                ${escapeHtml(
                  slide.eyebrow
                )}
              </span>
            </div>

            ${
              options
              && options.allowClose
                ? `
                    <button
                      class="ob-icon-button"
                      data-carousel-close
                      aria-label="Close"
                    >
                      ×
                    </button>
                  `
                : ""
            }
          </div>

          <div
            class="ob-carousel-stage"
          >
            <button
              type="button"
              class="ob-carousel-arrow left"
              data-carousel-prev
              aria-label="Previous page"
              ${index === 0 ? "disabled" : ""}
            >
              ‹
            </button>

            <article
              class="ob-carousel-page"
            >
              <div
                class="ob-carousel-art"
                aria-hidden="true"
              >
                <span></span>
                <span></span>
                <span></span>
              </div>

              <h2>
                ${escapeHtml(
                  slide.title
                )}
              </h2>

              <p>
                ${escapeHtml(
                  slide.body
                )}
              </p>

              <small>
                ${escapeHtml(
                  slide.foot
                )}
              </small>
            </article>

            <button
              type="button"
              class="ob-carousel-arrow right"
              data-carousel-next
              aria-label="${slide.final ? "Finish" : "Next page"}"
            >
              ${slide.final ? "✓" : "›"}
            </button>
          </div>

          <div
            class="ob-carousel-bottom"
          >
            <div
              class="ob-carousel-dots"
              aria-label="Carousel pages"
            >
              ${dots}
            </div>

            <span>
              ${index + 1} of ${slides.length}
            </span>
          </div>
        </div>
      `;

      const shell =
        mountModal(
          inner,
          {
            kind:
              options.kind,

            label:
              options.label,

            escapeAllowed:
              Boolean(
                options.allowClose
              ),
          }
        );

      const previous =
        shell.querySelector(
          "[data-carousel-prev]"
        );

      const next =
        shell.querySelector(
          "[data-carousel-next]"
        );

      if (
        previous
      ) {
        previous.addEventListener(
          "click",
          function () {
            if (
              index > 0
            ) {
              index -= 1;
              render();
            }
          }
        );
      }

      next.addEventListener(
        "click",
        function () {
          if (
            slide.final
          ) {
            closeModal();

            if (
              typeof options.onComplete
              === "function"
            ) {
              options.onComplete();
            }

            return;
          }

          index =
            Math.min(
              slides.length - 1,
              index + 1
            );

          render();
        }
      );

      shell
        .querySelectorAll(
          "[data-carousel-index]"
        )
        .forEach(
          function (
            dot
          ) {
            dot.addEventListener(
              "click",
              function () {
                index =
                  Number(
                    dot.dataset
                      .carouselIndex
                  );

                render();
              }
            );
          }
        );

      const close =
        shell.querySelector(
          "[data-carousel-close]"
        );

      if (
        close
      ) {
        close.addEventListener(
          "click",
          closeModal
        );
      }

      shell.addEventListener(
        "keydown",
        function (
          event
        ) {
          if (
            event.key
              === "ArrowRight"
          ) {
            event.preventDefault();

            if (
              slide.final
            ) {
              closeModal();

              if (
                typeof options.onComplete
                === "function"
              ) {
                options.onComplete();
              }

              return;
            }

            index =
              Math.min(
                slides.length - 1,
                index + 1
              );

            render();
          }

          if (
            event.key
              === "ArrowLeft"
            && index > 0
          ) {
            event.preventDefault();

            index -= 1;

            render();
          }
        }
      );

      shell.addEventListener(
        "touchstart",
        function (
          event
        ) {
          if (
            event.changedTouches
            && event.changedTouches[0]
          ) {
            touchStartX =
              event
                .changedTouches[0]
                .screenX;
          }
        },
        {
          passive: true,
        }
      );

      shell.addEventListener(
        "touchend",
        function (
          event
        ) {
          if (
            touchStartX
              === null
          ) {
            return;
          }

          const currentX =
            event.changedTouches
            && event.changedTouches[0]
              ? event
                  .changedTouches[0]
                  .screenX
              : touchStartX;

          const delta =
            currentX
            - touchStartX;

          touchStartX =
            null;

          if (
            Math.abs(
              delta
            ) < 50
          ) {
            return;
          }

          if (
            delta < 0
            && !slide.final
          ) {
            index =
              Math.min(
                slides.length - 1,
                index + 1
              );

            render();
          }

          if (
            delta > 0
            && index > 0
          ) {
            index -= 1;
            render();
          }
        },
        {
          passive: true,
        }
      );
    }


    render();
  }


  function openSop(
    force,
    allowClose
  ) {
    const body =
      document.body.dataset;

    const version =
      body.obSopVersion
      || "beta-sop-v1";

    const current =
      state().snapshot();

    if (
      !force
      && current
        .persistent
        .beta
        .sopAcknowledgedVersion
        === version
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        carousel(
          SOP,
          {
            kind:
              "sop",

            label:
              "Private beta standard operating guide",

            allowClose:
              Boolean(
                allowClose
              ),

            onComplete:
              function () {
                state()
                  .acknowledgeSop(
                    version
                  );

                /*
                  A first-time SOP already includes
                  the current release information.

                  Do not annoy the user with
                  What Changed on the very next login.
                */
                if (
                  body.obWhatsNewVersion
                ) {
                  state()
                    .acknowledgeWhatsNew(
                      body.obWhatsNewVersion
                    );
                }

                resolve(
                  true
                );
              },
          }
        );
      }
    );
  }


  function openWhatsNew(
    force
  ) {
    const body =
      document.body.dataset;

    const version =
      body.obWhatsNewVersion
      || "obux056-060-v1";

    const current =
      state().snapshot();

    if (
      !force
      && current
        .persistent
        .beta
        .whatsNewAcknowledgedVersion
        === version
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        carousel(
          WHATS_NEW,
          {
            kind:
              "whats-new",

            label:
              "What changed in the Observatory",

            allowClose:
              true,

            onComplete:
              function () {
                state()
                  .acknowledgeWhatsNew(
                    version
                  );

                resolve(
                  true
                );
              },
          }
        );
      }
    );
  }


  function checkInMessage(
    values
  ) {
    if (
      values.intent
        === "Just looking"
    ) {
      return (
        "No pressure. "
        + "Let’s look around."
      );
    }

    if (
      values.energy
        === "Low"
    ) {
      return (
        "Got you. "
        + "I’ll keep the important stuff up front."
      );
    }

    if (
      values.pace
        === "Rushed"
      || values.focus
        === "Scattered"
    ) {
      return (
        "I hear you. "
        + "I’ll keep the path simple "
        + "and the evidence close."
      );
    }

    if (
      values.feeling
        === "Focused"
      || values.focus
        === "Locked in"
    ) {
      return (
        "Perfect. "
        + "Let’s see what’s moving."
      );
    }

    return (
      "I’ve got you. "
      + "Let’s see what matters."
    );
  }


  function choiceLabels(
    name,
    values
  ) {
    return values
      .map(
        function (
          value
        ) {
          return `
            <label>
              <input
                type="radio"
                name="${name}"
                value="${escapeHtml(value)}"
              />

              <span>
                ${escapeHtml(value)}
              </span>
            </label>
          `;
        }
      )
      .join(
        ""
      );
  }


  function openCheckIn(
    force
  ) {
    const current =
      state().snapshot();

    if (
      !force
      && current
        .ephemeral
        .checkIn
        .status
        !== "not_started"
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        const inner = `
          <div
            class="ob-checkin"
          >
            <div
              class="ob-checkin-orb"
              aria-hidden="true"
            >
              <span></span>
            </div>

            <span
              class="ob-kicker"
            >
              SOULAANA · SESSION CHECK-IN
            </span>

            <h2>
              Before we get into the market —
              how are you coming in today?
            </h2>

            <p>
              This is optional.
              It can help me shape presentation and pace.
              It never changes market truth,
              rankings,
              or trade decisions.
            </p>

            <form
              id="obCheckInForm"
            >
              <fieldset>
                <legend>
                  How are you feeling?
                </legend>

                <div
                  class="ob-choice-row"
                >
                  ${choiceLabels(
                    "feeling",
                    [
                      "Focused",
                      "Good",
                      "Neutral",
                      "Off",
                      "Overwhelmed",
                    ]
                  )}
                </div>
              </fieldset>

              <fieldset>
                <legend>
                  Energy
                </legend>

                <div
                  class="ob-choice-row"
                >
                  ${choiceLabels(
                    "energy",
                    [
                      "Low",
                      "Steady",
                      "High",
                    ]
                  )}
                </div>
              </fieldset>

              <fieldset>
                <legend>
                  Focus
                </legend>

                <div
                  class="ob-choice-row"
                >
                  ${choiceLabels(
                    "focus",
                    [
                      "Scattered",
                      "Okay",
                      "Locked in",
                    ]
                  )}
                </div>
              </fieldset>

              <fieldset>
                <legend>
                  Your pace
                </legend>

                <div
                  class="ob-choice-row"
                >
                  ${choiceLabels(
                    "pace",
                    [
                      "Rushed",
                      "Normal",
                      "Plenty of time",
                    ]
                  )}
                </div>
              </fieldset>

              <fieldset>
                <legend>
                  What are you here for?
                </legend>

                <div
                  class="ob-choice-row"
                >
                  ${choiceLabels(
                    "intent",
                    [
                      "Just looking",
                      "Research",
                      "Paper practice",
                      "Review",
                      "Active work",
                    ]
                  )}
                </div>
              </fieldset>

              <label
                class="ob-memory-choice"
              >
                <input
                  type="checkbox"
                  name="remember"
                />

                <span>
                  Use this check-in in my private session review.
                  Otherwise it stays session-only
                  and disappears when this OB session closes.
                </span>
              </label>

              <div
                class="ob-checkin-actions"
              >
                <button
                  type="button"
                  class="ob-soft-button"
                  data-checkin-skip
                >
                  Skip for now
                </button>

                <button
                  type="submit"
                  class="ob-primary-button"
                >
                  Continue with Soulaana →
                </button>
              </div>
            </form>
          </div>
        `;

        const shell =
          mountModal(
            inner,
            {
              kind:
                "checkin",

              label:
                "Soulaana session check-in",

              escapeAllowed:
                false,
            }
          );

        shell
          .querySelector(
            "[data-checkin-skip]"
          )
          .addEventListener(
            "click",
            function () {
              state()
                .skipCheckIn();

              closeModal();

              resolve(
                {
                  skipped:
                    true,
                }
              );
            }
          );

        shell
          .querySelector(
            "#obCheckInForm"
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

              const values = {
                feeling:
                  form.get(
                    "feeling"
                  ),

                energy:
                  form.get(
                    "energy"
                  ),

                focus:
                  form.get(
                    "focus"
                  ),

                pace:
                  form.get(
                    "pace"
                  ),

                intent:
                  form.get(
                    "intent"
                  ),
              };

              state()
                .saveCheckIn(
                  values,
                  form.get(
                    "remember"
                  ) === "on"
                );

              const message =
                checkInMessage(
                  values
                );

              shell
                .querySelector(
                  ".ob-checkin"
                )
                .innerHTML = `
                  <div
                    class="ob-checkin-orb"
                    aria-hidden="true"
                  >
                    <span></span>
                  </div>

                  <span
                    class="ob-kicker"
                  >
                    SOULAANA
                  </span>

                  <h2>
                    ${escapeHtml(
                      message
                    )}
                  </h2>

                  <p>
                    Your answers change
                    presentation context only.
                    Market truth stays market truth.
                  </p>

                  <button
                    type="button"
                    class="ob-primary-button"
                    data-checkin-enter
                  >
                    Enter the Observatory →
                  </button>
                `;

              shell
                .querySelector(
                  "[data-checkin-enter]"
                )
                .addEventListener(
                  "click",
                  function () {
                    closeModal();

                    document
                      .body
                      .classList
                      .add(
                        "ob-observatory-awake"
                      );

                    resolve(
                      {
                        skipped:
                          false,

                        values,
                      }
                    );
                  }
                );
            }
          );
      }
    );
  }


  function openResumeChoice() {
    const candidate =
      state()
        .resumeCandidate();

    if (
      !candidate
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        const inner = `
          <div
            class="ob-simple-modal"
          >
            <span
              class="ob-kicker"
            >
              WELCOME BACK
            </span>

            <h2>
              You left something in
              ${escapeHtml(
                candidate.room
                || "your last room"
              )}.
            </h2>

            <p>
              I recovered the last safe OB route.
              This does not imply
              any brokerage action occurred
              while you were away.
            </p>

            <div
              class="ob-modal-actions"
            >
              <button
                type="button"
                class="ob-soft-button"
                data-resume-fresh
              >
                Start fresh
              </button>

              <button
                type="button"
                class="ob-primary-button"
                data-resume-go
              >
                Continue where I left off →
              </button>
            </div>
          </div>
        `;

        const shell =
          mountModal(
            inner,
            {
              kind:
                "resume",

              label:
                "Resume Observatory session",

              escapeAllowed:
                false,
            }
          );

        shell
          .querySelector(
            "[data-resume-fresh]"
          )
          .addEventListener(
            "click",
            function () {
              state()
                .startFresh();

              closeModal();

              resolve(
                false
              );
            }
          );

        shell
          .querySelector(
            "[data-resume-go]"
          )
          .addEventListener(
            "click",
            function () {
              const route =
                candidate.route;

              state()
                .consumeResume();

              closeModal();

              if (
                route
                && route
                  !== global.location.pathname
              ) {
                global.location.assign(
                  route
                );
              }

              resolve(
                true
              );
            }
          );
      }
    );
  }


  function openGuideOffer(
    force
  ) {
    const current =
      state().snapshot();

    if (
      !force
      && current
        .persistent
        .guidedFirstSessionComplete
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        const inner = `
          <div
            class="ob-simple-modal"
          >
            <span
              class="ob-kicker"
            >
              FIRST SESSION
            </span>

            <h2>
              Want me to walk with you the first time?
            </h2>

            <p>
              I’ll guide you through the real
              Dashboard → Market Map → Symbol → Trade → Review flow.
              No proof pages.
              You can stop whenever you want.
            </p>

            <div
              class="ob-modal-actions"
            >
              <button
                type="button"
                class="ob-soft-button"
                data-guide-no
              >
                I got it
              </button>

              <button
                type="button"
                class="ob-primary-button"
                data-guide-yes
              >
                Guide me →
              </button>
            </div>
          </div>
        `;

        const shell =
          mountModal(
            inner,
            {
              kind:
                "guide",

              label:
                "Optional first-session guide",

              escapeAllowed:
                false,
            }
          );

        shell
          .querySelector(
            "[data-guide-no]"
          )
          .addEventListener(
            "click",
            function () {
              state()
                .setGuidance(
                  false,
                  "complete"
                );

              closeModal();

              resolve(
                false
              );
            }
          );

        shell
          .querySelector(
            "[data-guide-yes]"
          )
          .addEventListener(
            "click",
            function () {
              state()
                .setGuidance(
                  true,
                  "dashboard"
                );

              closeModal();

              global.dispatchEvent(
                new CustomEvent(
                  "ob:guide-start"
                )
              );

              resolve(
                true
              );
            }
          );
      }
    );
  }


  function openMultiTabWarning() {
    const lease =
      state()
        .claimTab(
          false
        );

    if (
      !lease.activeOther
    ) {
      return Promise.resolve(
        false
      );
    }

    return new Promise(
      function (
        resolve
      ) {
        const inner = `
          <div
            class="ob-simple-modal"
          >
            <span
              class="ob-kicker"
            >
              SESSION CONTINUITY
            </span>

            <h2>
              OB is already open
              in another recent tab.
            </h2>

            <p>
              Multiple active tabs can make
              mode and session context look inconsistent.
              You can take over here
              or keep the other tab active.
            </p>

            <div
              class="ob-modal-actions"
            >
              <button
                type="button"
                class="ob-soft-button"
                data-tab-other
              >
                Keep the other session
              </button>

              <button
                type="button"
                class="ob-primary-button"
                data-tab-this
              >
                Use this tab instead →
              </button>
            </div>
          </div>
        `;

        const shell =
          mountModal(
            inner,
            {
              kind:
                "multi-tab",

              label:
                "Multiple Observatory tabs",

              escapeAllowed:
                false,
            }
          );

        shell
          .querySelector(
            "[data-tab-other]"
          )
          .addEventListener(
            "click",
            function () {
              closeModal();

              global.location.assign(
                document
                  .body
                  .dataset
                  .obTowerReturn
                || "/tower/return/observatory"
              );

              resolve(
                false
              );
            }
          );

        shell
          .querySelector(
            "[data-tab-this]"
          )
          .addEventListener(
            "click",
            function () {
              state()
                .claimTab(
                  true
                );

              closeModal();

              resolve(
                true
              );
            }
          );
      }
    );
  }


  async function runArrival() {
    try {
      await openMultiTabWarning();

      const body =
        document.body.dataset;

      const parameters =
        new URLSearchParams(
          global.location.search
        );

      const forceFreshArrival =
        parameters.get(
          "ob_arrival"
        ) === "fresh";

      const current =
        state().snapshot();

      const needsSop =
        body.obBeta
          === "true"
        && current
          .persistent
          .beta
          .sopAcknowledgedVersion
          !== body.obSopVersion;

      if (
        forceFreshArrival
      ) {
        await openSop(
          true,
          false
        );
      } else if (
        needsSop
      ) {
        await openSop(
          false,
          false
        );
      } else if (
        body.obBeta
          === "true"
        && current
          .persistent
          .beta
          .whatsNewAcknowledgedVersion
          !== body.obWhatsNewVersion
      ) {
        await openWhatsNew(
          false
        );
      }

      await openCheckIn(
        forceFreshArrival
      );

      if (
        !forceFreshArrival
      ) {
        const resumed =
          await openResumeChoice();

        if (
          resumed
        ) {
          return;
        }
      }

      await openGuideOffer(
        forceFreshArrival
      );

      if (
        forceFreshArrival
        && global.history
        && typeof global.history.replaceState
          === "function"
      ) {
        const cleanUrl =
          new URL(
            global.location.href
          );

        cleanUrl.searchParams.delete(
          "ob_arrival"
        );

        global.history.replaceState(
          {},
          "",
          cleanUrl.pathname
          + cleanUrl.search
          + cleanUrl.hash
        );
      }

      document
        .body
        .classList
        .add(
          "ob-observatory-awake"
        );

      unlockPage();

      global.dispatchEvent(
        new CustomEvent(
          "ob:arrival-complete"
        )
      );
    } catch (
      error
    ) {
      console.error(
        "OB arrival failed safely",
        error
      );

      closeModal();

      document
        .body
        .classList
        .add(
          "ob-arrival-fallback"
        );

      global.dispatchEvent(
        new CustomEvent(
          "ob:arrival-failed",
          {
            detail: {
              message:
                String(
                  error
                ),
            },
          }
        )
      );
    }
  }


  global.OBSessionArrival =
    Object.freeze(
      {
        run:
          runArrival,

        openSop:
          function () {
            return openSop(
              true,
              true
            );
          },

        openWhatsNew:
          function () {
            return openWhatsNew(
              true
            );
          },

        openCheckIn,
      }
    );


  document.addEventListener(
    "DOMContentLoaded",
    function () {
      if (
        !root()
        || !state()
      ) {
        document
          .documentElement
          .classList
          .remove(
            "ob-arrival-booting"
          );

        return;
      }

      runArrival();
    }
  );

})(window);
