export const money = (value) => `Rs. ${Number(value || 0).toFixed(2)}`;

export function showToast(message) {
  if (window.notifications) {
    window.notifications.info(message);
    return;
  }
  let toast = document.getElementById("gm-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "gm-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 1800);
}

export function selectedValue(scope, role) {
  return scope.querySelector(`.radio-row[data-role='${role}'] .radio-pill.active`)?.dataset.value || "";
}

export function initReveal() {
  const nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
        observer.unobserve(entry.target);
      }
    }),
    { threshold: 0.15 },
  );
  nodes.forEach((node) => observer.observe(node));
}

export function formatCountdown(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const mins = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  return [hours, mins, secs].map((n) => String(n).padStart(2, "0")).join(":");
}
