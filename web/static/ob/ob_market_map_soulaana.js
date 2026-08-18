// THE OBSERVATORY
// OBUX033
// SOULAANA · MARKET MAP
//
// Soulaana interprets canonical truth.
// She does not create the truth.

(function () {
  "use strict";


  function safeArray(value) {
    return Array.isArray(value)
      ? value
      : [];
  }


  function count(value) {
    return safeArray(value).length;
  }


  function explain(
    contract,
    projection,
    changeText
  ) {
    const safeContract =
      (
        contract
        &&
        typeof contract === "object"
      )
        ? contract
        : {};

    const safeProjection =
      (
        projection
        &&
        typeof projection === "object"
      )
        ? projection
        : {};


    const sectors =
      count(
        safeContract.sectors
      );

    const symbols =
      count(
        safeContract.symbols
      );

    const signals =
      count(
        safeContract.signals
      );

    const candidates =
      count(
        safeContract.candidates
      );

    const positions =
      count(
        safeContract.open_positions
      );

    const watchlist =
      count(
        safeContract.watchlist
      );


    if (
      !safeProjection.display_eligible
    ) {
      return {
        what_i_see:
          (
            "I do not have a source-backed market sky "
            +
            "I can safely show you right now."
          ),

        what_it_means:
          (
            "The canonical projection is unavailable, guarded, "
            +
            "or missing enough provenance. I am leaving the sky "
            +
            "quiet instead of carrying old stars forward."
          ),

        what_changed:
          changeText
          ||
          (
            "Current display eligibility is unavailable."
          ),

        what_needs_you:
          (
            "Nothing needs market action from this room."
          ),

        what_can_wait:
          (
            "Everything can wait until source-backed truth returns."
          ),

        next_best_move:
          (
            "Let the canonical feed refresh. "
            +
            "I will update this room when verified truth changes."
          ),

        no_action_needed:
          true,
      };
    }


    if (
      !safeProjection.current_eligible
    ) {
      return {
        what_i_see:
          (
            "I have source-backed market records, but they are "
            +
            "not eligible to be called current."
          ),

        what_it_means:
          (
            "This sky can provide context, but it should not be "
            +
            "treated as proof of what the market is doing right now."
          ),

        what_changed:
          changeText
          ||
          (
            "The latest projection is not current-eligible."
          ),

        what_needs_you:
          positions
            ? (
                positions
                +
                " projected open position"
                +
                (
                  positions === 1
                    ? ""
                    : "s"
                )
                +
                " deserve context review first, but stale truth "
                +
                "is not permission for a new decision."
              )
            : (
                "No fresh market decision should be made from this room."
              ),

        what_can_wait:
          (
            signals
            +
            " signal record"
            +
            (
              signals === 1
                ? ""
                : "s"
            )
            +
            " and "
            +
            candidates
            +
            " candidate record"
            +
            (
              candidates === 1
                ? ""
                : "s"
            )
            +
            " can wait for current truth."
          ),

        next_best_move:
          (
            "Let the canonical feed restore current eligibility "
            +
            "before treating this sky as live market context."
          ),

        no_action_needed:
          true,
      };
    }


    let needsYou;

    if (positions) {
      needsYou =
        (
          positions
          +
          " open position"
          +
          (
            positions === 1
              ? ""
              : "s"
          )
          +
          " are already exposed to the market. "
          +
          "They deserve your eyes before new opportunities."
        );
    }

    else if (
      signals
      ||
      candidates
    ) {
      needsYou =
        (
          signals
          +
          " signal record"
          +
          (
            signals === 1
              ? ""
              : "s"
          )
          +
          " and "
          +
          candidates
          +
          " candidate record"
          +
          (
            candidates === 1
              ? ""
              : "s"
          )
          +
          " deserve observation. Attention is not permission."
        );
    }

    else {
      needsYou =
        (
          "Nothing is asking for immediate market attention."
        );
    }


    return {
      what_i_see:
        (
          "The current canonical projection gives me "
          +
          sectors
          +
          " sector group"
          +
          (
            sectors === 1
              ? ""
              : "s"
          )
          +
          " and "
          +
          symbols
          +
          " source-backed symbol"
          +
          (
            symbols === 1
              ? ""
              : "s"
          )
          +
          "."
        ),

      what_it_means:
        (
          "This map shows where OB currently has source-backed "
          +
          "market context. It is not a prediction, ranking, "
          +
          "or automatic trade instruction."
        ),

      what_changed:
        changeText
        ||
        (
          "This is the first verified view in this browser session."
        ),

      what_needs_you:
        needsYou,

      what_can_wait:
        watchlist
          ? (
              watchlist
              +
              " watchlist record"
              +
              (
                watchlist === 1
                  ? ""
                  : "s"
              )
              +
              " can remain in the background until the evidence changes."
            )
          : (
              "Anything without a projected position, signal, "
              +
              "or candidate state can stay in the background."
            ),

      next_best_move:
        (
          positions
          ||
          signals
          ||
          candidates
        )
          ? (
              "Open a source-backed symbol only when you want "
              +
              "the deeper read. Market Map itself takes no action."
            )
          : (
              "No move is required. Keep observing until "
              +
              "the canonical projection gives you a reason."
            ),

      no_action_needed:
        !(
          positions
          ||
          signals
          ||
          candidates
        ),
    };
  }


  window.OB_MARKET_MAP_SOULAANA_OBUX033 = {
    explain,
  };
})();
