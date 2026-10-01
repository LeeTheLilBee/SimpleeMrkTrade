"use strict";
(() => {
  const commandLinks = document.querySelectorAll("[data-command-open]");
  const global = document.getElementById("global-q");
  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const typing = target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
    if (event.key === "/" && !typing && global) {
      event.preventDefault();
      global.focus();
    }
  });
  commandLinks.forEach((link) => link.setAttribute("title", "Search BuyBox (press /)"));
})();