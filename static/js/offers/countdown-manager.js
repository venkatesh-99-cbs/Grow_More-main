import { formatCountdown } from "../core/utilities.js";

const timers = new Set();
let intervalId = null;

export function initOfferCountdowns() {
  document.querySelectorAll("[data-offer-countdown][data-offer-end]").forEach((node) => timers.add(node));
  if (!timers.size || intervalId) return;
  intervalId = setInterval(tick, 1000);
  tick();
}

export function tick() {
  const serverStart = Date.parse(document.body.dataset.serverTime || new Date().toISOString());
  const clientStart = window._clientStartTime || (window._clientStartTime = Date.now());
  const now = serverStart + (Date.now() - clientStart);

  timers.forEach((node) => {
    if (!document.body.contains(node)) {
      timers.delete(node);
      return;
    }
    const endTime = Date.parse(node.dataset.offerEnd);
    const seconds = Math.max(0, Math.floor((endTime - now) / 1000));
    node.textContent = seconds ? formatCountdown(seconds) : "Offer ended";
    node.classList.toggle("expired", seconds === 0);
    if (seconds === 0) {
      node.closest("[data-offer-expirable]")?.setAttribute("hidden", "");
      document.getElementById("deal-floating-ball")?.setAttribute("hidden", "");
    }
  });
  if (!timers.size && intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}
