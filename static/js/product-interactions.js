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
  }

  attachEventListeners() {
    // Size selection
    const sizeButtons = this.card.querySelectorAll('[data-role="size"] button');
    sizeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => this.handleSizeSelect(e, btn));
    });

    // Color selection
    const colorButtons = this.card.querySelectorAll('[data-role="color"] button');
    colorButtons.forEach(btn => {
      btn.addEventListener('click', (e) => this.handleColorSelect(e, btn));
    });

    // Add to cart
    const addBtn = this.card.querySelector('[data-add-cart]');
    if (addBtn) {
      addBtn.addEventListener('click', () => this.handleAddToCart());
    }

    // Favorite button
    const favBtn = this.card.querySelector('[data-favorite-id]');
    if (favBtn) {
      favBtn.addEventListener('click', () => this.handleFavorite(favBtn));
    }
  }

  handleSizeSelect(e, btn) {
    e.preventDefault();
    if (btn.disabled) return;

    // Update active state
    this.card.querySelectorAll('[data-role="size"] button').forEach(b => {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    this.selectedSize = btn.dataset.value;

    // Show stock info
    const stockInfo = btn.querySelector('[style*="display: block"]');
    if (stockInfo) {
      notifications.info(`${btn.dataset.value} size selected - ${stockInfo.textContent.trim()}`, {
        title: 'Size Selected',
        duration: 2000
      });
    }
  }

  handleColorSelect(e, btn) {
    e.preventDefault();

    // Update active state
    this.card.querySelectorAll('[data-role="color"] button').forEach(b => {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    this.selectedColor = btn.dataset.value;

    // Animate color change
    const colorName = btn.querySelector('.pill-text')?.textContent || btn.dataset.value;
    notifications.info(`Color: ${colorName}`, {
      title: 'Color Selected',
      duration: 1500
    });
  }

  handleAddToCart() {
    const size = this.selectedSize || this.card.querySelector('[data-role="size"] button.active')?.dataset.value;
    const color = this.selectedColor || this.card.querySelector('[data-role="color"] button.active')?.dataset.value;

    if (!size) {
      notifications.warning('Please select a size', { title: 'Size Required' });
      return;
    }

    // Trigger custom event for cart system
    const event = new CustomEvent('add-to-cart', {
      detail: {
        productId: this.productId,
        size: size,
        color: color,
        quantity: 1
      }
    });
    document.dispatchEvent(event);
  }

  handleFavorite(btn) {
    const id = btn.dataset.favoriteId;
    const isActive = btn.classList.contains('active');

    // Toggle active state
    btn.classList.toggle('active');

    // Trigger custom event
    const event = new CustomEvent('toggle-favorite', {
      detail: {
        productId: id,
        isFavorite: !isActive
      }
    });
    document.dispatchEvent(event);
  }

  static initAll() {
    document.querySelectorAll('.product-card').forEach(card => {
      new ProductCardManager(card);
    });
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  ProductCardManager.initAll();
});

// Listen for dynamically added cards
const observer = new MutationObserver((mutations) => {
  mutations.forEach(mutation => {
    mutation.addedNodes.forEach(node => {
      if (node.classList && node.classList.contains('product-card')) {
        new ProductCardManager(node);
      }
    });
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Export for external use
window.ProductCardManager = ProductCardManager;
