import { offerStorage } from "./local-storage-manager.js";

export function initOfferPopup(offer) {
  const popup = document.getElementById("deal-popup-container");
  const close = popup?.querySelector(".popup-close");
  if (!popup || !offer) return;
  if (offerStorage.get("dismissed", offer.id) === "1") {
    popup.hidden = true;
    return;
  }
  popup.hidden = offerStorage.get("closed", offer.id) === "1";
  close?.addEventListener("click", () => {
    offerStorage.set("closed", offer.id);
    popup.hidden = true;
    window.dispatchEvent(new CustomEvent("growmore:offer-closed", { detail: offer }));
  });
}

export function reopenOfferPopup(offer) {
  const popup = document.getElementById("deal-popup-container");
  if (!popup || !offer) return;
  offerStorage.remove("closed", offer.id);
  popup.hidden = false;
}
