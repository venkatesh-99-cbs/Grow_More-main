import { storage } from "../services/storage-service.js";
import { apiGet, apiPost } from "../services/api-service.js";
import { initReveal, money, showToast } from "../core/utilities.js";
import { initProductOffers } from "../offers/product-offers.js";

let cachedFavorites = null;

async function getFavorites() {
  if (cachedFavorites !== null) return cachedFavorites;

  // Try to get from API if logged in
  const response = await apiGet("/api/wishlist/");
  if (response && Array.isArray(response.ids)) {
    cachedFavorites = response.ids;
  } else {
    cachedFavorites = storage.get("gm_favorites", []);
  }
  return cachedFavorites;
}

function setFavoritesLocally(ids) {
  cachedFavorites = ids;
  storage.set("gm_favorites", ids);
  updateFavoriteCount();
}

export async function updateFavoriteCount() {
  const favs = await getFavorites();
  const count = document.getElementById("fav-count");
  if (count) count.textContent = String(favs.length);
  document.querySelectorAll("[data-id]").forEach((btn) => {
    if (btn.classList.contains('fav-btn')) {
      btn.classList.toggle("active", favs.includes(Number(btn.dataset.id)));
    }
  });
}

export function initFavoriteUI() {
  updateFavoriteCount();
  if (document.body.dataset.favoriteBound === "1") return;
  document.body.dataset.favoriteBound = "1";
  document.addEventListener("click", async (event) => {
    const button = event.target.closest(".fav-btn[data-id]");
    if (!button) return;

    event.preventDefault();
    event.stopPropagation();

    const id = Number(button.dataset.id);

    if (document.body.dataset.authenticated !== 'true') {
        showToast("Please login to use wishlist");
        return;
    }

    try {
      // Optimistic UI update
      const allMatchingBtns = document.querySelectorAll(`.fav-btn[data-id="${id}"]`);
      const wasActive = button.classList.contains('active');
      allMatchingBtns.forEach(b => b.classList.toggle('active', !wasActive));

      const response = await apiPost("/api/wishlist/toggle/", { product_id: id });

      if (response && typeof response.added !== 'undefined') {
        // Update local cache
        const current = await getFavorites();
        const next = response.added ? [...new Set([...current, id])] : current.filter(fid => fid !== id);
        cachedFavorites = next;
        updateFavoriteCount();

        // Ensure all buttons match server state
        allMatchingBtns.forEach(b => b.classList.toggle('active', response.added));

        showToast(response.added ? "Added to favorites" : "Removed from favorites");

        // Re-render favorites page if we are on it
        if (document.getElementById("favorites-grid")) {
            renderFavoritesPage();
        }
      }
    } catch (err) {
      console.error("Wishlist toggle failed:", err);
      // Revert optimistic update
      const current = await getFavorites();
      const allMatchingBtns = document.querySelectorAll(`.fav-btn[data-id="${id}"]`);
      allMatchingBtns.forEach(b => b.classList.toggle('active', current.includes(id)));

      if (err.status === 401) {
          showToast("Please login to use wishlist");
      } else {
          showToast("Something went wrong. Please try again.");
      }
    }
  });
}

async function productCard(product) {
  const favs = await getFavorites();
  const favoriteActive = favs.includes(product.id) ? "active" : "";
  const images = product.images || product.gallery_images || [];
  const front = images[0] || product.main_image || product.thumbnail || "";
  const back = images[1] || front;
  const sizes = (product.sizes || []).map((size, index) => `<button type="button" class="radio-pill ${index === 0 ? "active" : ""}" data-value="${size}">${size}</button>`).join("");
  const colors = (product.colors || []).map((color, index) => {
    const hex = color.hex || color.hex_code || color.name || product.color_hex || "#51E2F5";
    return `<button type="button" class="radio-pill color-pill ${index === 0 ? "active" : ""}" data-value="${hex}" style="--swatch:${hex}"><span class="swatch"></span><span class="pill-text">${hex}</span></button>`;
  }).join("");
  const offerMarkup = product.offer ? `
    <div class="offer-chip-row">
      <span class="offer-label-chip">${product.offer.label}</span>
      ${product.isTrending ? '<span class="offer-label-chip muted-chip">Trending Deal</span>' : ""}
    </div>
    <div class="limited-badge" data-offer-countdown data-offer-end="${product.offer.endsAt}">Limited time</div>
  ` : "";
  const url = product.url || (product.slug ? `/products/${product.slug}/` : "#");
  const categoryName = product.categoryName || product.category || "";
  const description = product.desc || product.description || "";
  const price = product.price ?? product.current_price;
  const originalPrice = product.originalPrice ?? product.original_price ?? price;
  const discountPercent = product.discountPercent ?? product.discount_percent ?? 0;
  const highlight = product.offer?.highlight || (discountPercent ? "Special pricing" : "");
  const priceOld = discountPercent ? `<span class="price-old">${money(originalPrice)}</span><span class="price-off">${discountPercent}% OFF</span>` : "";
  const saveLine = highlight ? `<div class="save-line">${highlight}</div>` : "";
  return `
    <article class="product-card reveal" data-product-id="${product.id}" data-product-url="${url}">
      <div class="product-media" aria-label="${product.name}">
        <div class="flip-inner">
          <img class="front" src="${front}" alt="${product.name} front" loading="lazy">
          <img class="back" src="${back}" alt="${product.name} back" loading="lazy">
        </div>
        <button type="button" class="fav-btn ${favoriteActive}" data-id="${product.id}" title="Add to favorites"><i class="fa-regular fa-heart"></i></button>
        <div class="flip-hint">Tap to flip</div>
      </div>
      <div class="product-body">
        <p class="chip">${categoryName}</p><h3>${product.name}</h3><p class="tiny">${description}</p>
        <div class="price-block ${product.offer ? "has-offer" : ""}" ${product.offer ? `data-offer-expirable` : ""}><div class="price-line"><span class="price-now">${money(price)}</span>${priceOld}</div>${saveLine}${offerMarkup}</div>
        <div class="variant-stack"><label>Size</label><div class="radio-row" data-role="size">${sizes}</div>${colors ? `<label>Color</label><div class="radio-row" data-role="color">${colors}</div>` : ""}</div>
        ${product.stock > 0 ? '<button class="add-btn" type="button" data-add-cart>Add to cart</button>' : '<button class="add-btn" type="button" disabled>Out of stock</button>'}
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

    const cardHtmls = await Promise.all(data.products.map(productCard));
    grid.innerHTML = cardHtmls.join("") || "<p class='muted'>No matching products.</p>";

    initReveal();
    initProductOffers();
    updateFavoriteCount();
  };
  category?.addEventListener("change", apply);
  sort?.addEventListener("change", apply);
  search?.addEventListener("input", apply);
}

function initCardNavigation() {
  // Check if flip hint should be shown
  const hasSeenFlipHint = localStorage.getItem('gm_seen_flip_hint') === "1";
  if (hasSeenFlipHint) {
    document.querySelectorAll('.flip-hint').forEach(hint => hint.classList.add('hide'));
  }

  document.addEventListener("click", (event) => {
    const pill = event.target.closest(".radio-pill") || event.target.closest(".size-pill") || event.target.closest(".swatch-btn");
    if (pill) {
      const row = pill.closest(".radio-row") || pill.closest(".swatches-row");
      row?.querySelectorAll(".radio-pill, .size-pill, .swatch-btn").forEach((button) => button.classList.remove("active"));
      pill.classList.add("active");
      return;
    }

    const media = event.target.closest(".product-media");
    const isMobile = window.matchMedia("(hover: none)").matches || window.innerWidth <= 768;

    if (media && isMobile) {
      // Toggle flip only if clicking the media area
      media.classList.toggle("flipped");
      // Hide hint on first flip
      if (localStorage.getItem('gm_seen_flip_hint') !== "1") {
        localStorage.setItem('gm_seen_flip_hint', '1');
        document.querySelectorAll('.flip-hint').forEach(hint => hint.classList.add('hide'));
      }
      return;
    }

    const card = event.target.closest(".product-card");
    // If user clicks name (which is usually an H3 or link) or image on desktop
    const isLinkOrButton = event.target.closest("button, input, select, textarea, a, .radio-row, .swatches-row, .variant-selectors, .variant-group");

    if (card && !isLinkOrButton) {
        // Specifically for mobile: only navigate if NOT clicking media (which flips)
        if (isMobile && event.target.closest(".product-media")) return;

        if (card.dataset.productUrl && card.dataset.productUrl !== "#") {
          window.location.href = card.dataset.productUrl;
        }
    }
  });
}

async function renderFavoritesPage() {
  const target = document.getElementById("favorites-grid");
  const source = document.querySelector(".hidden-product-source");
  if (!target || !source) return;
  const wanted = await getFavorites();
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
