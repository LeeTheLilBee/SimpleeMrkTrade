(() => {
  "use strict";
  const form = document.getElementById("towerBuyBoxBootstrap");
  if (!form) return;
  if ((form.getAttribute("method") || "").toLowerCase() !== "post") return;
  const action = form.getAttribute("action") || "";
  if (!action.startsWith("https://") || !action.endsWith("/tower/bootstrap")) return;
  const handoff = form.querySelector('input[name="handoff"]');
  if (!handoff || !handoff.value) return;
  form.submit();
})();
