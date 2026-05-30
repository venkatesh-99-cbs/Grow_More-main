# Shop Template Integration Guide

## Overview

This guide provides the complete template structure for the shop page with advanced product filtering, responsive layout, and premium UI.

## Shop Page Structure

```html
{% extends 'base.html' %} {% load static %} {% block title %}Shop | Grow More{%
endblock %} {% block content %}
<main class="shop-page">
  <div class="container">
    <!-- Page Header -->
    <section class="shop-header">
      <div class="shop-header-content">
        <h1>Summer Collection 2026</h1>
        <p class="shop-tagline">
          Explore our complete range of premium summer menswear
        </p>

        <!-- Search Box -->
        <div class="search-box">
          <input
            type="text"
            placeholder="Search products..."
            data-search-products
            aria-label="Search products"
          />
          <svg
            class="search-icon"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
        </div>
      </div>
    </section>

    <!-- Products with Filters -->
    <div class="products-container">
      <!-- Filter Sidebar -->
      <aside class="product-filters">
        <!-- Brands Filter -->
        <div class="filter-group">
          <label class="filter-title">Brands</label>
          <div class="filter-options">
            {% for brand in available_brands %}
            <div class="filter-checkbox">
              <input
                type="checkbox"
                id="brand-{{ brand.id }}"
                name="brand"
                data-filter-brand="{{ brand.id }}"
                aria-label="Filter by {{ brand.name }}"
              />
              <label for="brand-{{ brand.id }}">{{ brand.name }}</label>
            </div>
            {% endfor %}
          </div>
        </div>

        <!-- Categories Filter -->
        <div class="filter-group">
          <label class="filter-title">Categories</label>
          <div class="filter-options">
            {% for category in available_categories %}
            <div class="filter-checkbox">
              <input
                type="checkbox"
                id="cat-{{ category.id }}"
                name="category"
                data-filter-category="{{ category.id }}"
                aria-label="Filter by {{ category.name }}"
              />
              <label for="cat-{{ category.id }}">{{ category.name }}</label>
            </div>
            {% endfor %}
          </div>
        </div>

        <!-- Colors Filter -->
        <div class="filter-group">
          <label class="filter-title">Colors</label>
          <div class="color-swatches">
            {% for color in available_colors %}
            <button
              class="color-swatch"
              data-filter-color="{{ color.id }}"
              style="background-color: {{ color.hex_code }};"
              title="{{ color.name }}"
              aria-label="Filter by {{ color.name }}"
            ></button>
            {% endfor %}
          </div>
        </div>

        <!-- Sizes Filter -->
        <div class="filter-group">
          <label class="filter-title">Sizes</label>
          <div class="size-buttons">
            {% for size in available_sizes %}
            <button
              class="size-btn"
              data-filter-size="{{ size }}"
              aria-label="Filter by size {{ size }}"
            >
              {{ size }}
            </button>
            {% endfor %}
          </div>
        </div>

        <!-- Price Range Filter -->
        <div class="filter-group">
          <label class="filter-title">Price Range</label>
          <div class="price-inputs">
            <input
              type="number"
              class="price-input"
              data-price-min
              placeholder="Min"
              min="0"
              aria-label="Minimum price"
            />
            <input
              type="number"
              class="price-input"
              data-price-max
              placeholder="Max"
              min="0"
              aria-label="Maximum price"
            />
          </div>
          <button class="price-apply-btn" data-price-apply>Apply Price</button>
        </div>

        <!-- Clear Filters -->
        <button
          class="clear-filters-btn"
          data-clear-filters
          aria-label="Clear all filters"
        >
          Clear All Filters
        </button>
      </aside>

      <!-- Products Grid -->
      <section class="products-section">
        <!-- Result Count -->
        <div class="filter-count" data-filter-count>
          {% if products %} {{ products|length }} product{{
          products|length|pluralize }} {% else %} No products found {% endif %}
        </div>

        <!-- Products Grid -->
        <div class="products-grid">
          {% for product in products %} {% include 'partials/product_card.html'
          with product=product %} {% empty %}
          <div
            style="grid-column: 1/-1; text-align: center; padding: 60px 20px;"
          >
            <p style="font-size: 1.1rem; color: rgba(0,0,0,0.5);">
              No products found. Try adjusting your filters.
            </p>
            <button
              style="margin-top: 20px; padding: 10px 24px; background: var(--bright-blue); color: white; border: none; border-radius: 20px; cursor: pointer;"
              onclick="document.querySelector('[data-clear-filters]')?.click()"
            >
              Clear Filters
            </button>
          </div>
          {% endfor %}
        </div>

        <!-- Pagination -->
        {% if paginator.num_pages > 1 %}
        <nav class="pagination" aria-label="Product pagination">
          {% if page_obj.has_previous %}
          <a href="?page=1" class="page-btn" title="First page">«</a>
          <a href="?page={{ page_obj.previous_page_number }}" class="page-btn"
            >← Previous</a
          >
          {% endif %} {% for num in paginator.page_range %} {% if
          page_obj.number == num %}
          <button class="page-btn active" aria-current="page">{{ num }}</button>
          {% elif num > page_obj.number|add:'-3' and num <
          page_obj.number|add:'3' %}
          <a href="?page={{ num }}" class="page-btn">{{ num }}</a>
          {% endif %} {% endfor %} {% if page_obj.has_next %}
          <a href="?page={{ page_obj.next_page_number }}" class="page-btn"
            >Next →</a
          >
          <a
            href="?page={{ paginator.num_pages }}"
            class="page-btn"
            title="Last page"
            >»</a
          >
          {% endif %}
        </nav>
        {% endif %}
      </section>
    </div>
  </div>
</main>

<script>
  // Initialize product filter manager
  document.addEventListener("DOMContentLoaded", () => {
    new ProductFilterManager({
      containerSelector: ".products-grid",
      filterSelector: ".product-filters",
      paginationSelector: ".pagination",
      apiUrl: '{% url "products:api_filter" %}',
    });
  });
</script>
{% endblock %}
```

## Views Configuration

Update your `products/views.py` to support filtering:

```python
from django.shortcuts import render
from products.models import Product, Brand, Category, ColorVariant, SizeStock
from django.core.paginator import Paginator
from django.db.models import Q

def shop(request):
    """
    Shop page with product listing and filtering
    """

    # Get all active products
    products = Product.objects.filter(is_active=True).select_related(
        'brand', 'category'
    ).prefetch_related('colors', 'sizestock_set')

    # Apply filters from query parameters (optional server-side filtering)
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # Get filter options for sidebar
    available_brands = Brand.objects.filter(is_active=True).order_by('sort_order')
    available_categories = Category.objects.filter(is_active=True).order_by('name')
    available_colors = ColorVariant.objects.filter(is_active=True).order_by('sort_order')

    # Get unique sizes from SizeStock
    available_sizes = (
        SizeStock.objects
        .filter(product__is_active=True, stock_quantity__gt=0)
        .values_list('size', flat=True)
        .distinct()
        .order_by('size')
    )

    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'available_brands': available_brands,
        'available_categories': available_categories,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'search_query': search,
    }

    return render(request, 'products/shop.html', context)
```

## CSS Classes Reference

### Filtering UI

- `.products-container` - Main container with sidebar
- `.product-filters` - Sidebar container (sticky)
- `.filter-group` - Individual filter section
- `.filter-title` - Filter section header
- `.filter-checkbox` - Checkbox wrapper
- `.color-swatches` - Color filter container
- `.color-swatch` - Individual color button
- `.size-buttons` - Size filter container
- `.size-btn` - Individual size button
- `.price-inputs` - Price input wrapper
- `.price-input` - Min/max price input
- `.price-apply-btn` - Apply price filter button
- `.clear-filters-btn` - Clear all filters button

### Products Display

- `.products-section` - Main products area
- `.filter-count` - Result count text
- `.products-grid` - Products grid layout
- `.product-card` - Individual product card
- `.product-image-container` - Product image wrapper
- `.product-image` - Product image
- `.discount-badge` - Discount percentage badge
- `.product-info` - Product details section
- `.product-name` - Product title
- `.product-price-block` - Price display area
- `.product-price` - Current price
- `.product-original-price` - Original price (strikethrough)

### Pagination

- `.pagination` - Pagination container
- `.page-btn` - Page button
- `.page-btn.active` - Active page button

## JavaScript API

### ProductFilterManager

```javascript
// Initialize
const filterManager = new ProductFilterManager({
  containerSelector: ".products-grid", // Product grid selector
  filterSelector: ".product-filters", // Filter sidebar selector
  paginationSelector: ".pagination", // Pagination selector
  apiUrl: "/api/products/filter/", // API endpoint
});

// Methods
filterManager.applyFilters(); // Apply current filters
filterManager.clearAllFilters(); // Reset all filters
filterManager.loadFiltersFromURL(); // Load filters from URL params
```

### URL Parameters

The filter manager preserves state in URL parameters:

```
?brands=1,2,3
&categories=5,6
&colors=10,12
&sizes=M,L,XL
&price_min=500
&price_max=5000
&search=shirt
&page=2
```

## API Endpoints

### Filter Products

```
GET /api/products/filter/

Parameters:
- brands: comma-separated brand IDs
- categories: comma-separated category IDs
- colors: comma-separated color IDs
- sizes: comma-separated sizes (XS,S,M,L,XL,2XL,3XL,4XL)
- price_min: minimum price
- price_max: maximum price
- search: search query
- page: page number
- page_size: items per page (default: 12)

Response:
{
  "success": true,
  "products": [...],
  "count": 12,
  "total_count": 156,
  "pagination": {
    "current_page": 1,
    "total_pages": 13,
    "has_next": true,
    "has_previous": false
  }
}
```

### Get Filter Options

```
GET /api/products/filter-options/

Response:
{
  "success": true,
  "brands": [{"id": 1, "name": "Brand Name", "slug": "brand-name"}],
  "categories": [...],
  "colors": [{"id": 1, "name": "Blue", "hex_code": "#51e2f5"}],
  "sizes": ["XS", "S", "M", "L", "XL"],
  "price_range": {"min": 500, "max": 15000}
}
```

### Search Products

```
GET /api/products/search/?q=shirt

Response:
{
  "success": true,
  "products": [...],
  "count": 5,
  "query": "shirt"
}
```

## Responsive Behavior

- **Desktop (> 900px)**: Sidebar filters + 4-column grid
- **Tablet (640-900px)**: Stacked layout, 2-column grid
- **Mobile (< 640px)**: Full-width filters, 2-column grid

## Accessibility Features

- ARIA labels on all filter controls
- Keyboard navigation support
- Screen reader announcements
- Semantic HTML with proper heading hierarchy
- Color filter includes title attributes
- Current page indicator in pagination

## Performance Optimization

- AJAX-based filtering (no page reload)
- Pagination with configurable page size
- Database query optimization with `select_related()` and `prefetch_related()`
- Lazy loading with skeleton placeholders
- Image optimization via Cloudinary
- CSS animations use GPU acceleration

## Customization

### Change Products Per Page

In `views.py`:

```python
paginator = Paginator(products, 24)  # Change 12 to desired count
```

### Modify Filter Options

Add to `products/views.py`:

```python
# Add sorting options
sort_by = request.GET.get('sort', '-created_at')
products = products.order_by(sort_by)
```

### Customize Product Grid

In CSS:

```css
.products-grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}
```

---

**Last Updated:** 2026
**Status:** Production Ready ✓
