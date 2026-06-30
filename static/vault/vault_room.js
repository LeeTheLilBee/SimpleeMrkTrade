/* Vault Giant Pack 002 room behavior. */
(function () {
  const room = window.VAULT_ROOM_BOOTSTRAP || {};

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function renderDocument(index) {
    const records = (((room || {}).document_drawer || {}).records || []);
    const detail = qs("[data-vault-document-detail]");
    if (!detail || !records.length) return;

    const record = records[index] || records[0];
    const chips = (record.drawer_status_chips || [])
      .map((chip) => `<span>${chip}</span>`)
      .join("");

    const hiddenCount = (record.sensitive_fields_hidden || []).length;
    const receiptCount = (record.linked_receipts || []).length;

    detail.innerHTML = `
      <p class="vault-eyebrow">${record.business_lane || "vault"} / ${record.document_type || "document"}</p>
      <h2>${record.title || "Document Index"}</h2>
      <p class="vault-muted">${record.summary || "No summary available."}</p>

      <div class="vault-detail-grid">
        <article>
          <span>Status</span>
          <strong>${record.status || "unknown"}</strong>
        </article>
        <article>
          <span>Sensitivity</span>
          <strong>${record.sensitivity || "unknown"}</strong>
        </article>
        <article>
          <span>Linked receipts</span>
          <strong>${receiptCount}</strong>
        </article>
        <article>
          <span>Hidden sensitive fields</span>
          <strong>${hiddenCount}</strong>
        </article>
        <article>
          <span>Freshness window</span>
          <strong>${record.freshness_days || 0} days</strong>
        </article>
        <article>
          <span>Direct upload</span>
          <strong>${record.direct_upload_allowed ? "allowed" : "locked"}</strong>
        </article>
      </div>

      <div class="vault-detail-chip-row">
        ${chips}
      </div>

      <div class="vault-card-footer">
        <strong>Owner next action</strong>
        <small>${record.next_action || "Review this record."}</small>
      </div>
    `;
  }

  function setupDocumentDrawer() {
    const buttons = qsa("[data-doc-index]");
    if (!buttons.length) return;

    buttons.forEach((button) => {
      button.addEventListener("click", function () {
        buttons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        renderDocument(Number(button.getAttribute("data-doc-index") || 0));
      });
    });

    renderDocument(0);
  }

  function setupPacketFilters() {
    const buttons = qsa("[data-filter]");
    const cards = qsa("[data-vault-packet-grid] .vault-packet-card");
    if (!buttons.length || !cards.length) return;

    buttons.forEach((button, index) => {
      if (index === 0) button.classList.add("active");

      button.addEventListener("click", function () {
        const filter = button.getAttribute("data-filter");
        buttons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");

        cards.forEach((card) => {
          const lane = card.getAttribute("data-lane");
          const status = card.getAttribute("data-status");
          const show = filter === "all" || filter === lane || filter === status;
          card.style.display = show ? "" : "none";
        });
      });
    });
  }

  function setup() {
    setupDocumentDrawer();
    setupPacketFilters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
