"use strict";
(() => {
  const form = document.getElementById("tower-buybox-bootstrap");
  if (form && form.method.toLowerCase() === "post") {
    form.submit();
  }
})();
