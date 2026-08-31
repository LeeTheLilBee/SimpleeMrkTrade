(function (global) {
  "use strict";

  /*
    OBUX081–085 — Observatory appearance identity.

    Tower owns plum / violet / gold.

    Observatory themes deliberately use
    space-black / teal / mint / silver.

    This module changes appearance only.
    It creates no trading permission.
  */

  const KEY =
    "ob.appearance.theme.v2";

  const DEFAULT =
    "aurora-ink";


  const THEMES =
    Object.freeze(
      {
        "aurora-ink": {
          label:
            "Aurora Ink",

          colors: [
            "#050809",
            "#0D1717",
            "#12302D",
            "#39BFA5",
            "#A7E8D8",
            "#D8E2E0",
            "#49B883",
            "#C65E67",
          ],
        },

        "deep-field": {
          label:
            "Deep Field",

          colors: [
            "#040707",
            "#0A1212",
            "#102421",
            "#2B9B88",
            "#8DD8C8",
            "#DDE8E4",
            "#5AA47D",
            "#C65E67",
          ],
        },

        "lunar-sage": {
          label:
            "Lunar Sage",

          colors: [
            "#070A09",
            "#111816",
            "#1B2824",
            "#78A894",
            "#BFD8CE",
            "#E8EEEB",
            "#6FA684",
            "#C65E67",
          ],
        },
      }
    );


  function normalize(
    value
  ) {
    return (
      Object.prototype
        .hasOwnProperty
        .call(
          THEMES,
          value
        )
        ? value
        : DEFAULT
    );
  }


  function current() {
    try {
      return normalize(
        global
          .localStorage
          .getItem(
            KEY
          )
        || DEFAULT
      );
    } catch (_) {
      return DEFAULT;
    }
  }


  function apply(
    value,
    persist
  ) {
    const theme =
      normalize(
        value
      );

    document
      .documentElement
      .dataset
      .obTheme =
        theme;

    if (
      persist !== false
    ) {
      try {
        global
          .localStorage
          .setItem(
            KEY,
            theme
          );
      } catch (_) {}
    }

    global.dispatchEvent(
      new CustomEvent(
        "ob:theme-change",
        {
          detail: {
            theme,
            definition:
              THEMES[theme],
          },
        }
      )
    );

    return theme;
  }


  function options() {
    return Object
      .entries(
        THEMES
      )
      .map(
        function (
          entry
        ) {
          const id =
            entry[0];

          const definition =
            entry[1];

          return {
            id,

            label:
              definition.label,

            colors:
              [
                ...definition
                  .colors,
              ],
          };
        }
      );
  }


  apply(
    current(),
    false
  );


  global.addEventListener(
    "storage",
    function (
      event
    ) {
      if (
        event.key
          === KEY
      ) {
        apply(
          event.newValue
          || DEFAULT,
          false
        );
      }
    }
  );


  global.OBThemeSwitcher =
    Object.freeze(
      {
        key:
          KEY,

        defaultTheme:
          DEFAULT,

        current,

        apply,

        options,
      }
    );

})(window);
