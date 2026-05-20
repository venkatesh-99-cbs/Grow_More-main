import { preventDoubleSubmit } from "../services/validation-service.js";

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(preventDoubleSubmit);
});
