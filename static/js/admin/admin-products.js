document.addEventListener("DOMContentLoaded", () => {
  const preview = document.querySelector("[data-image-preview]");
  if (!preview) return;
  document.querySelectorAll("input[type='file']").forEach((input) => {
    input.addEventListener("change", () => {
      preview.innerHTML = "";
      [...input.files].forEach((file) => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        preview.appendChild(img);
      });
    });
  });
});
