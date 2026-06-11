/**
 * Advanced Product Filtering System
 * Supports: brand, category, price range, size, color filters
 * AJAX-based with URL state preservation
 */

class ProductFilterManager {
  constructor(options = {}) {
    this.containerSelector = options.containerSelector || '.products-grid';
    this.filterSelector = options.filterSelector || '.product-filters';
    this.paginationSelector = options.paginationSelector || '.pagination';
    this.apiUrl = options.apiUrl || '/api/filter/';
    this.optionsUrl = options.optionsUrl || '/api/filter-options/';
    this.searchUrl = options.searchUrl || '/api/search/';
    
    this.filters = {
      brands: [],
      categories: [],
      colors: [],
      sizes: [],
      priceMin: null,
      priceMax: null,
      search: '',
    };

    this.page = 1;
    this.isLoading = false;
    this.debounceTimer = null;

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadFiltersFromURL();
  }

  /**
   * Setup filter UI event listeners
   */
  setupEventListeners() {
    const filterContainer = document.querySelector(this.filterSelector);
    if (!filterContainer) return;

    // Brand checkboxes
    filterContainer.querySelectorAll('[data-filter-brand]').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => this.handleBrandFilter(e));
    });

    // Category checkboxes
    filterContainer.querySelectorAll('[data-filter-category]').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => this.handleCategoryFilter(e));
    });

    // Color swatches
    filterContainer.querySelectorAll('[data-filter-color]').forEach(swatch => {
      swatch.addEventListener('click', (e) => this.handleColorFilter(e));
    });

    // Size buttons
    filterContainer.querySelectorAll('[data-filter-size]').forEach(button => {
      button.addEventListener('click', (e) => this.handleSizeFilter(e));
    });

    // Price range inputs
    const priceMinInput = filterContainer.querySelector('[data-price-min]');
    const priceMaxInput = filterContainer.querySelector('[data-price-max]');
    const priceApplyBtn = filterContainer.querySelector('[data-price-apply]');

    if (priceMinInput && priceMaxInput) {
      [priceMinInput, priceMaxInput].forEach(input => {
        input.addEventListener('change', (e) => {
          this.filters.priceMin = parseInt(priceMinInput.value) || null;
          this.filters.priceMax = parseInt(priceMaxInput.value) || null;
          this.page = 1;
          this.applyFilters();
        });
      });
    }

    if (priceApplyBtn) {
      priceApplyBtn.addEventListener('click', () => {
        this.filters.priceMin = parseInt(priceMinInput.value) || null;
        this.filters.priceMax = parseInt(priceMaxInput.value) || null;
        this.page = 1;
        this.applyFilters();
      });
    }

    // Clear filters button
    const clearBtn = filterContainer.querySelector('[data-clear-filters]');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearAllFilters());
    }

    // Search input with debounce
    const searchInput = filterContainer.querySelector('[data-search-products]');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filters.search = e.target.value;
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          this.page = 1;
          this.applyFilters();
        }, 300);
      });
    }
  }

  /**
   * Handle brand filter toggle
   */
  handleBrandFilter(e) {
    const brandId = e.target.dataset.filterBrand;
    if (e.target.checked) {
      if (!this.filters.brands.includes(brandId)) {
        this.filters.brands.push(brandId);
      }
    } else {
      this.filters.brands = this.filters.brands.filter(id => id !== brandId);
    }
    this.page = 1;
    this.applyFilters();
  }

  /**
   * Handle category filter toggle
   */
  handleCategoryFilter(e) {
    const categoryId = e.target.dataset.filterCategory;
    if (e.target.checked) {
      if (!this.filters.categories.includes(categoryId)) {
        this.filters.categories.push(categoryId);
      }
    } else {
      this.filters.categories = this.filters.categories.filter(id => id !== categoryId);
    }
    this.page = 1;
    this.applyFilters();
  }

  /**
   * Handle color filter toggle
   */
  handleColorFilter(e) {
    e.preventDefault();
    const colorId = e.currentTarget.dataset.filterColor;
    const isActive = e.currentTarget.classList.contains('active');

    if (!isActive) {
      // Allow multi-select
      this.filters.colors.push(colorId);
      e.currentTarget.classList.add('active');
    } else {
      // Deselect
      this.filters.colors = this.filters.colors.filter(id => id !== colorId);
      e.currentTarget.classList.remove('active');
    }
    this.page = 1;
    this.applyFilters();
  }

  /**
   * Handle size filter toggle (single select)
   */
  handleSizeFilter(e) {
    e.preventDefault();
    const sizeId = e.currentTarget.dataset.filterSize;
    const isActive = e.currentTarget.classList.contains('active');

    // Remove active from all size buttons
    document.querySelectorAll('[data-filter-size]').forEach(btn => {
      btn.classList.remove('active');
    });

    if (!isActive) {
      this.filters.sizes = [sizeId];
      e.currentTarget.classList.add('active');
    } else {
      this.filters.sizes = [];
      e.currentTarget.classList.remove('active');
    }
    this.page = 1;
    this.applyFilters();
  }

  /**
   * Apply current filters via AJAX
   */
  async applyFilters() {
    if (this.isLoading) return;
    this.isLoading = true;

    try {
      // Build query parameters
      const params = new URLSearchParams();
      
      if (this.filters.brands.length) {
        params.append('brands', this.filters.brands.join(','));
      }
      if (this.filters.categories.length) {
        params.append('categories', this.filters.categories.join(','));
      }
      if (this.filters.colors.length) {
        params.append('colors', this.filters.colors.join(','));
      }
      if (this.filters.sizes.length) {
        params.append('sizes', this.filters.sizes.join(','));
      }
      if (this.filters.priceMin) {
        params.append('price_min', this.filters.priceMin);
      }
      if (this.filters.priceMax) {
        params.append('price_max', this.filters.priceMax);
      }
      if (this.filters.search) {
        params.append('search', this.filters.search);
      }
      params.append('page', this.page);

      // Update URL
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState({ filters: this.filters, page: this.page }, '', newUrl);

      // Show loading state
      this.showLoadingState();

      // Fetch filtered products
      const response = await fetch(`${this.apiUrl}?${params.toString()}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update product grid
      this.updateProductGrid(data.products || []);

      // Update pagination
      if (data.pagination) {
        this.updatePagination(data.pagination);
      }

      // Show result count
      this.updateResultCount(data.count || 0);

      // Notify about filters applied
      this.showFilterNotification(data.count || 0);

    } catch (error) {
      console.error('Filter error:', error);
      notifications?.error('Failed to apply filters. Please try again.');
    } finally {
      this.isLoading = false;
      this.hideLoadingState();
    }
  }

  /**
   * Update product grid with new results
   */
  updateProductGrid(products) {
    const container = document.querySelector(this.containerSelector);
    if (!container) return;

    if (products.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
          <p style="font-size: 1.1rem; color: rgba(0,0,0,0.5);">
            No products found matching your filters.
          </p>
          <button 
            style="margin-top: 20px; padding: 10px 24px; background: var(--bright-blue); color: white; border: none; border-radius: 20px; cursor: pointer;"
            onclick="document.querySelector('[data-clear-filters]')?.click()"
          >
            Clear Filters
          </button>
        </div>
      `;
      return;
    }

    // Render products (simple HTML - customize based on your product card HTML)
    container.innerHTML = products.map(product => this.renderProductCard(product)).join('');

    // Re-initialize product interactions on new cards
    if (window.ProductCardManager) {
      ProductCardManager.initAll();
    }
  }

  /**
   * Render individual product card
   */
  renderProductCard(product) {
    const discount = product.discount_percentage || 0;
    const color = product.color_hex || product.colors?.[0]?.hex || product.colors?.[0]?.hex_code || "#51E2F5";
    const url = product.slug ? `/products/${product.slug}/` : "#";
    const mainImage = product.image || '/media/placeholder.jpg';
    const galleryImage = product.images?.[1] || mainImage;

    return `
      <article class="product-card reveal" data-product-id="${product.id}" data-product-url="${url}">
        <div class="product-media" aria-label="${product.name}">
          <div class="flip-inner">
            <img class="front" src="${mainImage}" alt="${product.name} front" loading="lazy">
            <img class="back" src="${galleryImage}" alt="${product.name} back" loading="lazy">
          </div>
          ${discount > 0 ? `<div class="discount-badge">${discount}% OFF</div>` : ""}
          <button type="button" class="fav-btn" data-id="${product.id}" aria-label="Add to favorites"><i class="fa-regular fa-heart"></i></button>
          <div class="flip-hint">Tap to flip</div>
        </div>
        <div class="product-body">
          <span class="product-category">${product.brand || product.category}</span>
          <h3 class="product-title">${product.name}</h3>
          <div class="product-price-row">
            <span class="price-now">Rs. ${product.current_price}</span>
            ${product.original_price && product.original_price > product.current_price ? `<span class="price-old">Rs. ${product.original_price}</span>` : ""}
          </div>
          <div class="swatches-row" data-role="color">
            <button type="button" class="swatch-btn active" data-value="${color}" style="background-color:${color}" title="${color}"></button>
          </div>
          <button class="add-btn" type="button" data-add-cart>Add to Cart</button>
        </div>
      </article>
    `;
  }

  /**
   * Update pagination UI
   */
  updatePagination(pagination) {
    const container = document.querySelector(this.paginationSelector);
    if (!container) return;

    let html = '';

    if (pagination.has_previous) {
      html += `<button class="page-btn" data-page="${pagination.current_page - 1}">← Previous</button>`;
    }

    for (let i = 1; i <= pagination.total_pages; i++) {
      if (i === pagination.current_page) {
        html += `<button class="page-btn active">${i}</button>`;
      } else {
        html += `<button class="page-btn" data-page="${i}">${i}</button>`;
      }
    }

    if (pagination.has_next) {
      html += `<button class="page-btn" data-page="${pagination.current_page + 1}">Next →</button>`;
    }

    container.innerHTML = html;

    // Add page button listeners
    container.querySelectorAll('[data-page]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.page = parseInt(e.target.dataset.page);
        this.applyFilters();
        window.scrollTo({ top: document.querySelector(this.containerSelector)?.offsetTop - 100, behavior: 'smooth' });
      });
    });
  }

  /**
   * Update result count display
   */
  updateResultCount(count) {
    const countEl = document.querySelector('[data-filter-count]');
    if (countEl) {
      countEl.textContent = `${count} product${count !== 1 ? 's' : ''} found`;
    }
  }

  /**
   * Show result notification
   */
  showFilterNotification(count) {
    if (window.notifications && this.filters.brands.length + this.filters.categories.length + this.filters.colors.length + this.filters.sizes.length > 0) {
      notifications.info(`Showing ${count} product${count !== 1 ? 's' : ''}`);
    }
  }

  /**
   * Show loading skeleton state
   */
  showLoadingState() {
    const container = document.querySelector(this.containerSelector);
    if (container && window.SkeletonLoader) {
      SkeletonLoader.loadProducts(container, 6, 500);
    }
  }

  /**
   * Hide loading state
   */
  hideLoadingState() {
    // Loading state is auto-replaced by actual content
  }

  /**
   * Load filters from URL parameters
   */
  loadFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);

    if (params.has('brands')) {
      this.filters.brands = params.get('brands').split(',');
    }
    if (params.has('categories')) {
      this.filters.categories = params.get('categories').split(',');
    }
    if (params.has('colors')) {
      this.filters.colors = params.get('colors').split(',');
    }
    if (params.has('sizes')) {
      this.filters.sizes = params.get('sizes').split(',');
    }
    if (params.has('price_min')) {
      this.filters.priceMin = parseInt(params.get('price_min'));
    }
    if (params.has('price_max')) {
      this.filters.priceMax = parseInt(params.get('price_max'));
    }
    if (params.has('search')) {
      this.filters.search = params.get('search');
    }
    this.page = parseInt(params.get('page')) || 1;

    // Update UI to match loaded filters
    this.updateFilterUI();
  }

  /**
   * Update filter UI checkboxes/buttons to match current filters
   */
  updateFilterUI() {
    // Update brand checkboxes
    document.querySelectorAll('[data-filter-brand]').forEach(checkbox => {
      checkbox.checked = this.filters.brands.includes(checkbox.dataset.filterBrand);
    });

    // Update category checkboxes
    document.querySelectorAll('[data-filter-category]').forEach(checkbox => {
      checkbox.checked = this.filters.categories.includes(checkbox.dataset.filterCategory);
    });

    // Update color swatches
    document.querySelectorAll('[data-filter-color]').forEach(swatch => {
      if (this.filters.colors.includes(swatch.dataset.filterColor)) {
        swatch.classList.add('active');
      } else {
        swatch.classList.remove('active');
      }
    });

    // Update size buttons
    document.querySelectorAll('[data-filter-size]').forEach(btn => {
      if (this.filters.sizes.includes(btn.dataset.filterSize)) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update price inputs
    const priceMinInput = document.querySelector('[data-price-min]');
    const priceMaxInput = document.querySelector('[data-price-max]');
    if (priceMinInput && this.filters.priceMin) {
      priceMinInput.value = this.filters.priceMin;
    }
    if (priceMaxInput && this.filters.priceMax) {
      priceMaxInput.value = this.filters.priceMax;
    }

    // Update search input
    const searchInput = document.querySelector('[data-search-products]');
    if (searchInput && this.filters.search) {
      searchInput.value = this.filters.search;
    }
  }

  /**
   * Clear all filters
   */
  clearAllFilters() {
    this.filters = {
      brands: [],
      categories: [],
      colors: [],
      sizes: [],
      priceMin: null,
      priceMax: null,
      search: '',
    };
    this.page = 1;

    // Reset UI
    document.querySelectorAll('[data-filter-brand], [data-filter-category]').forEach(el => {
      el.checked = false;
    });
    document.querySelectorAll('[data-filter-color], [data-filter-size]').forEach(el => {
      el.classList.remove('active');
    });

    const priceMinInput = document.querySelector('[data-price-min]');
    const priceMaxInput = document.querySelector('[data-price-max]');
    if (priceMinInput) priceMinInput.value = '';
    if (priceMaxInput) priceMaxInput.value = '';

    const searchInput = document.querySelector('[data-search-products]');
    if (searchInput) searchInput.value = '';

    // Update URL and apply
    window.history.replaceState({}, '', window.location.pathname);
    this.applyFilters();

    notifications?.success('Filters cleared');
  }
}

// Global instance
window.ProductFilterManager = ProductFilterManager;
