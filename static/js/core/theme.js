import { formatCountdown } from "./utilities.js";

const DEAL_SECONDS = 2 * 3600 + 14 * 60 + 39;

export function initDealTimer() {
  if (!localStorage.getItem("gm_deal_end_time")) {
    localStorage.setItem("gm_deal_end_time", String(Date.now() + DEAL_SECONDS * 1000));
  }
  const tick = () => {
    const end = Number(localStorage.getItem("gm_deal_end_time") || 0);
    const seconds = Math.max(0, Math.floor((end - Date.now()) / 1000));
    document.querySelectorAll(".popup-countdown, .limited-badge[data-ends-seconds]").forEach((el) => {
      el.textContent = seconds ? (el.classList.contains("limited-badge") ? `Ends in ${formatCountdown(seconds)}` : formatCountdown(seconds)) : "Deal ended";
    });
    if (!seconds) document.getElementById("deal-popup-container")?.style.setProperty("display", "none");
  };
  tick();
  setInterval(tick, 1000);
}

export function initPopupBanner() {
  const container = document.getElementById("deal-popup-container");
  const close = container?.querySelector(".popup-close");
  if (!container || !close) return;
  if (localStorage.getItem("gm_popup_closed") === "1") container.style.display = "none";
  close.addEventListener("click", () => {
    localStorage.setItem("gm_popup_closed", "1");
    container.style.display = "none";
  });
}
