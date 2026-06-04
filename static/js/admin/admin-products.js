const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
const maxSize = 5 * 1024 * 1024;

function showUploadMessage(message, type = "info") {
  if (window.notifications?.[type]) {
    window.notifications[type](message);
  } else if (window.notifications) {
    window.notifications.show(message, { type });
  }
}

function validateFile(file) {
  if (!file) return true;
  if (!allowedTypes.includes(file.type)) {
    showUploadMessage("Upload a JPG, JPEG, PNG, or WEBP image.", "error");
    return false;
  }
  if (file.size > maxSize) {
    showUploadMessage("Image must be 5 MB or smaller.", "error");
    return false;
  }
  return true;
}

function renderPreview(input, preview) {
  const files = [...input.files];
  if (!files.length || !files.every(validateFile)) {
    input.value = "";
    return;
  }

  preview.innerHTML = "";
  files.forEach((file) => {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.alt = file.name;
    preview.appendChild(img);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-product-form]");
  const preview = document.querySelector("[data-image-preview]");
  const dropzone = document.querySelector("[data-upload-dropzone]");
  const progress = document.querySelector("[data-upload-progress]");
  const progressBar = progress?.querySelector("span");
  const mainInput = document.getElementById("id_main_image");

  if (preview) {
    document.querySelectorAll("input[type='file']").forEach((input) => {
      input.addEventListener("change", () => renderPreview(input, preview));
    });
  }

  if (dropzone && mainInput) {
    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.add("is-dragging");
      });
    });
    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.remove("is-dragging");
      });
    });
    dropzone.addEventListener("drop", (event) => {
      const file = event.dataTransfer.files?.[0];
      if (!file || !validateFile(file)) return;
      const transfer = new DataTransfer();
      transfer.items.add(file);
      mainInput.files = transfer.files;
      renderPreview(mainInput, preview);
    });
  }

  form?.addEventListener("submit", (event) => {
    if (!window.FormData || !window.XMLHttpRequest) return;
    event.preventDefault();

    const submitButton = form.querySelector("[type='submit']");
    const request = new XMLHttpRequest();
    request.open("POST", form.action || window.location.href);
    request.setRequestHeader("X-Requested-With", "XMLHttpRequest");

    if (progress && progressBar) {
      progress.setAttribute("aria-hidden", "false");
      progressBar.style.width = "4%";
    }
    if (submitButton) submitButton.disabled = true;

    request.upload.addEventListener("progress", (uploadEvent) => {
      if (!uploadEvent.lengthComputable || !progressBar) return;
      const percent = Math.max(8, Math.round((uploadEvent.loaded / uploadEvent.total) * 100));
      progressBar.style.width = `${percent}%`;
    });

    request.addEventListener("load", () => {
      if (progressBar) progressBar.style.width = "100%";
      if (request.responseURL && request.responseURL !== window.location.href) {
        window.location.href = request.responseURL;
        return;
      }
      document.open();
      document.write(request.responseText);
      document.close();
    });

    request.addEventListener("error", () => {
      if (submitButton) submitButton.disabled = false;
      showUploadMessage("Upload failed. Please check your connection and try again.", "error");
    });

    request.send(new FormData(form));
  });
});
