"""ADHD-friendly Clouds owner-command renderer.

This module is presentation-only. It receives the canonical Clouds
OwnerCommandExperience object and renders explanation-first cards.
"""

from __future__ import annotations

from html import escape


def _value(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def render_owner_command_experience(
    *,
    experience,
    page_factory,
    canonical_title: str,
    canonical_subtitle: str,
    resume: str = "",
    returned_from: str = "",
) -> str:
    title = str(_value(experience, "title", canonical_title) or canonical_title)
    subtitle = str(
        _value(experience, "subtitle", canonical_subtitle)
        or canonical_subtitle
    )

    hero = _value(experience, "hero")
    greeting = str(
        _value(hero, "greeting", "Good to see you.")
        or "Good to see you."
    )
    headline = str(
        _value(
            hero,
            "headline",
            "Here is what needs you, what I am watching, and what can wait.",
        )
        or ""
    )
    explanation = str(
        _value(
            hero,
            "explanation",
            (
                "Soulaana leads with meaning first. "
                "Details stay tucked away until you ask for them."
            ),
        )
        or ""
    )

    needs_count = int(_value(hero, "needs_you_count", 0) or 0)
    watching_count = int(_value(hero, "watching_count", 0) or 0)
    quiet_count = int(_value(hero, "quiet_count", 0) or 0)

    resume = str(resume or "").strip()
    returned_from = str(returned_from or "").strip()

    return_banner = ""

    if resume or returned_from:
        source_label = (
            returned_from.replace("_", " ").title()
            if returned_from
            else "your app"
        )

        return_banner = f"""
        <section class="resume-banner">
          <div>
            <strong>Back in Clouds.</strong>
            <span>
              I kept your place from {escape(source_label)}.
              I will only clear the item when its source says it actually changed.
            </span>
          </div>
          <a href="/tower/ecosystem/lines">Check all lines</a>
        </section>
        """

    def chip_html(chip):
        label = str(_value(chip, "label", "Status") or "Status")
        value = str(_value(chip, "value", "unknown") or "unknown")

        return (
            '<span class="chip">'
            + escape(label)
            + " · "
            + escape(value)
            + "</span>"
        )

    def card_html(card):
        source_id = str(_value(card, "source_id", "") or "")
        source_label = str(
            _value(card, "source_label", source_id)
            or source_id
        )
        card_title = str(
            _value(card, "title", source_label)
            or source_label
        )
        message = str(
            _value(
                card,
                "soulaana_message",
                (
                    "I am keeping this visible until "
                    "the source tells me otherwise."
                ),
            )
            or ""
        )

        why = str(_value(card, "why_it_matters", "") or "")
        attention = str(
            _value(card, "what_needs_attention", "")
            or ""
        )
        wait = str(_value(card, "what_can_wait", "") or "")
        next_step = str(_value(card, "owner_next_step", "") or "")
        chips = _as_list(_value(card, "chips", []))

        navigation = _value(card, "navigation")
        route = str(
            _value(navigation, "route_reference", "")
            or ""
        )
        nav_label = str(
            _value(navigation, "label", "Open through Tower")
            or "Open through Tower"
        )
        requires_step_up = bool(
            _value(navigation, "requires_step_up", False)
        )

        is_resume = bool(
            resume
            and source_id
            and source_id.replace("_", "-") in resume
        )

        action = ""

        if route:
            step_note = " · step-up" if requires_step_up else ""

            action = f"""
            <a class="button primary" href="{escape(route)}">
              {escape(nav_label)}{escape(step_note)}
            </a>
            """

        return f"""
        <article
          class="focus-card {'resume-focus' if is_resume else ''}"
          data-source="{escape(source_id)}"
        >
          <div class="focus-top">
            <div>
              <div class="source-kicker">
                {escape(source_label)}
              </div>
              <h3>{escape(card_title)}</h3>
            </div>
            <span class="state-dot" aria-hidden="true"></span>
          </div>

          <p class="soulaana-line">{escape(message)}</p>

          <div class="chip-row compact">
            {''.join(chip_html(chip) for chip in chips)}
          </div>

          <div class="actions">
            {action}
            <a class="button" href="/tower/ecosystem/lines">
              Line status
            </a>
          </div>

          <details>
            <summary>Soulaana explains</summary>
            <div class="explain-grid">
              <div>
                <strong>Why it matters</strong>
                <p>{escape(why)}</p>
              </div>
              <div>
                <strong>Needs attention</strong>
                <p>{escape(attention)}</p>
              </div>
              <div>
                <strong>Can wait</strong>
                <p>{escape(wait)}</p>
              </div>
              <div>
                <strong>Next move</strong>
                <p>{escape(next_step)}</p>
              </div>
            </div>
          </details>
        </article>
        """

    sections = _as_list(_value(experience, "sections", []))
    section_html = []

    for section in sections:
        section_id = str(
            _value(section, "section_id", "section")
            or "section"
        )
        section_title = str(
            _value(section, "title", "Focus")
            or "Focus"
        )
        intro = str(
            _value(section, "soulaana_intro", "")
            or ""
        )
        cards = _as_list(_value(section, "cards", []))
        collapsed = bool(
            _value(section, "collapsed_by_default", False)
        )

        if not cards:
            continue

        cards_markup = "".join(
            card_html(card)
            for card in cards
        )

        if collapsed:
            section_html.append(
                f"""
                <details
                  class="lane collapsed-lane"
                  id="{escape(section_id)}"
                >
                  <summary>
                    <span>{escape(section_title)}</span>
                    <small>{len(cards)} items · tucked away</small>
                  </summary>
                  <p class="lane-intro">{escape(intro)}</p>
                  <div class="focus-grid">{cards_markup}</div>
                </details>
                """
            )

        else:
            section_html.append(
                f"""
                <section class="lane" id="{escape(section_id)}">
                  <div class="lane-head">
                    <div>
                      <div class="lane-title">
                        {escape(section_title)}
                      </div>
                      <p>{escape(intro)}</p>
                    </div>
                    <span class="lane-count">
                      {len(cards)}
                    </span>
                  </div>
                  <div class="focus-grid">{cards_markup}</div>
                </section>
                """
            )

    if not section_html:
        section_html.append(
            """
            <section class="lane">
              <div class="lane-head">
                <div>
                  <div class="lane-title">
                    Nothing is shouting at you.
                  </div>
                  <p>
                    Clouds could not load the current card set,
                    so I left the system fail-closed instead of inventing work.
                  </p>
                </div>
              </div>
            </section>
            """
        )

    style = """
    <style id="clouds-adhd-owner-command-v2">
      .resume-banner {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:14px;
        margin:0 0 16px;
        padding:14px 16px;
        border:1px solid rgba(158,240,192,.28);
        border-radius:18px;
        background:rgba(32,75,53,.18);
      }

      .resume-banner strong {
        display:block;
        color:var(--good);
        margin-bottom:4px;
      }

      .resume-banner span {
        color:var(--muted);
      }

      .resume-banner a {
        color:var(--gold);
        font-weight:900;
        white-space:nowrap;
        text-decoration:none;
      }

      .command-rail {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:10px;
        margin-top:20px;
      }

      .command-stat {
        padding:14px;
        border:1px solid var(--line);
        border-radius:17px;
        background:rgba(255,255,255,.045);
      }

      .command-stat strong {
        display:block;
        font-size:1.65rem;
        line-height:1;
      }

      .command-stat span {
        color:var(--muted);
        font-size:.78rem;
      }

      .lane {
        margin-top:16px;
        padding:20px;
        border:1px solid var(--line);
        border-radius:24px;
        background:rgba(18,15,31,.74);
      }

      .lane-head {
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:16px;
      }

      .lane-head p,
      .lane-intro {
        margin:5px 0 0;
      }

      .lane-title {
        font-size:1.05rem;
        font-weight:950;
        letter-spacing:.08em;
        text-transform:uppercase;
        color:var(--gold);
      }

      .lane-count {
        min-width:34px;
        height:34px;
        display:grid;
        place-items:center;
        border:1px solid var(--line);
        border-radius:999px;
        color:var(--violet);
        font-weight:950;
      }

      .collapsed-lane > summary {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:14px;
        list-style:none;
      }

      .collapsed-lane > summary small {
        color:var(--muted);
        font-weight:700;
      }

      .focus-grid {
        display:grid;
        grid-template-columns:
          repeat(auto-fit,minmax(250px,1fr));
        gap:12px;
        margin-top:14px;
      }

      .focus-card {
        padding:17px;
        border:1px solid var(--line);
        border-radius:19px;
        background:rgba(35,27,56,.76);
      }

      .focus-card.resume-focus {
        border-color:rgba(158,240,192,.55);
        box-shadow:
          0 0 0 2px rgba(158,240,192,.08);
      }

      .focus-top {
        display:flex;
        justify-content:space-between;
        gap:12px;
      }

      .focus-top h3 {
        margin:3px 0 0;
        font-size:1.15rem;
      }

      .source-kicker {
        color:var(--violet);
        font-size:.7rem;
        font-weight:950;
        letter-spacing:.12em;
        text-transform:uppercase;
      }

      .state-dot {
        width:10px;
        height:10px;
        border-radius:999px;
        background:var(--gold);
        box-shadow:
          0 0 18px rgba(245,207,122,.55);
        margin-top:4px;
      }

      .soulaana-line {
        color:var(--text);
        font-size:.96rem;
        line-height:1.5;
        min-height:2.8em;
      }

      .compact {
        margin-top:10px;
      }

      .compact .chip {
        padding:7px 9px;
        font-size:.72rem;
      }

      .explain-grid {
        display:grid;
        grid-template-columns:
          repeat(2,minmax(0,1fr));
        gap:10px;
        margin-top:12px;
      }

      .explain-grid > div {
        padding:12px;
        border-radius:14px;
        background:rgba(255,255,255,.04);
      }

      .explain-grid strong {
        color:var(--gold);
        font-size:.78rem;
        text-transform:uppercase;
        letter-spacing:.05em;
      }

      .explain-grid p {
        margin:5px 0 0;
      }

      @media (max-width:700px) {
        .command-rail {
          grid-template-columns:1fr;
        }

        .resume-banner {
          align-items:flex-start;
          flex-direction:column;
        }

        .explain-grid {
          grid-template-columns:1fr;
        }
      }
    </style>
    """

    return page_factory(
        title=title,
        body=f"""
        {style}
        {return_banner}

        <section
          class="hero"
          aria-label="Soulaana Explains"
        >
          <div class="kicker">
            {escape(subtitle)}
          </div>

          <h1>{escape(title)}</h1>
          <h2>{escape(greeting)}</h2>
          <p>{escape(headline)}</p>
          <p>{escape(explanation)}</p>

          <div class="command-rail">
            <div class="command-stat">
              <strong>{needs_count}</strong>
              <span>Needs You</span>
            </div>

            <div class="command-stat">
              <strong>{watching_count}</strong>
              <span>Keep Watching</span>
            </div>

            <div class="command-stat">
              <strong>{quiet_count}</strong>
              <span>Can Wait</span>
            </div>
          </div>

          <div class="actions">
            <a
              class="button primary"
              href="/tower/ecosystem/lines"
            >
              Ecosystem Lines
            </a>

            <a
              class="button"
              href="/tower/access-home"
            >
              Tower Home
            </a>
          </div>
        </section>

        {''.join(section_html)}
        """,
    )
