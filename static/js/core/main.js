import { initNavbar } from "./navbar.js";
import { initReveal } from "./utilities.js";
import { initCartUI } from "../shop/cart.js";
import { initFavoriteUI, initCardNavigation, initShopControls } from "../shop/products.js";

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initCartUI();
  initFavoriteUI();
  initCardNavigation();
  initShopControls();
  initReveal();
});
