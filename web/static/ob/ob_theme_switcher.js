(function (global) {
  "use strict";

  const KEY =
    "ob.appearance.theme.v1";

  const DEFAULT =
    "obsidian-plum";


  const THEMES =
    Object.freeze(
      {
        "obsidian-plum": {
          label:
            "Obsidian Plum",

          colors: [
            "#07070B",
            "#15111D",
            "#2C2038",
            "#6C4D8E",
            "#B58A45",
            "#F3EBDD",
            "#6E8F6E",
            "#C46A6A",
          ],
        },

        "velvet-night": {
          label:
            "Velvet Night",

          colors: [
            "#08090D",
            "#17131F",
            "#221A2D",
            "#8E79B7",
            "#C49A57",
            "#F5EEDF",
            "#6D8B6F",
            "#B86464",
          ],
        },

        "eclipse-gold": {
          label:
            "Eclipse Gold",

          colors: [
            "#06070A",
            "#131017",
            "#261E2D",
            "#74618F",
            "#D0A45D",
            "#F6F0E6",
            "#7C8A6A",
            "#B05A67",
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
        key: KEY,

        defaultTheme:
          DEFAULT,

        current,

        apply,

        options,
      }
    );

})(window);
