document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("select[name='status']").forEach((select) => {
    select.title = "Update order status";
  });
});
