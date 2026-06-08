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
    this.attachEventListeners();
    // Pre-select first available size and color
    this.autoSelectDefaults();
  }

  autoSelectDefaults() {
    const firstSize = this.card.querySelector('[data-role="size"] button:not([disabled])');
    if (firstSize) this.selectSize(firstSize);

    const firstColor = this.card.querySelector('[data-role="color"] button');
    if (firstColor) this.selectColor(firstColor);
  }

  attachEventListeners() {
    // Size selection
    this.card.querySelectorAll('[data-role="size"] button').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.selectSize(btn);
      });
    });

    // Color selection
    this.card.querySelectorAll('[data-role="color"] button').forEach(btn => {
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

    // Favorite button
    const favBtn = this.card.querySelector('[data-favorite-id]');
    if (favBtn) {
      favBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.handleFavorite(favBtn);
      });
    }

    // Make entire card clickable to go to detail page
    this.card.addEventListener('click', (e) => {
        // Don't navigate if clicking an action button
        if (e.target.closest('button') || e.target.closest('.radio-pill')) return;
        const url = this.card.dataset.productUrl;
        if (url) window.location.href = url;
    });
  }

  selectSize(btn) {
    if (btn.disabled) return;
    this.card.querySelectorAll('[data-role="size"] button').forEach(b => b.classList.remove('active'));
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
    this.card.querySelectorAll('[data-role="color"] button').forEach(b => b.classList.remove('active'));
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

  handleFavorite(btn) {
    const id = btn.dataset.favoriteId;
    const isActive = btn.classList.contains('active');
    btn.classList.toggle('active');

    const event = new CustomEvent('toggle-favorite', {
      detail: { productId: id, isFavorite: !isActive }
    });
    document.dispatchEvent(event);

    if (window.notifications) {
        window.notifications.success(isActive ? 'Removed from favorites' : 'Added to favorites');
    }
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
