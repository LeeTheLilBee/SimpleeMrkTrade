(function () {
  "use strict";

  const PROJECTION =
    window.OBReviewCenterProjection;

  if (!PROJECTION) {
    console.error(
      "Canonical Review Center projection unavailable."
    );
    return;
  }


  const state = {
    filter: "attention",
    records: [],
    selectedId: null,
  };


  // ================================================================================================
  // UTILS
  // ================================================================================================

  function el(id) {
    return document.getElementById(id);
  }


  function obj(value) {
    return (
      value
      && typeof value === "object"
      && !Array.isArray(value)
    ) ? value : {};
  }


  function arr(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function num(value) {
    const parsed = Number(value);

    return Number.isFinite(parsed)
      ? parsed
      : null;
  }


  function txt(value, fallback = "—") {
    return (
      value === undefined
      || value === null
      || value === ""
    ) ? fallback : String(value);
  }


  function esc(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }


  function money(value) {
    const parsed = num(value);

    if (parsed === null) {
      return "Unavailable";
    }

    return new Intl.NumberFormat(
      "en-US",
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
      }
    ).format(parsed);
  }


  function pct(value) {
    const parsed = num(value);

    if (parsed === null) {
      return "Unavailable";
    }

    const sign = parsed > 0
      ? "+"
      : "";

    return `${sign}${parsed.toFixed(1)}%`;
  }


  function duration(minutes) {
    const parsed = num(minutes);

    if (parsed === null) {
      return "Unavailable";
    }

    const rounded =
      Math.max(
        0,
        Math.round(parsed)
      );

    const hours =
      Math.floor(
        rounded / 60
      );

    const mins =
      rounded % 60;

    if (!hours) {
      return `${mins}m`;
    }

    return `${hours}h ${String(mins).padStart(2, "0")}m`;
  }


  function tone(record) {
    if (
      record.process_quality === "POOR"
      || arr(record.rule_violations).length
      || (
        record.negative_dive.time_below_stop_minutes !== null
        && record.negative_dive.time_below_stop_minutes > 0
      )
    ) {
      return "danger";
    }

    if (
      record.process_quality === "NEEDS_REVIEW"
      || record.overtime.overtime === true
      || arr(record.causes).length
    ) {
      return "warn";
    }

    if (
      record.process_quality === "CLEAN"
    ) {
      return "clean";
    }

    return "neutral";
  }


  function needsAttention(record) {
    return (
      tone(record) === "danger"
      || tone(record) === "warn"
      || record.outcome_class === "UNKNOWN"
      || record.process_quality === "UNKNOWN"
    );
  }


  function contractTitle(record) {
    const contract = obj(
      record.contract
    );

    if (contract.contract_symbol) {
      return contract.contract_symbol;
    }

    const pieces = [];

    if (record.symbol) {
      pieces.push(record.symbol);
    }

    if (contract.strike !== null) {
      pieces.push(
        `$${contract.strike}`
      );
    }

    if (contract.right) {
      pieces.push(
        contract.right
      );
    }

    if (contract.expiration) {
      pieces.push(
        contract.expiration
      );
    }

    return pieces.length
      ? pieces.join(" · ")
      : "Trade review";
  }


  function truthLabel(mode) {
    const labels = {
      manual_live: "MANUAL LIVE",
      paper: "PAPER",
      rehearsal: "REHEARSAL",
      proof: "PROOF / UNCLASSIFIED",
      quarantined: "QUARANTINED",
    };

    return labels[mode]
      || String(mode || "UNKNOWN").toUpperCase();
  }


  // ================================================================================================
  // FILTERING
  // ================================================================================================

  function filteredRecords() {
    const records = state.records;

    if (state.filter === "attention") {
      return records.filter(
        needsAttention
      );
    }

    if (state.filter === "official") {
      return records.filter(
        item =>
          item.official_performance
      );
    }

    if (state.filter === "manual_live") {
      return records.filter(
        item =>
          item.truth_mode === "manual_live"
      );
    }

    if (state.filter === "paper") {
      return records.filter(
        item =>
          item.truth_mode === "paper"
      );
    }

    if (state.filter === "practice") {
      return records.filter(
        item =>
          item.truth_mode === "rehearsal"
          || item.truth_mode === "proof"
      );
    }

    return records;
  }


  function selectedRecord() {
    const filtered =
      filteredRecords();

    const selected =
      filtered.find(
        item =>
          item.review_id === state.selectedId
      );

    if (selected) {
      return selected;
    }

    return filtered[0] || null;
  }


  // ================================================================================================
  // SUMMARY
  // ================================================================================================

  function renderSummary() {
    const official =
      state.records.filter(
        item =>
          item.official_performance
      );

    const attention =
      state.records.filter(
        needsAttention
      );

    const overtime =
      state.records.filter(
        item =>
          item.overtime.overtime === true
      );

    const clean =
      state.records.filter(
        item =>
          item.process_quality === "CLEAN"
      );

    el("reviewSummary").innerHTML = `
      <div class="obux-review-stat">
        <span>Reviewed</span>
        <strong>${state.records.length}</strong>
      </div>

      <div class="obux-review-stat">
        <span>Needs attention</span>
        <strong>${attention.length}</strong>
      </div>

      <div class="obux-review-stat">
        <span>Official</span>
        <strong>${official.length}</strong>
      </div>

      <div class="obux-review-stat">
        <span>Overtime</span>
        <strong>${overtime.length}</strong>
      </div>

      <div class="obux-review-stat">
        <span>Clean process</span>
        <strong>${clean.length}</strong>
      </div>
    `;
  }


  // ================================================================================================
  // REVIEW QUEUE
  // ================================================================================================

  function queueCard(record) {
    const active =
      record.review_id === state.selectedId
        ? "active"
        : "";

    const t = tone(record);

    const overtime =
      record.overtime.overtime === true
        ? `<span class="obux-review-queue-alert">
             +${duration(record.overtime.overtime_minutes)} overtime
           </span>`
        : "";

    return `
      <button
        class="obux-review-queue-card ${t} ${active}"
        data-review-id="${esc(record.review_id)}"
      >
        <div class="obux-review-card-top">
          <span class="obux-review-truth ${esc(record.truth_mode)}">
            ${esc(truthLabel(record.truth_mode))}
          </span>

          <span class="obux-review-process ${t}">
            ${esc(record.process_quality)}
          </span>
        </div>

        <strong class="obux-review-symbol">
          ${esc(contractTitle(record))}
        </strong>

        <span class="obux-review-account">
          ${esc(txt(record.mission_account, "Account unavailable"))}
        </span>

        <div class="obux-review-card-bottom">
          <span>
            ${esc(record.outcome_class)}
          </span>

          <span>
            ${esc(
              record.realized_return_pct !== null
                ? pct(record.realized_return_pct)
                : money(record.realized_pnl)
            )}
          </span>
        </div>

        ${overtime}
      </button>
    `;
  }


  function renderQueue() {
    const records =
      filteredRecords();

    const mount =
      el("reviewQueue");

    if (!records.length) {
      mount.innerHTML = `
        <div class="obux-review-empty">
          <strong>No records in this view.</strong>
          <span>
            Review Center will not manufacture example trades.
            When canonical review records arrive, they will appear here.
          </span>
        </div>
      `;

      state.selectedId = null;

      return;
    }

    if (
      !records.some(
        item =>
          item.review_id === state.selectedId
      )
    ) {
      state.selectedId =
        records[0].review_id;
    }

    mount.innerHTML =
      records.map(queueCard).join("");

    mount
      .querySelectorAll(
        "[data-review-id]"
      )
      .forEach(button => {
        button.addEventListener(
          "click",
          () => {
            state.selectedId =
              button.dataset.reviewId;

            renderQueue();
            renderDetail();
          }
        );
      });
  }


  // ================================================================================================
  // NEGATIVE DIVE
  // ================================================================================================

  function metric(label, value, extraClass = "") {
    return `
      <div class="obux-review-metric ${extraClass}">
        <span>${esc(label)}</span>
        <strong>${esc(value)}</strong>
      </div>
    `;
  }


  function renderNegativeDive(record) {
    const neg =
      record.negative_dive;

    const overtime =
      record.overtime;

    return `
      <section class="obux-review-section obux-negative-dive">
        <div class="obux-section-heading">
          <div>
            <span class="obux-eyebrow">
              Negative Dive
            </span>

            <h3>
              What happened below the pretty result?
            </h3>
          </div>

          ${
            overtime.overtime === true
              ? `<span class="obux-danger-chip">
                   OVERTIME +${duration(overtime.overtime_minutes)}
                 </span>`
              : `<span class="obux-muted-chip">
                   ${overtime.overtime === false
                     ? "WITHIN HOLD WINDOW"
                     : "HOLD WINDOW UNKNOWN"}
                 </span>`
          }
        </div>

        <div class="obux-review-metrics-grid">
          ${metric(
            "Planned hold",
            duration(
              overtime.intended_hold_minutes
            )
          )}

          ${metric(
            "Actual hold",
            duration(
              overtime.actual_hold_minutes
            )
          )}

          ${metric(
            "Overtime",
            duration(
              overtime.overtime_minutes
            ),
            overtime.overtime === true
              ? "danger"
              : ""
          )}

          ${metric(
            "MAE",
            pct(
              neg.mae_pct
            ),
            neg.mae_pct !== null
              && neg.mae_pct < 0
                ? "danger"
                : ""
          )}

          ${metric(
            "MFE",
            pct(
              neg.mfe_pct
            )
          )}

          ${metric(
            "Deepest drawdown",
            pct(
              neg.deepest_drawdown_pct
            ),
            neg.deepest_drawdown_pct !== null
              ? "danger"
              : ""
          )}

          ${metric(
            "Time negative",
            duration(
              neg.time_negative_minutes
            )
          )}

          ${metric(
            "Time under stop",
            duration(
              neg.time_below_stop_minutes
            ),
            neg.time_below_stop_minutes !== null
              && neg.time_below_stop_minutes > 0
                ? "danger"
                : ""
          )}
        </div>

        <div class="obux-review-truth-note">
          Missing excursion metrics are shown as
          <strong>Unavailable</strong>.
          Review Center does not estimate MAE, MFE, drawdown or
          negative duration from the final result alone.
        </div>
      </section>
    `;
  }


  // ================================================================================================
  // CAUSES / LESSONS
  // ================================================================================================

  function renderCauses(record) {
    const causes =
      arr(record.causes);

    const violations =
      arr(record.rule_violations);

    return `
      <section class="obux-review-section">
        <span class="obux-eyebrow">
          Why it went sideways
        </span>

        <h3>
          Cause + discipline review
        </h3>

        ${
          causes.length
            ? `
              <div class="obux-cause-grid">
                ${causes.map(
                  cause => `
                    <div class="obux-cause-chip">
                      <span>●</span>
                      ${esc(cause.label)}
                    </div>
                  `
                ).join("")}
              </div>
            `
            : `
              <div class="obux-review-empty compact">
                No evidence-supported cause classification yet.
              </div>
            `
        }

        ${
          violations.length
            ? `
              <div class="obux-violation-box">
                <strong>
                  Rule violations
                </strong>

                ${violations.map(
                  violation => `
                    <span>
                      ${esc(violation)}
                    </span>
                  `
                ).join("")}
              </div>
            `
            : ""
        }
      </section>
    `;
  }


  function lessonRow(label, value) {
    return `
      <div class="obux-lesson-row">
        <span>${esc(label)}</span>
        <strong>
          ${esc(txt(value, "Not recorded yet"))}
        </strong>
      </div>
    `;
  }


  function renderLesson(record) {
    const lesson =
      obj(record.lesson);

    return `
      <section class="obux-review-section obux-lesson-section">
        <span class="obux-eyebrow">
          What changes
        </span>

        <h3>
          Turn the trade into a rule.
        </h3>

        <div class="obux-lesson-grid">
          ${lessonRow(
            "What worked",
            lesson.what_worked
          )}

          ${lessonRow(
            "What failed",
            lesson.what_failed
          )}

          ${lessonRow(
            "Missed warning",
            lesson.missed_warning
          )}

          ${lessonRow(
            "Repeat",
            lesson.what_to_repeat
          )}

          ${lessonRow(
            "Avoid",
            lesson.what_to_avoid
          )}

          ${lessonRow(
            "Best next rule",
            lesson.best_next_rule
          )}
        </div>

        <div class="obux-owner-note">
          <span>Owner note</span>
          <p>
            ${esc(
              txt(
                lesson.owner_notes,
                "No owner note recorded yet."
              )
            )}
          </p>
        </div>
      </section>
    `;
  }


  // ================================================================================================
  // LIFECYCLE REPLAY
  // ================================================================================================

  function renderTimeline(record) {
    const timeline =
      arr(record.lifecycle);

    if (!timeline.length) {
      return `
        <div class="obux-review-empty compact">
          No canonical lifecycle events were supplied for this record.
        </div>
      `;
    }

    return `
      <div class="obux-review-timeline">
        ${timeline.map(
          (item, index) => {
            const safe = obj(item);

            return `
              <div class="obux-timeline-node">
                <div class="obux-timeline-number">
                  ${index + 1}
                </div>

                <div>
                  <strong>
                    ${esc(
                      txt(
                        safe.label,
                        safe.event_type || "Event"
                      )
                    )}
                  </strong>

                  <span>
                    ${esc(
                      txt(
                        safe.timestamp,
                        safe.time || safe.created_at || "Time unavailable"
                      )
                    )}
                  </span>

                  ${
                    safe.result
                      ? `<p>${esc(safe.result)}</p>`
                      : ""
                  }
                </div>
              </div>
            `;
          }
        ).join("")}
      </div>
    `;
  }


  // ================================================================================================
  // SOULAANA
  // ================================================================================================

  function soulaana(record) {
    const bits = [];

    bits.push(
      `${record.outcome_class} is the money result.`
    );

    bits.push(
      `${record.process_quality} is the process result.`
    );

    if (
      record.outcome_class === "WIN"
      && (
        record.process_quality === "POOR"
        || record.process_quality === "NEEDS_REVIEW"
      )
    ) {
      bits.push(
        "Do not confuse getting paid with trading clean. A profitable violation still gets reviewed."
      );
    }

    if (
      record.outcome_class === "LOSS"
      && record.process_quality === "CLEAN"
    ) {
      bits.push(
        "A clean loss is not the same thing as a bad decision. The system can do the right thing and still lose."
      );
    }

    if (
      record.overtime.overtime === true
    ) {
      bits.push(
        `This position exceeded its intended hold window by ${duration(record.overtime.overtime_minutes)}.`
      );
    }

    if (
      record.negative_dive.time_below_stop_minutes !== null
      && record.negative_dive.time_below_stop_minutes > 0
    ) {
      bits.push(
        `It remained beyond the recorded stop boundary for ${duration(record.negative_dive.time_below_stop_minutes)}.`
      );
    }

    if (arr(record.causes).length) {
      bits.push(
        `Evidence-backed causes: ${record.causes.map(item => item.label).join(", ")}.`
      );
    }

    if (
      !arr(record.causes).length
      && record.process_quality === "UNKNOWN"
    ) {
      bits.push(
        "I do not have enough source evidence to blame the market, the system, or you. That stays unknown until the record supports an answer."
      );
    }

    return bits.join(" ");
  }


  // ================================================================================================
  // HERO REVIEW
  // ================================================================================================

  function renderDetail() {
    const record =
      selectedRecord();

    const mount =
      el("reviewHero");

    if (!record) {
      mount.innerHTML = `
        <div class="obux-review-empty hero">
          <strong>
            Nothing selected.
          </strong>

          <span>
            Review Center is waiting for canonical review truth.
          </span>
        </div>
      `;

      return;
    }

    state.selectedId =
      record.review_id;

    const contract =
      obj(record.contract);

    const resultValue =
      record.realized_return_pct !== null
        ? pct(record.realized_return_pct)
        : money(record.realized_pnl);

    mount.innerHTML = `
      <article class="obux-review-hero-card">

        <header class="obux-review-hero-header">
          <div>
            <div class="obux-review-kickers">
              <span class="obux-review-truth ${esc(record.truth_mode)}">
                ${esc(truthLabel(record.truth_mode))}
              </span>

              <span class="obux-review-source">
                ${esc(record.source_name)}
              </span>
            </div>

            <h2>
              ${esc(contractTitle(record))}
            </h2>

            <p>
              ${esc(
                txt(
                  record.mission_account,
                  "Mission account unavailable"
                )
              )}
              ${
                record.strategy
                  ? ` · ${esc(record.strategy)}`
                  : ""
              }
            </p>
          </div>

          <div class="obux-result-stack">
            <div>
              <span>Outcome</span>
              <strong class="${record.outcome_class.toLowerCase()}">
                ${esc(record.outcome_class)}
              </strong>
            </div>

            <div>
              <span>Result</span>
              <strong>
                ${esc(resultValue)}
              </strong>
            </div>

            <div>
              <span>Process</span>
              <strong class="${tone(record)}">
                ${esc(record.process_quality)}
              </strong>
            </div>
          </div>
        </header>

        <section class="obux-soulaana-review">
          <div class="obux-soulaana-mark">
            S
          </div>

          <div>
            <span>Soulaana</span>
            <p>
              ${esc(soulaana(record))}
            </p>
          </div>
        </section>

        <section class="obux-review-section">
          <div class="obux-section-heading">
            <div>
              <span class="obux-eyebrow">
                Trade replay
              </span>

              <h3>
                How we got here
              </h3>
            </div>

            ${
              contract.contract_symbol
                ? `
                  <span class="obux-contract-pill">
                    ${esc(contract.contract_symbol)}
                  </span>
                `
                : ""
            }
          </div>

          ${renderTimeline(record)}
        </section>

        <section class="obux-review-section">
          <span class="obux-eyebrow">
            Entry → Exit
          </span>

          <div class="obux-review-metrics-grid">
            ${metric(
              "Planned entry",
              money(
                record.entry.planned_price
              )
            )}

            ${metric(
              "Actual entry",
              money(
                record.entry.actual_price
              )
            )}

            ${metric(
              "Stop",
              money(
                record.exit.stop
              )
            )}

            ${metric(
              "Planned exit",
              money(
                record.exit.planned_price
              )
            )}

            ${metric(
              "Actual exit",
              money(
                record.exit.actual_price
              )
            )}

            ${metric(
              "Exit reason",
              txt(
                record.exit.reason,
                "Unavailable"
              )
            )}
          </div>
        </section>

        ${
          contract.contract_symbol
          || record.premium.entry_premium !== null
          || record.premium.exit_premium !== null
            ? `
              <section class="obux-review-section">
                <span class="obux-eyebrow">
                  Contract economics
                </span>

                <div class="obux-review-metrics-grid">
                  ${metric(
                    "Contract",
                    txt(
                      contract.contract_symbol,
                      contractTitle(record)
                    )
                  )}

                  ${metric(
                    "Entry premium",
                    money(
                      record.premium.entry_premium
                    )
                  )}

                  ${metric(
                    "Exit premium",
                    money(
                      record.premium.exit_premium
                    )
                  )}

                  ${metric(
                    "Contracts",
                    txt(
                      record.premium.contracts,
                      "Unavailable"
                    )
                  )}

                  ${metric(
                    "Premium P&L",
                    money(
                      record.premium.premium_pnl
                    )
                  )}

                  ${metric(
                    "Premium return",
                    pct(
                      record.premium.premium_return_pct
                    )
                  )}
                </div>
              </section>
            `
            : ""
        }

        ${renderNegativeDive(record)}

        ${renderCauses(record)}

        ${renderLesson(record)}

        <footer class="obux-review-footer">
          <div>
            <span>
              REVIEW ID
            </span>
            <strong>
              ${esc(record.review_id)}
            </strong>
          </div>

          <div>
            <span>
              OFFICIAL PERFORMANCE
            </span>
            <strong>
              ${record.official_performance
                ? "YES"
                : "NO"}
            </strong>
          </div>

          <div>
            <span>
              LIVE AUTO
            </span>
            <strong>
              LOCKED
            </strong>
          </div>
        </footer>
      </article>
    `;
  }


  // ================================================================================================
  // FILTER BUTTONS
  // ================================================================================================

  function wireFilters() {
    document
      .querySelectorAll(
        "[data-review-filter]"
      )
      .forEach(button => {
        button.addEventListener(
          "click",
          () => {
            state.filter =
              button.dataset.reviewFilter;

            document
              .querySelectorAll(
                "[data-review-filter]"
              )
              .forEach(item =>
                item.classList.toggle(
                  "active",
                  item === button
                )
              );

            state.selectedId = null;

            renderQueue();
            renderDetail();
          }
        );
      });
  }


  // ================================================================================================
  // RENDER
  // ================================================================================================

  function render() {
    renderSummary();
    renderQueue();
    renderDetail();
  }


  async function boot() {
    wireFilters();

    const loading =
      el("reviewLoading");

    try {
      const snapshot =
        await PROJECTION.refresh();

      state.records =
        arr(snapshot.records);

      if (loading) {
        loading.remove();
      }

      render();

    } catch (error) {
      if (loading) {
        loading.innerHTML = `
          <strong>
            Review Center could not load canonical review data.
          </strong>

          <span>
            ${esc(
              error
              && error.message
                ? error.message
                : String(error)
            )}
          </span>
        `;
      }
    }
  }


  window.addEventListener(
    "ob:review-center-projection-updated",
    event => {
      const detail =
        obj(event.detail);

      state.records =
        arr(detail.records);

      render();
    }
  );


  document.addEventListener(
    "DOMContentLoaded",
    boot
  );


  window.OBReviewCenter =
    Object.freeze({
      refresh: boot,
      getState: () => ({
        ...state,
        records: [...state.records],
      }),
    });


  window.dispatchEvent(
    new CustomEvent(
      "ob:obux046-050-review-center-ready",
      {
        detail: {
          canonicalReviewCenter: true,
          negativeDiveEnabled: true,
          overtimeReviewEnabled: true,
          fakePerformanceFallbackEnabled: false,
          liveAutoLocked: true,
        },
      }
    )
  );
})();
