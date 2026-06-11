export function initNavbar() {
  const toggle = document.querySelector("[data-menu-toggle]");
  const navLinks = document.querySelector(".nav-links");

  if (toggle && navLinks) {
    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      navLinks.classList.toggle("open");
      toggle.innerHTML = navLinks.classList.contains("open") ? "&times;" : "&#9776;";
    });

    // Close menu when clicking outside
    document.addEventListener("click", (e) => {
      if (navLinks.classList.contains("open") && !navLinks.contains(e.target) && !toggle.contains(e.target)) {
        navLinks.classList.remove("open");
        toggle.innerHTML = "&#9776;";
      }
    });

    // Close menu when clicking a link
    navLinks.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("open");
            toggle.innerHTML = "&#9776;";
        });
    });
  }

  document.body.classList.toggle("has-fixed-header", Boolean(document.querySelector(".topbar")));
}
