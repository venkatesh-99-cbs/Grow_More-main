export function validateStep(stepEl) {
  const fields = [...stepEl.querySelectorAll("input, select, textarea")].filter((el) => !el.disabled);
  for (const field of fields) {
    if (!field.checkValidity()) {
      field.reportValidity();
      return false;
    }
  }
  return true;
}

export function preventDoubleSubmit(form) {
  form?.addEventListener("submit", () => {
    const button = form.querySelector("button[type='submit']");
    if (button) {
      button.disabled = true;
      button.dataset.originalText = button.textContent;
      button.textContent = "Processing...";
    }
  });
}
