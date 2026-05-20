import { apiGet, apiPost } from "../services/api-service.js";
import { money, selectedValue, showToast } from "../core/utilities.js";

export async function refreshCart() {
  const list = document.getElementById("cart-items");
  const total = document.getElementById("cart-total-amount");
  const count = document.getElementById("cart-count");
  if (!list || !total) return;
  const cart = await apiGet("/cart/");
  count.textContent = String(cart.count || 0);
  total.textContent = money(cart.total);
  if (!cart.items.length) {
    list.innerHTML = '<p class="muted">Your cart is empty</p>';
    return;
  }
  list.innerHTML = cart.items.map((item) => `
    <div class="cart-row cart-row-rich">
      <img src="${item.image}" alt="${item.name}">
      <div><p>${item.name}</p><small>${item.size || ""}${item.color ? `, ${item.color}` : ""} x${item.qty}</small>${item.offerLabel ? `<small class="offer-mini">${item.offerLabel}</small>` : ""}</div>
      <div class="cart-row-actions"><strong>${money(item.subtotal)}</strong><button class="remove-btn" type="button" data-remove-cart="${item.id}">Remove</button></div>
    </div>
  `).join("");
}

export function initCartUI() {
  const sidebar = document.getElementById("cart-sidebar");
  if (!sidebar) return;
  if (!document.getElementById("cart-overlay")) {
    const overlay = document.createElement("div");
    overlay.id = "cart-overlay";
    overlay.className = "cart-overlay";
    overlay.addEventListener("click", () => toggleCart(false));
    document.body.appendChild(overlay);
  }
  const close = document.createElement("button");
  close.className = "cart-close";
  close.type = "button";
  close.innerHTML = "&times;";
  close.addEventListener("click", () => toggleCart(false));
  if (!sidebar.querySelector(".cart-close")) sidebar.prepend(close);
  document.querySelectorAll("[data-cart-toggle]").forEach((btn) => btn.addEventListener("click", () => toggleCart()));
  document.querySelector("[data-checkout-button]")?.addEventListener("click", (event) => {
    window.location.href = event.currentTarget.dataset.checkoutUrl;
  });
  document.addEventListener("click", handleCartClick);
  refreshCart().catch(() => {});
}

function toggleCart(force) {
  const cart = document.getElementById("cart-sidebar");
  const overlay = document.getElementById("cart-overlay");
  const open = typeof force === "boolean" ? force : !cart.classList.contains("active");
  cart?.classList.toggle("active", open);
  overlay?.classList.toggle("active", open);
}

async function handleCartClick(event) {
  const remove = event.target.closest("[data-remove-cart]");
  if (remove) {
    await apiPost(`/cart/items/${remove.dataset.removeCart}/remove/`);
    await refreshCart();
    return;
  }
  const button = event.target.closest("[data-add-cart]");
  if (!button) return;
  const scope = button.closest("[data-product-id]");
  if (!scope) return;
  button.disabled = true;
  try {
    await apiPost("/cart/add/", {
      product_id: scope.dataset.productId,
      quantity: Number(document.getElementById("detail-qty")?.value || 1),
      size: selectedValue(scope, "size"),
      color: selectedValue(scope, "color"),
    });
    await refreshCart();
    showToast("Added to cart");
  } finally {
    button.disabled = false;
  }
}
