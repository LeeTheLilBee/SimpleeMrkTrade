// OBSERVATORY_V13_HOVER_NAV_ROUTE_POLISH_JS

(function () {
  function currentRoom(path) {
    if (path.includes("/symbol/")) return "Symbol Page";
    if (path.includes("market-map")) return "Market Map";
    if (path.includes("trade")) return "Trade Center";
    if (path.includes("review")) return "Review Center";
    if (path.includes("owner") || path.includes("admin")) return "Owner Console";
    return "Dashboard";
  }

  function isActive(path, key) {
    if (key === "dashboard") return currentRoom(path) === "Dashboard";
    if (key === "market") return path.includes("market-map");
    if (key === "trade") return path.includes("trade");
    if (key === "review") return path.includes("review");
    if (key === "owner") return path.includes("owner") || path.includes("admin");
    return false;
  }

  function navLink(path, href, label, key, locked) {
    const active = isActive(path, key) ? " active" : "";
    const lock = locked ? " locked" : "";
    return `<a class="ob-nav-link${active}${lock}" href="${href}">
      <span>${label}</span>
      <span class="ob-nav-dot"></span>
    </a>`;
  }

  function buildNav() {
    if (document.getElementById("obHoverRail")) return;

    const path = window.location.pathname;

    const rail = document.createElement("aside");
    rail.id = "obHoverRail";
    rail.className = "ob-hover-rail";
    rail.setAttribute("aria-label", "Observatory navigation");

    rail.innerHTML = `
      <div class="ob-hover-menu-tab">MENU</div>

      <div class="ob-nav-content">
        <div class="ob-nav-brand">
          <strong>The Observatory</strong>
          <span>private room map</span>
        </div>

        <div class="ob-nav-group">
          <div class="ob-nav-group-label">Observe</div>
          ${navLink(path, "/ob/dashboard", "Dashboard", "dashboard", false)}
          ${navLink(path, "/ob/market-map", "Market Map", "market", false)}
        </div>

        <div class="ob-nav-group">
          <div class="ob-nav-group-label">Trade</div>
          ${navLink(path, "/trade-center", "Trade Center", "trade", false)}
        </div>

        <div class="ob-nav-group">
          <div class="ob-nav-group-label">Review</div>
          ${navLink(path, "/review-center", "Review Center", "review", false)}
        </div>

        <div class="ob-nav-group">
          <div class="ob-nav-group-label">Owner</div>
          ${navLink(path, "/ob/owner-console", "Owner Console", "owner", true)}
        </div>

        <div class="ob-nav-foot">
          OB shows the signal.<br>
          Tower controls permission.<br>
          Soulaana tells you how to move clean.
        </div>
      </div>
    `;

    document.body.prepend(rail);
  }

  function buildRouteBar() {
    if (document.getElementById("obRouteBar")) return;

    const app = document.getElementById("ob-app");
    const layer = document.querySelector(".ob-layer");
    if (!app || !layer) return;

    const path = window.location.pathname;
    const room = currentRoom(path);

    const bar = document.createElement("div");
    bar.id = "obRouteBar";
    bar.className = "ob-route-bar";

    const symbolMatch = path.match(/\/symbol\/([^/]+)/i);
    const symbolText = symbolMatch ? " · " + decodeURIComponent(symbolMatch[1]).toUpperCase() : "";

    bar.innerHTML = `
      <div class="ob-route-crumb">
        <strong>OB://${room.replace(/\s+/g, "")}</strong>${symbolText}
      </div>

      <div class="ob-route-actions">
        <span class="ob-route-chip gold">Paper Mode</span>
        <span class="ob-route-chip green">Tower Clear</span>
        <span class="ob-route-chip red">Live Auto Locked</span>
        <span class="ob-route-chip">Settings</span>
        <span class="ob-route-chip">Notifications</span>
      </div>
    `;

    layer.prepend(bar);
  }

  document.addEventListener("DOMContentLoaded", function () {
    buildNav();
    buildRouteBar();
  });
})();
