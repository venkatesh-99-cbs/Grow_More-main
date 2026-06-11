/**
 * Premium Product Card Interactions
 * Handles color swatches, size selection, and stock indicators
 */

class ProductCardManager {
  constructor(cardElement) {
    this.card = cardElement;
    this.productId = cardElement.dataset.productId;
    this.selectedSize = null;
    this.selectedColor = null;
    this.init();
  }

  init() {
    if (this.card.dataset.managerInitialized === 'true') return;
    this.card.dataset.managerInitialized = 'true';

    this.attachEventListeners();
    // Pre-select first available size and color
    this.autoSelectDefaults();
  }

  autoSelectDefaults() {
    const firstSize = this.card.querySelector('[data-role="size"] .size-pill:not([disabled]), [data-role="size"] button:not([disabled])');
    if (firstSize) this.selectSize(firstSize);

    const firstColor = this.card.querySelector('[data-role="color"] .swatch-btn, [data-role="color"] button');
    if (firstColor) this.selectColor(firstColor);
  }

  attachEventListeners() {
    // Size selection
    this.card.querySelectorAll('[data-role="size"] button, .size-pill').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.selectSize(btn);
      });
    });

    // Color selection
    this.card.querySelectorAll('[data-role="color"] button, .swatch-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.selectColor(btn);
      });
    });

    // Add to cart
    const addBtn = this.card.querySelector('[data-add-cart]');
    if (addBtn) {
      addBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.handleAddToCart();
      });
    }

    // Favorite button - Handled globally by products.js
    const favBtn = this.card.querySelector('.fav-btn[data-id]');
    if (favBtn) {
      favBtn.addEventListener('click', (e) => {
        // We let it bubble so products.js can handle it,
        // but we ensure it doesn't trigger card navigation if any
      });
    }

    // Note: Card navigation is handled globally in products.js to avoid conflicts with flip logic
  }

  selectSize(btn) {
    if (btn.disabled) return;
    this.card.querySelectorAll('[data-role="size"] button, [data-role="size"] .size-pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    this.selectedSize = btn.dataset.value;

    // Update stock message if applicable
    const stockMsg = btn.title;
    const statusEl = this.card.querySelector('.stock-status');
    if (statusEl) {
        statusEl.textContent = stockMsg;
        statusEl.className = 'stock-status ' + (stockMsg.includes('Only') ? 'low' : '');
    }
  }

  selectColor(btn) {
    this.card.querySelectorAll('[data-role="color"] button, [data-role="color"] .swatch-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    this.selectedColor = btn.dataset.value;
  }

  handleAddToCart() {
    if (!this.selectedSize && this.card.querySelector('[data-role="size"]')) {
      if (window.notifications) {
        window.notifications.warning('Please select a size first');
      }
      return;
    }

    const qtyInput = this.card.querySelector('#detail-qty') || this.card.querySelector('[name="quantity"]');
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    // Dispatch event that cart.js listens for
    const event = new CustomEvent('add-to-cart', {
      detail: {
        productId: this.productId,
        size: this.selectedSize,
        color: this.selectedColor,
        quantity: quantity
      }
    });
    document.dispatchEvent(event);
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  static initAll() {
    document.querySelectorAll('.product-card').forEach(card => {
      if (!card.dataset.initialized) {
        new ProductCardManager(card);
        card.dataset.initialized = 'true';
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ProductCardManager.initAll();
});

// Watch for new products (e.g. from infinite scroll or filters)
const observer = new MutationObserver(() => {
  ProductCardManager.initAll();
});
observer.observe(document.body, { childList: true, subtree: true });

window.ProductCardManager = ProductCardManager;
