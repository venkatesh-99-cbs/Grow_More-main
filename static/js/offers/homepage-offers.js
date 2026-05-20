import { initOfferCountdowns } from "./countdown-manager.js";
import { initFloatingBall } from "./floating-ball.js";
import { getEmbeddedOffer } from "./offer-service.js";
import { initOfferPopup } from "./popup-banner.js";
import { initProductOffers } from "./product-offers.js";

document.addEventListener("DOMContentLoaded", () => {
  const offer = getEmbeddedOffer();
  initOfferPopup(offer);
  initFloatingBall(offer);
  initProductOffers();
  initOfferCountdowns();
});
