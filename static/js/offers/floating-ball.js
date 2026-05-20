import { offerStorage } from "./local-storage-manager.js";
import { reopenOfferPopup } from "./popup-banner.js";

export function initFloatingBall(offer) {
  const ball = document.getElementById("deal-floating-ball");
  if (!ball || !offer || !offer.floatingBallEnabled) return;
  const maybeShow = () => {
    const closed = offerStorage.get("closed", offer.id) === "1";
    const dismissed = offerStorage.get("dismissed", offer.id) === "1";
    ball.hidden = !closed || dismissed;
  };
  maybeShow();
  window.addEventListener("growmore:offer-closed", maybeShow);
  ball.addEventListener("click", (event) => {
    if (event.target.closest("[data-offer-dismiss]")) {
      offerStorage.set("dismissed", offer.id);
      ball.hidden = true;
      event.stopPropagation();
      return;
    }
    reopenOfferPopup(offer);
    ball.hidden = true;
  });
}
