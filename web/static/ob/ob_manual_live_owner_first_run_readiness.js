// OB_GIANT_PACK_045_OWNER_FIRST_RUN_READINESS_CHECKPOINT_JS
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

  window.OBOwnerFirstRunReadiness =
    Object.freeze({
      evaluate: (
        receiptId,
        ownerAssertions,
        ownerId = "owner",
      ) =>
        request(
          "/ob/manual-live-owner-first-run-readiness/evaluate.json",
          {
            method: "POST",
            body: JSON.stringify({
              receipt_id: receiptId,
              owner_id: ownerId,
              owner_assertions:
                ownerAssertions || {},
            }),
          },
        ),

      get: (checkpointId) =>
        request(
          `/ob/manual-live-owner-first-run-readiness/${encodeURIComponent(
            checkpointId,
          )}.json`,
        ),

      verify: (checkpointId) =>
        request(
          `/ob/manual-live-owner-first-run-readiness/${encodeURIComponent(
            checkpointId,
          )}/verify.json`,
        ),

      list: (params = {}) =>
        request(
          `/ob/manual-live-owner-first-run-readiness.json${toQuery(
            params,
          )}`,
        ),

      status: (params = {}) =>
        request(
          `/ob/manual-live-owner-first-run-readiness-status.json${toQuery(
            params,
          )}`,
        ),
    });

  window.dispatchEvent(
    new CustomEvent(
      "ob:gp045-ready",
      {
        detail: {
          productionManualLiveAuthorized: false,
          brokerOrderSubmissionEnabled: false,
          realCapitalMovementEnabled: false,
          directVaultUploadEnabled: false,
          liveAutoLocked: true,
          ownerFirstRunIsRehearsalOnly: true,
        },
      },
    ),
  );
})();
