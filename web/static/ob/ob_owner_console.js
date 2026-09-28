(function () {
  "use strict";

  const API =
    window.OBOwnerConsoleProjection;

  if (!API) {
    console.error(
      "Owner Console projection unavailable."
    );

    return;
  }


  let state =
    API.snapshot();


  // ================================================================================================
  // HELPERS
  // ================================================================================================

  function el(id) {
    return document.getElementById(id);
  }


  function obj(value) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    )
      ? value
      : {};
  }


  function arr(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function txt(value, fallback = "Unavailable") {
    return (
      value === undefined
      || value === null
      || value === ""
    )
      ? fallback
      : String(value);
  }


  function esc(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }


  function statusNode(
    node,
    value
  ) {
    if (!node) {
      return;
    }

    node.textContent =
      txt(
        value,
        "UNKNOWN"
      );

    node.setAttribute(
      "data-status",
      txt(
        value,
        "UNKNOWN"
      )
    );
  }


  function numberText(value) {
    return (
      value === null
      || value === undefined
    )
      ? "Unavailable"
      : String(value);
  }


  // ================================================================================================
  // TOP QUESTIONS
  // ================================================================================================

  function renderQuestions() {
    const health =
      obj(
        state.system_health
      );

    const attention =
      arr(
        state.attention
      );

    const diagnostics =
      obj(
        state.diagnostics
      );

    const audit =
      obj(
        state.source_audit
      );

    statusNode(
      el("oboc-overall-chip"),
      health.overall
    );

    statusNode(
      el("oboc-health-answer"),
      health.overall
    );

    el("oboc-health-detail").textContent =
      `Market ${txt(health.market_truth, "UNKNOWN")} · Rooms ${txt(health.room_chain, "UNKNOWN")}`;


    statusNode(
      el("oboc-money-answer"),
      "GUARDED"
    );

    el("oboc-money-detail").textContent =
      "Owner Console cannot read or execute at the broker. Live Auto remains locked.";


    el("oboc-attention-answer").textContent =
      String(
        attention.length
      );

    el("oboc-attention-detail").textContent =
      attention.length
        ? "Owner-facing issues need review."
        : "No source-backed owner attention currently surfaced.";


    const degraded =
      [
        diagnostics.status,
        audit.status,
        ...arr(state.rooms).map(
          room =>
            room.status
        ),
      ]
        .filter(
          status =>
            status === "DEGRADED"
            ||
            status === "GUARDED"
        )
        .length;

    el("oboc-degraded-answer").textContent =
      String(
        degraded
      );

    el("oboc-degraded-detail").textContent =
      degraded
        ? "Guarded or degraded truth is visible below."
        : "No guarded/degraded source-backed state currently reported.";
  }


  // ================================================================================================
  // OWNER ATTENTION
  // ================================================================================================

  function renderAttention() {
    const mount =
      el(
        "oboc-attention-list"
      );

    const items =
      arr(
        state.attention
      );

    el(
      "oboc-attention-count"
    ).textContent =
      String(
        items.length
      );

    if (!items.length) {
      mount.innerHTML = `
        <div class="oboc-empty">
          No source-backed owner attention is currently surfaced.
          Unknown information stays unknown.
        </div>
      `;

      return;
    }

    mount.innerHTML =
      items
        .map(
          item => `
            <article
              class="oboc-attention-card ${esc(
                String(
                  item.severity
                  || "UNKNOWN"
                )
                  .toLowerCase()
              )}"
            >
              <strong>
                ${esc(
                  txt(
                    item.title,
                    "Owner review"
                  )
                )}
              </strong>

              <span>
                ${esc(
                  txt(
                    item.detail,
                    "Details unavailable."
                  )
                )}
              </span>

              <small>
                SOURCE · ${esc(
                  txt(
                    item.source,
                    "unknown"
                  )
                )}
              </small>
            </article>
          `
        )
        .join("");
  }


  // ================================================================================================
  // SYSTEM HEALTH
  // ================================================================================================

  function healthCard(
    label,
    status,
    detail
  ) {
    return `
      <article class="oboc-health-card">
        <span>
          ${esc(label)}
        </span>

        <strong
          data-status="${esc(
            txt(
              status,
              "UNKNOWN"
            )
          )}"
        >
          ${esc(
            txt(
              status,
              "UNKNOWN"
            )
          )}
        </strong>

        <small>
          ${esc(
            txt(
              detail,
              "No additional source truth."
            )
          )}
        </small>
      </article>
    `;
  }


  function renderHealth() {
    const health =
      obj(
        state.system_health
      );

    const review =
      obj(
        state.review
      );

    const readiness =
      obj(
        state.readiness
      );

    const diagnostics =
      obj(
        state.diagnostics
      );

    const audit =
      obj(
        state.source_audit
      );

    const mount =
      el(
        "oboc-health-grid"
      );

    mount.innerHTML =
      [
        healthCard(
          "Market truth",
          health.market_truth,
          diagnostics.display_label
        ),

        healthCard(
          "Source truth",
          health.source_truth,
          audit.trust_label
        ),

        healthCard(
          "Room chain",
          health.room_chain,
          "Market → Symbol → Trade → Review → Owner"
        ),

        healthCard(
          "Review attention",
          health.review_attention,
          review.attention === null
            ? "Review count unavailable"
            : `${review.attention} need attention`
        ),

        healthCard(
          "Readiness",
          health.readiness,
          readiness.label
        ),

        healthCard(
          "Safety gates",
          "LOCKED",
          "Broker execution disabled · Live Auto locked"
        ),
      ]
        .join("");

    statusNode(
      el(
        "oboc-system-state"
      ),
      health.overall
    );
  }


  // ================================================================================================
  // MISSION ACCOUNTS
  // ================================================================================================

  const MISSION_LABELS = {
    personal:
      "Personal",

    trust:
      "Trust",

    business:
      "Simplee World",

    atm:
      "ATM",

    apartment:
      "Apartment",

    proof:
      "Proof / Demo",
  };


  function renderMissions() {
    const mount =
      el(
        "oboc-mission-list"
      );

    const missions =
      arr(
        state.missions
      );

    mount.innerHTML =
      missions
        .map(
          mission => `
            <article
              class="oboc-mission-row ${
                mission.selected
                  ? "selected"
                  : ""
              }"
            >
              <div>
                <strong>
                  ${esc(
                    MISSION_LABELS[
                      mission.id
                    ]
                    ||
                    mission.id
                  )}
                </strong>

                <span>
                  ${mission.selected
                    ? "Selected mission"
                    : "Mission policy available"}
                </span>

                <small>
                  Live balance: unavailable
                </small>
              </div>

              <strong
                data-status="UNKNOWN"
              >
                UNKNOWN
              </strong>
            </article>
          `
        )
        .join("");
  }


  // ================================================================================================
  // SOURCE TRUTH
  // ================================================================================================

  function sourceCard(
    label,
    value
  ) {
    return `
      <article class="oboc-source-card">
        <span>
          ${esc(label)}
        </span>

        <strong>
          ${esc(
            txt(
              value,
              "Unavailable"
            )
          )}
        </strong>
      </article>
    `;
  }


  function renderSources() {
    const diagnostics =
      obj(
        state.diagnostics
      );

    const audit =
      obj(
        state.source_audit
      );

    const trust =
      obj(
        state.trust
      );

    statusNode(
      el(
        "oboc-source-chip"
      ),
      audit.status
    );

    el(
      "oboc-source-grid"
    ).innerHTML =
      [
        sourceCard(
          "Feed status",
          diagnostics.status
        ),

        sourceCard(
          "Freshness score",
          diagnostics.freshness_score
        ),

        sourceCard(
          "Trust label",
          trust.label
        ),

        sourceCard(
          "Present sources",
          audit.summary
            ? audit.summary.present
            : null
        ),

        sourceCard(
          "Missing",
          audit.summary
            ? audit.summary.missing
            : null
        ),

        sourceCard(
          "Fallback only",
          audit.summary
            ? audit.summary.fallback_only
            : null
        ),
      ]
        .join("");
  }


  // ================================================================================================
  // ROOM CHAIN
  // ================================================================================================

  function renderRooms() {
    const mount =
      el(
        "oboc-room-chain"
      );

    const rooms =
      arr(
        state.rooms
      );

    mount.innerHTML =
      rooms
        .map(
          (
            room,
            index
          ) => `
            <article class="oboc-room-card">
              <span>
                ${index + 1}
              </span>

              <strong>
                ${esc(
                  txt(
                    room.label,
                    room.id
                  )
                )}
              </strong>

              <strong
                data-status="${esc(
                  txt(
                    room.status,
                    "UNKNOWN"
                  )
                )}"
              >
                ${esc(
                  txt(
                    room.status,
                    "UNKNOWN"
                  )
                )}
              </strong>

              <small>
                ${esc(
                  txt(
                    room.source,
                    "Source unknown"
                  )
                )}
              </small>
            </article>
          `
        )
        .join("");
  }


  // ================================================================================================
  // SOURCE DRAWER
  // ================================================================================================

  function renderDrawer() {
    const mount =
      el(
        "oboc-source-detail-list"
      );

    const diagnostics =
      obj(
        state.diagnostics
      );

    const audit =
      obj(
        state.source_audit
      );

    const files =
      arr(
        audit.files
      ).length
        ? arr(
            audit.files
          )
        : arr(
            diagnostics.files
          );

    if (!files.length) {
      mount.innerHTML = `
        <div class="oboc-empty">
          No canonical source-detail rows are available.
        </div>
      `;

      return;
    }

    mount.innerHTML =
      files
        .map(
          file => `
            <article class="oboc-source-detail-row">
              <strong>
                ${esc(
                  txt(
                    file.name,
                    "unknown source"
                  )
                )}
              </strong>

              <span>
                Status:
                ${esc(
                  txt(
                    file.status,
                    "unknown"
                  )
                )}
              </span>

              <span>
                Safe to display:
                ${esc(
                  txt(
                    file.safe_to_display,
                    "unknown"
                  )
                )}
              </span>

              <span>
                Age:
                ${
                  file.age_minutes === null
                  ||
                  file.age_minutes === undefined
                    ? "Unavailable"
                    : `${esc(file.age_minutes)}m`
                }
              </span>
            </article>
          `
        )
        .join("");
  }


  function wireDrawer() {
    const button =
      el(
        "oboc-source-details-button"
      );

    const drawer =
      el(
        "oboc-source-drawer"
      );

    const close =
      el(
        "oboc-source-drawer-close"
      );

    button.addEventListener(
      "click",
      function () {
        renderDrawer();

        drawer.hidden =
          false;
      }
    );

    close.addEventListener(
      "click",
      function () {
        drawer.hidden =
          true;
      }
    );
  }


  // ================================================================================================
  // SOULAANA
  // ================================================================================================

  function soulaanaLine() {
    const health =
      obj(
        state.system_health
      );

    const attention =
      arr(
        state.attention
      );

    const diagnostics =
      obj(
        state.diagnostics
      );

    if (
      diagnostics.fallback_active
    ) {
      return (
        "OB is operating with guarded fallback diagnostics. "
        +
        "I will not call that healthy until the canonical source confirms it."
      );
    }

    if (
      health.overall
      === "DEGRADED"
    ) {
      return (
        "Something in the system truth is degraded. "
        +
        "The attention queue shows what needs review before you rely on it."
      );
    }

    if (
      attention.length
    ) {
      return (
        `${attention.length} owner item`
        +
        (
          attention.length === 1
            ? ""
            : "s"
        )
        +
        " need review. Nothing here creates execution permission."
      );
    }

    if (
      health.overall
      === "HEALTHY"
    ) {
      return (
        "The available source-backed checks are healthy. "
        +
        "Broker execution and Live Auto remain locked."
      );
    }

    return (
      "Some system truth is still unknown. "
      +
      "Unknown stays unknown instead of being dressed up as healthy."
    );
  }


  function renderSoulaana() {
    el(
      "oboc-soulaana-line"
    ).textContent =
      soulaanaLine();
  }


  // ================================================================================================
  // MASTER RENDER
  // ================================================================================================

  function render() {
    renderQuestions();
    renderAttention();
    renderHealth();
    renderMissions();
    renderSources();
    renderRooms();
    renderSoulaana();
  }


  function refresh() {
    state =
      API.refresh();

    render();
  }


  // ================================================================================================
  // BOOT
  // ================================================================================================

  function boot() {
    state =
      API.refresh();

    wireDrawer();
    render();

    setTimeout(
      refresh,
      1800
    );

    setTimeout(
      refresh,
      3400
    );
  }


  window.addEventListener(
    "ob:owner-console-truth-updated",
    function (event) {
      if (
        event
        &&
        event.detail
      ) {
        state =
          event.detail;

        render();
      }
    }
  );


  if (
    document.readyState
    === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      boot,
      {
        once: true,
      }
    );
  }

  else {
    boot();
  }


  window.OBOwnerConsole =
    Object.freeze({
      refresh,

      snapshot() {
        return state;
      },
    });


  window.dispatchEvent(
    new CustomEvent(
      "ob:obux051-055-owner-console-ready",
      {
        detail: {
          canonicalOwnerConsole:
            true,

          sourceBacked:
            true,

          fakeHealthFallback:
            false,

          fakeBalanceFallback:
            false,

          brokerExecution:
            false,

          liveAutoLocked:
            true,
        },
      }
    )
  );
})();
