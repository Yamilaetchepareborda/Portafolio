// JS mínimo: menú en celular y tema claro/oscuro. El sitio funciona sin JS.
(function () {
  var root = document.documentElement;

  // ---- Menú móvil
  var menuBtn = document.getElementById("menu-toggle");
  var nav = document.getElementById("menu");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("is-open");
        menuBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  // ---- Tema
  var themeBtn = document.getElementById("theme-toggle");
  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "oscuro" : "claro";
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "oscuro" ? "claro" : "oscuro";
      root.dataset.theme = next;
      try { localStorage.setItem("tema", next); } catch (e) {}
    });
  }
})();
