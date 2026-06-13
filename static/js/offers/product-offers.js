function initProductOffers() {
  // Logic is now handled by offer-engine.js for global synchronization
  document.querySelectorAll(".price-block.has-offer").forEach((block) => {
    block.classList.add("offer-ready");
  });
}

window.initProductOffers = initProductOffers;
