import { initOfferCountdowns } from "./countdown-manager.js";

export function initProductOffers() {
  initOfferCountdowns();
  document.querySelectorAll(".price-block.has-offer").forEach((block) => {
    block.classList.add("offer-ready");
  });
}
