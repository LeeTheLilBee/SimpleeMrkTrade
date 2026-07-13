// OB_GIANT_PACK_042_REAL_CHECKLIST_TO_RECORD_SAVE_FLOW_JS
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
      const message =
        payload.error ||
        payload.message ||
        `Request failed (${response.status})`;

      throw new Error(message);
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

  const client = {
    create: (
      handoffId,
      payload,
    ) =>
      request(
        `/ob/manual-live-candidate-decision-handoffs/${encodeURIComponent(
          handoffId,
        )}/checklist-record-save.json`,
        {
          method: "POST",
          body: JSON.stringify(
            payload || {},
          ),
        },
      ),

    get: (flowId) =>
      request(
        `/ob/manual-live-checklist-record-save-flows/${encodeURIComponent(
          flowId,
        )}.json`,
      ),

    list: (params = {}) => {
      const search =
        new URLSearchParams();

      Object.entries(params).forEach(
        ([key, value]) => {
          if (
            value !== undefined &&
            value !== null &&
            value !== ""
          ) {
            search.set(key, value);
          }
        },
      );

      const suffix = search.toString();

      return request(
        `/ob/manual-live-checklist-record-save-flows.json${
          suffix ? `?${suffix}` : ""
        }`,
      );
    },

    status: (params = {}) => {
      const search =
        new URLSearchParams();

      Object.entries(params).forEach(
        ([key, value]) => {
          if (
            value !== undefined &&
            value !== null &&
            value !== ""
          ) {
            search.set(key, value);
          }
        },
      );

      const suffix = search.toString();

      return request(
        `/ob/manual-live-checklist-record-save-flows-status.json${
          suffix ? `?${suffix}` : ""
        }`,
      );
    },
  };

  window.OBChecklistRecordSaveFlow =
    Object.freeze(client);

  window.dispatchEvent(
    new CustomEvent(
      "ob:gp042-ready",
      {
        detail: {
          orderSubmitEnabled: false,
          capitalMovementEnabled: false,
          directVaultUploadEnabled: false,
          liveAutoLocked: true,
        },
      },
    ),
  );
})();
