/**
 * Shop Filtering Manager
 * Handles AJAX product filtering, search, and sorting.
 */

window.ShopManager = class ShopManager {
    constructor() {
        this.grid = document.getElementById('product-grid');
        this.resultsCount = document.getElementById('results-count');
        this.filters = {
            q: '',
            categories: [],
            brands: [],
            minPrice: '',
            maxPrice: '',
            sizes: [],
            sort: 'featured'
        };

        if (this.grid) {
            this.init();
        }
    }

    init() {
        this.initMobileUI();
        this.bindEvents();
        this.triggerReveal();
    }

    initMobileUI() {
        // Mobile Filter Drawer
        const trigger = document.getElementById('mobile-filter-trigger');
        const sidebar = document.getElementById('shop-sidebar');
        const close = document.getElementById('mobile-filter-close');

        if (trigger && sidebar) {
            trigger.addEventListener('click', () => {
                sidebar.classList.add('active');
            });
        }

        if (close && sidebar) {
            close.addEventListener('click', () => {
                sidebar.classList.remove('active');
            });
        }

        // Collapsible Sections
        document.querySelectorAll('.filter-section.collapsible .filter-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const parent = toggle.closest('.filter-section');
                parent.classList.toggle('active');
            });
        });
    }

    bindEvents() {
        // Search
        const searchInput = document.getElementById('shop-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.q = e.target.value;
                this.debouncedFetch();
            });
        }

        // Categories & Brands
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', () => {
                const name = cb.name;
                const value = cb.value;
                if (name === 'category') {
                    if (value === 'all') {
                        if (cb.checked) {
                            this.filters.categories = [];
                            document.querySelectorAll('input[name="category"]:not([value="all"])').forEach(c => c.checked = false);
                        }
                    } else {
                        if (cb.checked) {
                            const allCb = document.querySelector('input[name="category"][value="all"]');
                            if (allCb) allCb.checked = false;
                            this.filters.categories.push(value);
                        } else {
                            this.filters.categories = this.filters.categories.filter(v => v !== value);
                        }
                    }
                } else if (name === 'brand') {
                    if (cb.checked) this.filters.brands.push(value);
                    else this.filters.brands = this.filters.brands.filter(v => v !== value);
                }
                this.fetchProducts();
            });
        });

        // Prices
        ['min-price', 'max-price'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', (e) => {
                    this.filters[id === 'min-price' ? 'minPrice' : 'maxPrice'] = e.target.value;
                    this.debouncedFetch();
                });
            }
        });

        // Sizes
        document.querySelectorAll('.filter-size').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.classList.toggle('active');
                const size = btn.dataset.size;
                if (btn.classList.contains('active')) this.filters.sizes.push(size);
                else this.filters.sizes = this.filters.sizes.filter(s => s !== size);
                this.fetchProducts();
            });
        });

        // Sort
        const sortSelect = document.getElementById('shop-sort');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.filters.sort = e.target.value;
                this.fetchProducts();
            });
        }

        // Clear
        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                window.location.href = window.location.pathname;
            });
        }
    }

    debouncedFetch() {
        clearTimeout(this.timeout);
        this.timeout = setTimeout(() => this.fetchProducts(), 500);
    }

    async fetchProducts() {
        if (!this.grid) return;
        this.grid.style.opacity = '0.5';
        await this.fetchRenderedGrid(this.filters);
        this.grid.style.opacity = '1';
    }

    async fetchRenderedGrid(filters) {
        const params = new URLSearchParams();
        if (filters.q) params.append('q', filters.q);
        filters.categories.forEach(c => params.append('category', c));
        filters.brands.forEach(b => params.append('brand', b));
        if (filters.minPrice) params.append('min_price', filters.minPrice);
        if (filters.maxPrice) params.append('max_price', filters.maxPrice);
        filters.sizes.forEach(s => params.append('size', s));
        params.append('sort', filters.sort);
        params.append('partial', 'true');

        try {
            const response = await fetch(`/shop/?${params.toString()}`);
            const html = await response.text();
            this.grid.innerHTML = html;

            // Update count
            const count = this.grid.querySelectorAll('.product-card').length;
            if (this.resultsCount) {
                this.resultsCount.textContent = `Showing ${count} products`;
            }

            // Trigger reveal & interactions
            this.triggerReveal();
            if (window.ProductCardManager) {
                window.ProductCardManager.initAll();
            }
        } catch (err) {
            console.error("Filter fetch failed:", err);
        }
    }

    triggerReveal() {
        if (!this.grid) return;
        this.grid.querySelectorAll('.reveal').forEach((el, i) => {
            setTimeout(() => el.classList.add('active'), i * 100);
        });
    }
};

// Auto-init on DOMContentLoaded if in shop page
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('.shop-sidebar')) {
            window.shopManager = new window.ShopManager();
        }
    });
} else {
    if (document.querySelector('.shop-sidebar')) {
        window.shopManager = new window.ShopManager();
    }
}
