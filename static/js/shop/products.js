import { storage } from "../services/storage-service.js";
import { apiGet } from "../services/api-service.js";
import { initReveal, money, showToast } from "../core/utilities.js";
import { initProductOffers } from "../offers/product-offers.js";

const COLOR_MAP = {
  "Bright Blue": "#51e2f5",
  "Blue Green": "#9df9ef",
  "Dusty White": "#edf756",
  "Pink Sand": "#ffa8b6",
  "Dark Sand": "#a28089",
};

function favorites() {
  return storage.get("gm_favorites", []);
}

function setFavorites(ids) {
  storage.set("gm_favorites", ids);
  updateFavoriteCount();
}

export function updateFavoriteCount() {
  const count = document.getElementById("fav-count");
  if (count) count.textContent = String(favorites().length);
  document.querySelectorAll("[data-favorite-id]").forEach((btn) => {
    btn.classList.toggle("active", favorites().includes(Number(btn.dataset.favoriteId)));
  });
}

export function initFavoriteUI() {
  updateFavoriteCount();
  if (document.body.dataset.favoriteBound === "1") return;
  document.body.dataset.favoriteBound = "1";
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-favorite-id]");
    if (!button) return;
    const id = Number(button.dataset.favoriteId);
    const current = favorites();
    const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id];
    setFavorites(next);
    showToast(next.includes(id) ? "Added to favorites" : "Removed from favorites");
    renderFavoritesPage();
    event.preventDefault();
  });
}

function productCard(product) {
  const favoriteActive = favorites().includes(product.id) ? "active" : "";
  const front = product.images[0] || "";
  const back = product.images[1] || front;
  const sizes = product.sizes.map((size, index) => `<button type="button" class="radio-pill ${index === 0 ? "active" : ""}" data-value="${size}">${size}</button>`).join("");
  const colors = product.colors.map((color, index) => `<button type="button" class="radio-pill color-pill ${index === 0 ? "active" : ""}" data-value="${color}" style="--swatch:${COLOR_MAP[color] || "#fff"}"><span class="swatch"></span><span class="pill-text">${color}</span></button>`).join("");
  const offerMarkup = product.offer ? `
    <div class="offer-chip-row">
      <span class="offer-label-chip">${product.offer.label}</span>
      ${product.isTrending ? '<span class="offer-label-chip muted-chip">Trending Deal</span>' : ""}
    </div>
    <div class="limited-badge" data-offer-countdown data-offer-end="${product.offer.endsAt}">Limited time</div>
  ` : "";
  const highlight = product.offer?.highlight || "Premium summer pricing";
  return `
    <article class="product-card reveal" data-product-id="${product.id}" data-product-url="${product.url}">
      <div class="product-media" aria-label="${product.name}">
        <div class="flip-inner"><img class="front" src="${front}" alt="${product.name} front" loading="lazy"><img class="back" src="${back}" alt="${product.name} back" loading="lazy"></div>
        <button type="button" class="fav-btn ${favoriteActive}" data-favorite-id="${product.id}" title="Add to favorites">&#10084;</button><div class="flip-hint">Tap to flip</div>
      </div>
      <div class="product-body">
        <p class="chip">${product.categoryName}</p><h3>${product.name}</h3><p class="tiny">${product.desc}</p>
        <div class="price-block ${product.offer ? "has-offer" : ""}" ${product.offer ? `data-offer-expirable` : ""}><div class="price-line"><span class="price-now">${money(product.price)}</span><span class="price-old">${money(product.originalPrice)}</span><span class="price-off">${product.discountPercent}% OFF</span></div><div class="save-line">${highlight}</div>${offerMarkup}</div>
        <div class="variant-stack"><label>Size</label><div class="radio-row" data-role="size">${sizes}</div>${colors ? `<label>Color</label><div class="radio-row" data-role="color">${colors}</div>` : ""}</div>
        <button class="add-btn" type="button" data-add-cart>Add to cart</button>
      </div>
    </article>`;
}

async function initShopControls() {
  const grid = document.getElementById("product-grid");
  if (!grid) return;
  const category = document.getElementById("category-filter");
  const sort = document.getElementById("sort-by");
  const search = document.getElementById("search-input");
  const apply = async () => {
    const params = new URLSearchParams({ q: search?.value || "", category: category?.value || "all", sort: sort?.value || "featured" });
    const data = await apiGet(`/api/products/?${params.toString()}`);
    grid.innerHTML = data.products.map(productCard).join("") || "<p class='muted'>No matching products.</p>";
    initReveal();
    initProductOffers();
    updateFavoriteCount();
  };
  category?.addEventListener("change", apply);
  sort?.addEventListener("change", apply);
  search?.addEventListener("input", apply);
}

function initCardNavigation() {
  document.addEventListener("click", (event) => {
    const pill = event.target.closest(".radio-pill");
    if (pill) {
      const row = pill.closest(".radio-row");
      row?.querySelectorAll(".radio-pill").forEach((button) => button.classList.remove("active"));
      pill.classList.add("active");
      return;
    }
    const media = event.target.closest(".product-media");
    if (media && window.matchMedia("(hover: none)").matches) {
      media.classList.toggle("flipped");
      event.preventDefault();
      return;
    }
    const card = event.target.closest(".product-card");
    if (!card || event.target.closest("button, input, select, textarea, a, .radio-row")) return;
    window.location.href = card.dataset.productUrl;
  });
}

function renderFavoritesPage() {
  const target = document.getElementById("favorites-grid");
  const source = document.querySelector(".hidden-product-source");
  if (!target || !source) return;
  const wanted = favorites();
  const cards = [...source.querySelectorAll(".product-card")].filter((card) => wanted.includes(Number(card.dataset.productId)));
  target.innerHTML = cards.length ? cards.map((card) => card.outerHTML).join("") : "<p class='muted'>No favorites yet. Tap the heart on products.</p>";
  updateFavoriteCount();
}

document.addEventListener("DOMContentLoaded", () => {
  initFavoriteUI();
  initShopControls();
  initCardNavigation();
  renderFavoritesPage();
});
