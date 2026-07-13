// OB_GIANT_PACK_044_OUTCOME_TO_RECEIPT_MATERIALIZATION_JS
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

  window.OBOutcomeReceiptMaterialization =
    Object.freeze({
      create: (
        finalizationId,
        payload = {},
      ) =>
        request(
          `/ob/manual-live-dry-run-outcome-finalizations/${encodeURIComponent(
            finalizationId,
          )}/receipt.json`,
          {
            method: "POST",
            body: JSON.stringify(payload),
          },
        ),

      get: (receiptId) =>
        request(
          `/ob/manual-live-outcome-receipts/${encodeURIComponent(
            receiptId,
          )}.json`,
        ),

      verify: (receiptId) =>
        request(
          `/ob/manual-live-outcome-receipts/${encodeURIComponent(
            receiptId,
          )}/verify.json`,
        ),

      list: (params = {}) =>
        request(
          `/ob/manual-live-outcome-receipts.json${toQuery(
            params,
          )}`,
        ),

      status: (params = {}) =>
        request(
          `/ob/manual-live-outcome-receipts-status.json${toQuery(
            params,
          )}`,
        ),
    });

  window.dispatchEvent(
    new CustomEvent("ob:gp044-ready", {
      detail: {
        brokerOrderSubmissionEnabled: false,
        realCapitalMovementEnabled: false,
        directVaultUploadEnabled: false,
        rawPublicReceiptUrlEnabled: false,
        liveAutoLocked: true,
      },
    }),
  );
})();
