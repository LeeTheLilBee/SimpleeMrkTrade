// OB_GIANT_PACK_043_REAL_DRY_RUN_OUTCOME_FINALIZATION_JS
(() => {
  "use strict";

  const parseResponse = async (response) => {
    let payload = {};

    try {
      payload = await response.json();
    } catch (_error) {
      payload = {};
    }

    if (!response.ok) {
      throw new Error(
        payload.error ||
          payload.message ||
          `Request failed (${response.status})`,
      );
    }

    return payload;
  };

  const request = async (
    url,
    options = {},
  ) => {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });

    return parseResponse(response);
  };

  const toQuery = (params = {}) => {
    const query = new URLSearchParams();

    Object.entries(params).forEach(
      ([key, value]) => {
        if (
          value !== undefined &&
          value !== null &&
          value !== ""
        ) {
          query.set(key, value);
        }
      },
    );

    const rendered = query.toString();

    return rendered ? `?${rendered}` : "";
  };

  window.OBDryRunOutcomeFinalization =
    Object.freeze({
      finalize: (
        flowId,
        payload = {},
      ) =>
        request(
          `/ob/manual-live-checklist-record-save-flows/${encodeURIComponent(
            flowId,
          )}/outcome-finalize.json`,
          {
            method: "POST",
            body: JSON.stringify(payload),
          },
        ),

      get: (finalizationId) =>
        request(
          `/ob/manual-live-dry-run-outcome-finalizations/${encodeURIComponent(
            finalizationId,
          )}.json`,
        ),

      verify: (finalizationId) =>
        request(
          `/ob/manual-live-dry-run-outcome-finalizations/${encodeURIComponent(
            finalizationId,
          )}/verify.json`,
        ),

      list: (params = {}) =>
        request(
          `/ob/manual-live-dry-run-outcome-finalizations.json${toQuery(
            params,
          )}`,
        ),

      status: (params = {}) =>
        request(
          `/ob/manual-live-dry-run-outcome-finalizations-status.json${toQuery(
            params,
          )}`,
        ),
    });

  window.dispatchEvent(
    new CustomEvent(
      "ob:gp043-ready",
      {
        detail: {
          allowedOutcomes: [
            "not_placed",
            "fake_fill",
            "cancelled",
            "needs_review",
            "blocked_live",
          ],
          brokerOrderSubmissionEnabled: false,
          realCapitalMovementEnabled: false,
          directVaultUploadEnabled: false,
          liveAutoLocked: true,
        },
      },
    ),
  );
})();
