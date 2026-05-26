document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".admin-nav a").forEach((link) => {
    link.classList.toggle("active", link.href === window.location.href);
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });
});
