export function initNavbar() {
  document.querySelector("[data-menu-toggle]")?.addEventListener("click", () => {
    document.querySelector(".nav-links")?.classList.toggle("open");
  });
  document.body.classList.toggle("has-fixed-header", Boolean(document.querySelector(".topbar")));
}
