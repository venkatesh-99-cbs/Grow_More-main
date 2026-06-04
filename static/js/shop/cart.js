import { apiGet, apiPost } from "../services/api-service.js";
import { money, selectedValue } from "../core/utilities.js";

export async function refreshCart() {
  const list = document.getElementById("cart-items");
  const total = document.getElementById("cart-total-amount");
  const count = document.getElementById("cart-count");
  if (!list || !total) return;

  try {
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
        <div>
          <p>${item.name}</p>
          <small class="cart-variant-line">
            ${item.size || ""}
            ${item.color ? `<span class="cart-color-chip"><span class="cart-color-dot" style="background:${item.color}"></span>${item.color}</span>` : ""}
            x${item.qty}
          </small>
          ${item.offerLabel ? `<small class="offer-mini">${item.offerLabel}</small>` : ""}
        </div>
        <div class="cart-row-actions">
          <strong>${money(item.subtotal)}</strong>
          <button class="remove-btn" type="button" data-remove-cart="${item.id}">Remove</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Cart refresh failed:", err);
  }
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

  // Listen for the custom event from ProductCardManager
  document.addEventListener("add-to-cart", (e) => {
    const { productId, size, color, quantity } = e.detail;
    addToCart(productId, size, color, quantity);
  });

  refreshCart().catch(() => {});
}

export function toggleCart(force) {
  const cart = document.getElementById("cart-sidebar");
  const overlay = document.getElementById("cart-overlay");
  const open = typeof force === "boolean" ? force : !cart.classList.contains("active");
  cart?.classList.toggle("active", open);
  overlay?.classList.toggle("active", open);
}

async function addToCart(productId, size, color, quantity = 1) {
  try {
    const cart = await apiPost("/cart/add/", {
      product_id: productId,
      quantity: quantity,
      size: size,
      color: color,
    });

    await refreshCart();
    toggleCart(true);

    if (window.notifications) {
      window.notifications.success("Added to cart successfully");
    }
  } catch (err) {
    console.error("Add to cart failed:", err);
    const errorMsg = err.error || "Failed to add to cart";
    if (window.notifications) {
      window.notifications.error(errorMsg);
    }
  }
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

  // Handled by ProductCardManager or custom event now,
  // but keep a fallback for simple buttons if needed.
  const scope = button.closest("[data-product-id]");
  if (!scope) return;
}
