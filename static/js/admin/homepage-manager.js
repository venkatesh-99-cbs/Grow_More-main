document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("input[type='file']").forEach((input) => {
    input.addEventListener("change", () => {
      const label = input.closest("p")?.querySelector("label");
      if (label && input.files[0]) label.textContent = `${label.textContent} (${input.files[0].name})`;
    });
  });
});
