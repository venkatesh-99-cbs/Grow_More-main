document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".admin-nav a").forEach((link) => {
    link.classList.toggle("active", link.href === window.location.href);
  });
});
