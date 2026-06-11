/**
 * Dynamic Homepage Loading
 * Loads all homepage content from backend API
 */

import * as apiClient from '../api/api-client.js';
import { initReveal } from '../core/utilities.js';

/**
 * Render hero banners from API
 */
async function loadHeroBanners() {
  try {
    const data = await apiClient.getHeroBanners();
    if (!data.banners || data.banners.length === 0) {
      console.log('No hero banners available');
      return;
    }

    const heroWrap = document.getElementById('hero-wrap');
    if (!heroWrap) return;

    // Clear existing slides
    heroWrap.querySelectorAll('.hero-slide').forEach(slide => slide.remove());

    // Add banner slides
    data.banners.forEach((banner, index) => {
      const slide = document.createElement('div');
      slide.className = `hero-slide ${index === 0 ? 'active' : ''}`;
      slide.innerHTML = `<img src="${banner.image}" alt="${banner.title}" />`;
      heroWrap.appendChild(slide);
    });

    // Update hero content with first banner
    if (data.banners.length > 0) {
      const firstBanner = data.banners[0];
      const subtitle = document.getElementById('hero-subtitle');
      const ctaBtn = heroWrap.querySelector('.cta-btn');
      const h1 = heroWrap.querySelector('h1');

      if (h1) h1.textContent = firstBanner.title;
      if (subtitle) subtitle.textContent = firstBanner.subtitle || 'High-energy summer menswear built with breathable fabrics, clean cuts, and ocean-cool color tones.';
      if (ctaBtn) {
        ctaBtn.textContent = firstBanner.button_label;
        ctaBtn.href = firstBanner.button_url;
      }
    }
  } catch (error) {
    console.error('Error loading hero banners:', error);
  }
}

/**
 * Render product card HTML - matches existing CSS structure
 */
function renderProductCard(product) {
  const mainImage = product.main_image || product.thumbnail || product.images?.[0];
  const galleryImage = product.images?.[1] || mainImage;
  const colorButtons = (product.colors || []).map((color, idx) => {
    const hex = color.hex || color.hex_code || color.name || product.color_hex || '#51E2F5';
    return `<button type="button" class="radio-pill color-pill ${idx === 0 ? 'active' : ''}" data-value="${hex}" style="--swatch:${hex}"><span class="swatch"></span><span class="pill-text">${hex}</span></button>`;
  }).join('');
  const offerHTML = product.offer 
    ? `<div class="price-block has-offer" data-offer-expirable data-offer-id="${product.offer.id}">
        <div class="price-line">
          <span class="price-now">Rs. ${product.current_price}</span>
          <span class="price-old">Rs. ${product.original_price}</span>
          <span class="price-off">${product.discount_percent}% OFF</span>
        </div>
        <div class="limited-badge" data-offer-countdown data-offer-end="${product.offer.countdown_end}">Limited time</div>
      </div>`
    : `<div class="price-block">
        <div class="price-line">
          <span class="price-now">Rs. ${product.current_price}</span>
        </div>
      </div>`;

  return `
    <article class="product-card reveal" data-product-id="${product.id}" data-product-url="/products/${product.slug}/">
      <div class="product-media" aria-label="${product.name}">
        <div class="flip-inner">
          <img class="front" src="${mainImage}" alt="${product.name} front" loading="lazy" />
          <img class="back" src="${galleryImage}" alt="${product.name} back" loading="lazy" />
        </div>
        <button type="button" class="fav-btn" data-id="${product.id}" title="Add to favorites"><i class="fa-regular fa-heart"></i></button>
        <div class="flip-hint">Tap to flip</div>
      </div>
      <div class="product-body">
        <p class="chip">${product.category}</p>
        <h3><a href="/products/${product.slug}/">${product.name}</a></h3>
        <p class="tiny">${product.description || ''}</p>
        ${offerHTML}
        <div class="variant-stack">
          <label>Size</label>
          <div class="radio-row" data-role="size">
            ${product.sizes.map((size, idx) => `<button type="button" class="radio-pill ${idx === 0 ? 'active' : ''}" data-value="${size}">${size}</button>`).join('')}
          </div>
          ${colorButtons
            ? `<label>Color</label>
               <div class="radio-row" data-role="color">
                 ${colorButtons}
               </div>`
            : ''}
        </div>
        ${product.stock > 0 
          ? `<button class="add-btn" type="button" data-add-cart data-product-id="${product.id}">Add to cart</button>`
          : `<button class="add-btn" type="button" disabled>Out of stock</button>`}
      </div>
    </article>
  `;
}

/**
 * Load featured products
 */
async function loadFeaturedProducts() {
  try {
    const data = await apiClient.getFeaturedProducts();
    if (!data.products || data.products.length === 0) {
      console.log('No featured products available');
      return;
    }

    const container = document.getElementById('featured-products');
    if (!container) return;

    container.innerHTML = data.products
      .map(product => renderProductCard(product))
      .join('');
  } catch (error) {
    console.error('Error loading featured products:', error);
  }
}

/**
 * Load deal products (products with active offers)
 */
async function loadDealProducts() {
  try {
    const data = await apiClient.getDealProducts();
    if (!data.products || data.products.length === 0) {
      console.log('No deal products available');
      return;
    }

    const section = document.getElementById('deals-section');
    const container = document.getElementById('deal-products');
    if (!section || !container) return;

    section.style.display = 'block';
    container.innerHTML = data.products
      .map(product => renderProductCard(product))
      .join('');
  } catch (error) {
    console.error('Error loading deal products:', error);
  }
}

/**
 * Initialize homepage
 */
async function initDynamicHomepage() {
  try {
    // Load all dynamic content in parallel
    await Promise.all([
      loadHeroBanners(),
      loadFeaturedProducts(),
      loadDealProducts(),
    ]);

    // Initialize reveal animations
    initReveal();

    // Dispatch custom event to notify other scripts
    window.dispatchEvent(new CustomEvent('growmore:homepage-loaded'));
  } catch (error) {
    console.error('Error initializing dynamic homepage:', error);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDynamicHomepage);
} else {
  initDynamicHomepage();
}
