/**
 * Centralized API client for Grow More frontend
 * Handles all communication with Django backend
 */

const API_BASE_URL = '/api';

/**
 * Get CSRF token from cookies
 */
export function getCsrfToken() {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...options.headers,
    },
    ...options,
  };

  // Add CSRF token for POST/PUT/DELETE
  if (['POST', 'PUT', 'DELETE'].includes(config.method)) {
    config.headers['X-CSRFToken'] = getCsrfToken();
  }

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API request failed (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Hero Banners API
 */
export async function getHeroBanners() {
  return fetchAPI('/hero-banners/');
}

/**
 * Products API
 */
export async function getProducts(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.append('category', filters.category);
  if (filters.featured) params.append('featured', 'true');
  if (filters.trending) params.append('trending', 'true');
  if (filters.limit) params.append('limit', filters.limit);

  const query = params.toString() ? `?${params.toString()}` : '';
  return fetchAPI(`/products/${query}`);
}

export async function getProduct(productId) {
  return fetchAPI(`/products/${productId}/`);
}

export async function getProductOffer(productId) {
  return fetchAPI(`/products/${productId}/offer/`);
}

export async function getFeaturedProducts() {
  return fetchAPI('/featured-products/');
}

export async function getTrendingProducts() {
  return fetchAPI('/trending-products/');
}

export async function getDealProducts() {
  return fetchAPI('/deal-products/');
}

/**
 * Homepage Sections API
 */
export async function getHomepageSections() {
  return fetchAPI('/homepage/sections/');
}

/**
 * Categories API
 */
export async function getCategories() {
  return fetchAPI('/categories/');
}

/**
 * Offers API
 */
export async function getActiveOffers() {
  return fetchAPI('/offers/active/');
}

export async function getOffer(offerId) {
  return fetchAPI(`/offers/${offerId}/`);
}
