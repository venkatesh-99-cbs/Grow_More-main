let PRODUCTS = [
  { id: 1, name: "Aero Linen Camp Shirt", category: "shirts", price: 52, desc: "Breathable linen blend with relaxed summer drape.", sizes: ["S", "M", "L", "XL"], colors: ["Dusty White", "Bright Blue", "Pink Sand"], images: ["https://images.unsplash.com/photo-1618886614638-80e3c103d31a?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1622445275576-721325763afe?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80"] },
  { id: 2, name: "Coastal Knit Polo", category: "tees", price: 48, desc: "Soft knit polo built for humid city days.", sizes: ["S", "M", "L", "XL"], colors: ["Blue Green", "Bright Blue", "Dark Sand"], images: ["https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=80"] },
  { id: 3, name: "Sunset Chino Shorts", category: "shorts", price: 38, desc: "Tailored fit with stretch comfort for movement.", sizes: ["30", "32", "34", "36"], colors: ["Dark Sand", "Dusty White", "Blue Green"], images: ["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1592878940526-0214b0f374f6?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=80"] },
  { id: 4, name: "Wave Runner Tee", category: "tees", price: 29, desc: "Ultra-light cotton tee with athletic silhouette.", sizes: ["S", "M", "L", "XL"], colors: ["Bright Blue", "Blue Green", "Dusty White"], images: ["https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=900&q=80"] },
  { id: 5, name: "Breeze Utility Overshirt", category: "outerwear", price: 64, desc: "Light layer for cooler summer evenings.", sizes: ["M", "L", "XL"], colors: ["Dark Sand", "Bright Blue", "Pink Sand"], images: ["https://images.unsplash.com/photo-1610652492500-ded49ceeb378?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?auto=format&fit=crop&w=900&q=80"] },
  { id: 6, name: "Harbor Straw Fedora", category: "accessories", price: 24, desc: "Ventilated weave and crisp edge for beach style.", sizes: ["One"], colors: ["Dusty White", "Dark Sand"], images: ["https://images.unsplash.com/photo-1514329926535-7f6db2f2b56a?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1503342394128-c104d54dba01?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1533827432537-70133748f5c8?auto=format&fit=crop&w=900&q=80"] }
];

const COLOR_MAP = { "Bright Blue": "#51e2f5", "Blue Green": "#9df9ef", "Dusty White": "#edf756", "Pink Sand": "#ffa8b6", "Dark Sand": "#a28089" };

const state = {
  cart: JSON.parse(localStorage.getItem("gm_cart") || "[]"),
  favorites: JSON.parse(localStorage.getItem("gm_favorites") || "[]")
};

const money = (n) => `₹${Number(n).toFixed(2)}`;
const saveCart = () => localStorage.setItem("gm_cart", JSON.stringify(state.cart));
const saveFavorites = () => localStorage.setItem("gm_favorites", JSON.stringify(state.favorites));
const isLoggedIn = () => localStorage.getItem("gm_logged_in") === "1";
const getProduct = (id) => PRODUCTS.find((p) => String(p.id) === String(id));
const getProductByRef = (ref) => PRODUCTS.find((p) => String(p.id) === String(ref) || String(p.slug) === String(ref));
const loginUser = () => localStorage.setItem("gm_logged_in", "1");
const logoutUser = () => {
  localStorage.removeItem("gm_logged_in");
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_info");
  localStorage.removeItem("user_role");
};
const hasSeenFlipHint = () => localStorage.getItem("gm_seen_flip_hint") === "1";
const setSeenFlipHint = () => localStorage.setItem("gm_seen_flip_hint", "1");
const DEAL_TIMER_START = 2 * 3600 + 14 * 60 + 39;
const GM_API_BASE_URL = "http://localhost:8000/api";

function saveAuthenticatedSession(data) {
  if (data.access_token) localStorage.setItem("access_token", data.access_token);
  if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
  if (data.user) localStorage.setItem("user_info", JSON.stringify(data.user));
  if (data.role) localStorage.setItem("user_role", data.role);
  loginUser();
}

function normalizeProduct(raw) {
  const images = Array.isArray(raw.images) && raw.images.length
    ? raw.images
    : [raw.thumbnail].filter(Boolean);
  return {
    ...raw,
    id: raw.id,
    name: raw.name || "Product",
    category: raw.category || raw.category_slug || raw.category_name || "all",
    price: Number(raw.price || 0),
    originalPrice: raw.original_price ? Number(raw.original_price) : undefined,
    desc: raw.desc || raw.short_description || raw.description || "",
    sizes: raw.sizes || raw.size_options || ["M"],
    colors: raw.colors || raw.color_options || ["Default"],
    images: images.length ? images : PRODUCTS[0].images,
  };
}

function setLiveProducts(list) {
  if (!Array.isArray(list) || !list.length) return;
  PRODUCTS = list.map(normalizeProduct);
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return false;
  try {
    const response = await fetch(`${GM_API_BASE_URL}/users/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.access_token) return false;
    saveAuthenticatedSession(data);
    return true;
  } catch (error) {
    return false;
  }
}

// Generic API call function with proper error handling and CORS support
async function apiCall(url, options = {}, retryOnUnauthorized = true) {
  const defaultHeaders = {
    "Content-Type": "application/json",
  };

  // Add authentication token if available
  const token = localStorage.getItem("access_token");
  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    method: options.method || "GET",
    headers: { ...defaultHeaders, ...options.headers },
    credentials: "include", // Important for CORS
  };

  if (options.body) {
    config.body = typeof options.body === "string" ? options.body : JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 401) {
        if (retryOnUnauthorized && await refreshAccessToken()) {
          return apiCall(url, options, false);
        }
        logoutUser();
        throw new Error("Session expired. Please login again.");
      }
      const message = data.detail || data.error || data.non_field_errors?.[0] || Object.values(data)[0]?.[0] || `Request failed (${response.status})`;
      throw new Error(message);
    }

    return data;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error("Invalid response from server");
    }
    throw error;
  }
}

// Authentication request function - wrapper around apiCall
async function authRequest(path, payload) {
  try {
    return await apiCall(`${GM_API_BASE_URL}${path}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw error;
  }
}

function getCartLineItems() {
  return state.cart.map((item) => ({
    id: item.id,
    name: item.name,
    price: Number(item.price),
    quantity: Number(item.qty || item.quantity || 1),
    size: item.size || "",
    color: item.color || "",
  }));
}

function splitFullName(fullName) {
  const parts = String(fullName || "").trim().split(/\s+/).filter(Boolean);
  return {
    first_name: parts[0] || "Customer",
    last_name: parts.slice(1).join(" ") || "GrowMore",
  };
}

// Global countdown synchronization
function initGlobalDealTimer() {
  const stored = localStorage.getItem("gm_deal_end_time");
  if (!stored) {
    localStorage.setItem("gm_deal_end_time", String(Date.now() + DEAL_TIMER_START * 1000));
  }
}

function getGlobalCountdownSeconds() {
  const endTime = Number(localStorage.getItem("gm_deal_end_time") || 0);
  return Math.max(0, Math.floor((endTime - Date.now()) / 1000));
}

let globalCountdownInterval = null;
let countdownCallbacks = [];

function registerCountdownCallback(callback) {
  if (!callback || typeof callback !== 'function') return;
  if (!countdownCallbacks.includes(callback)) {
    countdownCallbacks.push(callback);
    callback(getGlobalCountdownSeconds());
  }
}

function unregisterCountdownCallback(callback) {
  countdownCallbacks = countdownCallbacks.filter(cb => cb !== callback);
}

function startGlobalCountdownTick() {
  if (globalCountdownInterval) return;
  globalCountdownInterval = setInterval(() => {
    const secondsLeft = getGlobalCountdownSeconds();
    countdownCallbacks.forEach(cb => {
      try {
        cb(secondsLeft);
      } catch (err) {
        console.error('Countdown callback error:', err);
      }
    });
  }, 1000);
  const secondsLeft = getGlobalCountdownSeconds();
  countdownCallbacks.forEach(cb => {
    try {
      cb(secondsLeft);
    } catch (err) {
      console.error('Countdown callback error:', err);
    }
  });
}

function updateCartCount() { const c = document.getElementById("cart-count"); if (c) c.textContent = String(state.cart.reduce((s, i) => s + i.qty, 0)); }
function updateFavoriteCount() {
  const c = document.getElementById("fav-count");
  if (c) c.textContent = String(state.favorites.length);
}
function toggleMenu() { document.querySelector(".nav-links")?.classList.toggle("open"); }

function toggleCart(force) {
  const cart = document.getElementById("cart-sidebar");
  const ov = document.getElementById("cart-overlay");
  if (!cart || !ov) return;
  const open = typeof force === "boolean" ? force : !cart.classList.contains("active");
  cart.classList.toggle("active", open);
  ov.classList.toggle("active", open);
}

function addToCart(id, qty = 1, size = "M", color = "Default") {
  const p = getProduct(id);
  if (!p) return;
  const key = `${id}-${size}-${color}`;
  const ex = state.cart.find((x) => x.key === key);
  if (ex) ex.qty += qty;
  else state.cart.push({ key, id, name: p.name, price: p.price, qty, size, color, image: p.images[0] });
  saveCart();
  renderCart();
  showToast("Added to cart");
}

function removeItem(i) { state.cart.splice(i, 1); saveCart(); renderCart(); }

function checkout() {
  if (!state.cart.length) return alert("Your cart is empty.");
  if (!isLoggedIn()) {
    localStorage.setItem("gm_post_login_redirect", "checkout.html");
    window.location.href = "login.html";
    return;
  }
  window.location.href = "checkout.html";
}

function renderCart() {
  updateCartCount();
  updateFavoriteCount();
  const list = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total-amount");
  if (!list || !totalEl) return;
  if (!state.cart.length) { list.innerHTML = '<p class="muted">Your cart is empty</p>'; totalEl.textContent = "$0.00"; return; }
  list.innerHTML = state.cart.map((i, idx) => `<div class="cart-row cart-row-rich"><img src="${i.image}" alt="${i.name}"><div><p>${i.name}</p><small>${i.size}, ${i.color} x${i.qty}</small></div><div class="cart-row-actions"><strong>${money(i.price * i.qty)}</strong><button class="remove-btn" onclick="removeItem(${idx})">Remove</button></div></div>`).join("");
  totalEl.textContent = money(state.cart.reduce((s, i) => s + i.price * i.qty, 0));
}

function colorStyle(v) { return `style="--swatch:${COLOR_MAP[v] || "#fff"}"`; }
function pricingFor(p) {
  const original = p.originalPrice || Math.round((p.price / 0.72) * 100) / 100;
  const save = Math.max(0, original - p.price);
  const pct = original > 0 ? Math.round((save / original) * 100) : 0;
  return { original, save, pct };
}
function pricingHTML(p, big = false) {
  const { original, save, pct } = pricingFor(p);
  return `<div class="price-block${big ? " big" : ""}"><div class="price-line"><span class="price-now">${money(p.price)}</span><span class="price-old">${money(original)}</span><span class="price-off">${pct}% OFF</span></div><div class="save-line">You save ${money(save)} today</div><div class="limited-badge" data-ends-seconds="${DEAL_TIMER_START}">Ends in 02:14:39</div></div>`;
}

function variantButtons(role, values) {
  if (role === "color") {
    return `<div class="radio-row" data-role="${role}">${values.map((v, i) => `<button type="button" class="radio-pill color-pill${i === 0 ? " active" : ""}" data-value="${v}" ${colorStyle(v)}><span class="swatch"></span><span class="pill-text">${v}</span></button>`).join("")}</div>`;
  }
  return `<div class="radio-row" data-role="${role}">${values.map((v, i) => `<button type="button" class="radio-pill${i === 0 ? " active" : ""}" data-value="${v}">${v}</button>`).join("")}</div>`;
}

function favoriteButton(p) {
  const active = state.favorites.includes(p.id) ? "active" : "";
  return `<button type="button" class="fav-btn ${active}" data-fav-id="${p.id}" title="Add to favorites">&#10084;</button>`;
}

function productCardTemplate(p) {
  const front = p.images[0];
  const back = p.images[1] || p.images[0];
  return `<article class="product-card reveal" data-product-id="${p.slug || p.id}"><div class="product-media" aria-label="${p.name}"><div class="flip-inner"><img class="front" src="${front}" alt="${p.name} front"><img class="back" src="${back}" alt="${p.name} back"></div>${favoriteButton(p)}<div class="flip-hint">Tap to flip</div></div><div class="product-body"><p class="chip">${p.category}</p><h3>${p.name}</h3><p class="tiny">${p.desc}</p>${pricingHTML(p)}<div class="variant-stack"><label>Size</label>${variantButtons("size", p.sizes)}<label>Color</label>${variantButtons("color", p.colors)}</div><button class="add-btn" onclick="addToCartFromCard('${p.id}', this)">Add to cart</button></div></article>`;
}

function getSelected(card, role) { return card.querySelector(`.radio-row[data-role='${role}'] .radio-pill.active`)?.dataset.value || ""; }
function addToCartFromCard(id, btn) { const card = btn.closest(".product-card"); if (!card) return; addToCart(id, 1, getSelected(card, "size") || "M", getSelected(card, "color") || "Default"); }

function renderProducts(targetId, list) { const root = document.getElementById(targetId); if (!root) return; root.innerHTML = list.map(productCardTemplate).join(""); }

// Update initShopControls to load from backend
let searchTimeout;
async function initShopControls() {
  if (!document.getElementById("product-grid")) return;

  const category = document.getElementById("category-filter");
  const sort = document.getElementById("sort-by");
  const search = document.getElementById("search-input");

  const apply = async () => {
    try {
      let url = `${GM_API_BASE_URL}/products/?`;

      const searchValue = search?.value || "";
      if (searchValue) url += `search=${searchValue}&`;

      const categoryValue = category?.value;
      if (categoryValue && categoryValue !== "all")
        url += `category=${categoryValue}&`;

      const sortValue = sort?.value;
      if (sortValue) {
        const sortMap = {
          "price-low": "price",
          "price-high": "-price",
          name: "name",
        };
        url += `ordering=${sortMap[sortValue]}&`;
      }

      const response = await apiCall(url);
      const products = (response.results || response).map(normalizeProduct);
      setLiveProducts(products);
      renderProducts("product-grid", products);
      initReveal();
    } catch (error) {
      console.error("Error loading products:", error);
      renderProducts("product-grid", PRODUCTS);
      showToast("Showing offline products. Backend is unavailable.");
    }
  };

  category?.addEventListener("change", apply);
  sort?.addEventListener("change", apply);
  search?.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(apply, 300);
  });

  apply();
}

function initHeroSlider() {
  const slides = [...document.querySelectorAll(".hero-slide")];
  if (!slides.length) return;
  let i = 0;
  setInterval(() => { slides[i].classList.remove("active"); i = (i + 1) % slides.length; slides[i].classList.add("active"); }, 4200);
}

function renderRelated(current) {
  const root = document.getElementById("related-products");
  if (!root) return;
  const related = PRODUCTS.filter((p) => p.id !== current.id && (p.category === current.category || Math.abs(p.price - current.price) <= 20)).slice(0, 3);
  root.innerHTML = related.map(productCardTemplate).join("");
}

async function initProductDetail() {
  const root = document.getElementById("product-detail");
  if (!root) return;
  const rawId = new URLSearchParams(window.location.search).get("id");
  let p = getProductByRef(rawId) || PRODUCTS[0];
  try {
    if (rawId) {
      const detail = await apiCall(`${GM_API_BASE_URL}/products/${rawId}/`);
      p = normalizeProduct(detail);
    }
  } catch (error) {
    console.warn("Using cached product detail:", error.message);
  }
  const thumbs = p.images.map((img, i) => `<button type="button" class="thumb-btn" data-img="${img}" data-index="${i}"><img src="${img}" alt="${p.name} view ${i + 1}"></button>`).join("");
  const dots = p.images.map((_, i) => `<span class="swipe-dot${i === 0 ? " active" : ""}" data-dot-index="${i}"></span>`).join("");
  root.innerHTML = `<div class="detail-media"><div class="detail-main-frame"><button type="button" class="img-nav prev" data-dir="-1" aria-label="Previous image">&#10094;</button><img src="${p.images[0]}" alt="${p.name}" id="detail-main-img"><button type="button" class="img-nav next" data-dir="1" aria-label="Next image">&#10095;</button></div><div class="swipe-dots" id="swipe-dots">${dots}</div><div class="detail-thumbs">${thumbs}</div></div><div class="detail-copy"><p class="chip">${p.category}</p><h1>${p.name}</h1><p>${p.desc}</p>${pricingHTML(p, true)}<div class="variant-stack"><label>Size</label>${variantButtons("size", p.sizes)}<label>Color</label>${variantButtons("color", p.colors)}</div><div class="qty-wrap"><label>Quantity</label><div class="qty-stepper"><button type="button" class="qty-btn" data-action="minus">-</button><input id="detail-qty" class="qty-input" type="number" min="1" value="1" /><button type="button" class="qty-btn" data-action="plus">+</button></div></div><div class="product-actions"><button class="add-btn" onclick="addToCart(${p.id}, Math.max(1, Number(document.getElementById('detail-qty').value||1)), getSelected(document.querySelector('.detail-copy'), 'size')||'M', getSelected(document.querySelector('.detail-copy'), 'color')||'Default')">Add to cart</button><button class="fav-action-btn" type="button" onclick="toggleFavoriteFromDetail(${p.id})">Add to Favorite</button></div></div>`;
  renderRelated(p);
  initProductSwipe();
}

function toggleFavoriteFromDetail(id) {
  if (!state.favorites.includes(id)) state.favorites.push(id);
  else state.favorites = state.favorites.filter((x) => x !== id);
  saveFavorites();
  updateFavoriteCount();
  showToast(state.favorites.includes(id) ? "Added to favorites" : "Removed from favorites");
}

function validateStep(stepEl) {
  const fields = [...stepEl.querySelectorAll("input, select, textarea")].filter((el) => !el.disabled);
  for (const field of fields) {
    if (!field.checkValidity()) { field.reportValidity(); return false; }
  }
  return true;
}

function removeCheckoutItem(index) {
  state.cart.splice(index, 1);
  saveCart();
  renderCart();
  const summary = document.getElementById("checkout-summary");
  if (summary) renderCheckoutSummary(summary);
}

function renderCheckoutSummary(summary) {
  const total = state.cart.reduce((s, i) => s + i.price * i.qty, 0);
  const tax = total * 0.18;
  if (!state.cart.length) {
    summary.innerHTML = "<p>Your cart is empty. Add items from shop.</p>";
    return;
  }
  summary.innerHTML = `${state.cart.map((i, idx) => `<div class='checkout-item'><img src='${i.image}' alt='${i.name}'><div><p>${i.name}</p><small>${i.size}, ${i.color} x${i.qty}</small></div><div class='checkout-actions'><strong>${money(i.price * i.qty)}</strong><button class='checkout-remove' type='button' onclick='removeCheckoutItem(${idx})'>Remove</button></div></div>`).join("")}<div class='cart-row'><span>Subtotal</span><strong>${money(total)}</strong></div><div class='cart-row'><span>Tax</span><strong>${money(tax)}</strong></div><div class='cart-row'><strong>Total</strong><strong>${money(total + tax)}</strong></div>`;
}

function initCheckoutPage() {
  const summary = document.getElementById("checkout-summary");
  const form = document.getElementById("checkout-form");
  if (!summary || !form) return;
  renderCheckoutSummary(summary);

  const steps = [...document.querySelectorAll(".step")];
  const showStep = (n) => {
    steps.forEach((s) => s.classList.toggle("active", Number(s.dataset.step) === n));
    document.querySelectorAll(".step-dot").forEach((d) => { const v = Number(d.dataset.step); d.classList.toggle("active", v === n); d.classList.toggle("done", v < n); });
  };

  document.getElementById("to-payment")?.addEventListener("click", (e) => {
    e.preventDefault();
    if (!state.cart.length) {
      showToast("Cart is empty");
      return;
    }
    if (!validateStep(document.querySelector('.step[data-step="1"]'))) return;
    showStep(2);
  });

  document.getElementById("back-shipping")?.addEventListener("click", () => showStep(1));

  document.getElementById("to-review")?.addEventListener("click", (e) => {
    e.preventDefault();
    if (!validateStep(document.querySelector('.step[data-step="2"]'))) return;
    const review = document.getElementById("review-block");
    if (review) {
      const formData = new FormData(form);
      const subtotal = state.cart.reduce((sum, item) => sum + item.price * item.qty, 0);
      const tax = subtotal * 0.18;
      review.innerHTML = `<p><strong>${formData.get("name")}</strong></p><p>${formData.get("email")} | ${formData.get("phone")}</p><p>${formData.get("address")}, ${formData.get("city")} - ${formData.get("zip")}</p><div class="cart-row"><span>Payable</span><strong>${money(subtotal + tax)}</strong></div>`;
    }
    showStep(3);
  });

  document.getElementById("back-payment")?.addEventListener("click", () => showStep(2));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.cart.length) {
      showToast("Cart is empty");
      return;
    }
    const formData = new FormData(form);
    const names = splitFullName(formData.get("name"));

    try {
      const orderResponse = await apiCall(`${GM_API_BASE_URL}/orders/create/`, {
        method: "POST",
        body: JSON.stringify({
          ...names,
          email: formData.get("email"),
          phone: formData.get("phone"),
          shipping_address: formData.get("address"),
          shipping_city: formData.get("city"),
          shipping_state: formData.get("city"),
          shipping_postal_code: formData.get("zip"),
          payment_method: "razorpay",
          items: getCartLineItems(),
        }),
      });

      await initiatePayment(orderResponse.order.id, orderResponse.order.total_amount);
    } catch (error) {
      showToast("Order creation failed: " + error.message);
    }
  });
}

// Initiate Razorpay payment
async function initiatePayment(orderId, totalAmount) {
  try {
    const paymentResponse = await apiCall(`${GM_API_BASE_URL}/payments/create/`, {
      method: "POST",
      body: JSON.stringify({
        order_id: orderId,
        amount: totalAmount,
      }),
    });

    // Open Razorpay
    openRazorpayModal(paymentResponse);
  } catch (error) {
    showToast("Payment initiation failed: " + error.message);
  }
}

// Razorpay modal
function openRazorpayModal(paymentData) {
  if (typeof Razorpay === "undefined") {
    showToast("Razorpay checkout script did not load. Check your internet connection.");
    return;
  }
  const options = {
    key: paymentData.razorpay_key_id,
    amount: paymentData.amount,
    currency: paymentData.currency,
    name: "Grow More",
    description: paymentData.description,
    order_id: paymentData.razorpay_order_id,
    customer_details: {
      name: paymentData.customer_name,
      email: paymentData.customer_email,
      contact: paymentData.customer_phone,
    },
    handler: async function (response) {
      await verifyPayment(response, paymentData.payment_id);
    },
    prefill: {
      name: paymentData.customer_name,
      email: paymentData.customer_email,
      contact: paymentData.customer_phone,
    },
    theme: { color: "#51e2f5" },
  };

  const rzp = new Razorpay(options);
  rzp.open();
}

// Verify payment
async function verifyPayment(response, paymentId) {
  try {
    const verifyResponse = await apiCall(`${GM_API_BASE_URL}/payments/verify/`, {
      method: "POST",
      body: JSON.stringify({
        razorpay_order_id: response.razorpay_order_id,
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_signature: response.razorpay_signature,
      }),
    });

    // Payment successful
    showToast("Payment successful!");
    localStorage.removeItem("gm_cart");
    window.location.href =
      "order-success.html?order=" + verifyResponse.order_id;
  } catch (error) {
    showToast("Payment verification failed: " + error.message);
  }
}

function initFavoritesPage() {
  const root = document.getElementById("favorites-grid");
  if (!root) return;
  const items = PRODUCTS.filter((p) => state.favorites.includes(p.id));
  if (!items.length) {
    root.innerHTML = "<p class='muted'>No favorites yet. Tap the heart on products.</p>";
    return;
  }
  root.innerHTML = items.map(productCardTemplate).join("");
}

function initLoginPage() {
  const card = document.getElementById("login-card");
  if (!card) return;
  const tabs = [...card.querySelectorAll(".login-tab")];
  const panes = [...card.querySelectorAll(".login-pane")];
  const redirectAfter = () => {
    const redirect = localStorage.getItem("gm_post_login_redirect") || "checkout.html";
    localStorage.removeItem("gm_post_login_redirect");
    window.location.href = redirect;
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const mode = tab.dataset.mode;
      tabs.forEach((t) => t.classList.toggle("active", t === tab));
      panes.forEach((p) => p.classList.toggle("active", p.dataset.mode === mode));
    });
  });

  document.getElementById("login-back-btn")?.addEventListener("click", () => {
    window.location.href = "index.html";
  });

  document.getElementById("google-login-btn")?.addEventListener("click", async () => {
    const email = (document.getElementById("google-email-input")?.value || "").trim();
    if (!email) {
      showToast("Enter your Google email");
      return;
    }
    try {
      const data = await authRequest("/users/auth/google/", { email });
      saveAuthenticatedSession(data);
      showToast(data.message || "Google login successful");
      redirectAfter();
    } catch (error) {
      showToast("Google login error: " + error.message);
    }
  });

  document.getElementById("generate-otp-btn")?.addEventListener("click", async () => {
    const phone = (document.getElementById("phone-input")?.value || "").trim();
    const hint = document.getElementById("otp-hint");
    if (!phone) {
      showToast("Enter phone number first");
      return;
    }
    try {
      const data = await authRequest("/users/auth/phone/request-otp/", { phone });
      if (hint) {
        hint.textContent = data.otp
          ? `Development OTP: ${data.otp}`
          : "OTP sent. It expires in 5 minutes.";
      }
      showToast("OTP sent");
    } catch (error) {
      showToast("OTP error: " + error.message);
    }
  });

  document.getElementById("phone-login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const phone = (document.getElementById("phone-input")?.value || "").trim();
    const entered = (document.getElementById("phone-otp-input")?.value || "").trim();
    if (!phone || !entered) {
      showToast("Enter phone number and OTP");
      return;
    }
    try {
      const data = await authRequest("/users/auth/phone/verify-otp/", { phone, otp: entered });
      saveAuthenticatedSession(data);
      showToast(data.message || "Phone login successful");
      redirectAfter();
    } catch (error) {
      showToast("Phone login error: " + error.message);
    }
  });

  document
  .getElementById("manual-login-form")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;

    try {
      const data = await authRequest("/users/auth/login/", { email, password });
      saveAuthenticatedSession(data);
      showToast(data.message || "Login successful");
      redirectAfter();
    } catch (error) {
      showToast("Login error: " + error.message);
    }
  });
}

function showToast(message) {
  let toast = document.getElementById("gm-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "gm-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => toast.classList.remove("show"), 1800);
}

function initCardInteractions() {
  let lastTouchFlipAt = 0;
  document.addEventListener("click", (e) => {
    const fav = e.target.closest(".fav-btn");
    if (fav) {
      const id = Number(fav.dataset.favId);
      if (!state.favorites.includes(id)) state.favorites.push(id);
      else state.favorites = state.favorites.filter((x) => x !== id);
      saveFavorites();
      updateFavoriteCount();
      const active = state.favorites.includes(id);
      fav.classList.toggle("active", active);
      showToast(active ? "Added to favorites" : "Removed from favorites");
      if (document.getElementById("favorites-grid") && !active) {
        initFavoritesPage();
      }
      return;
    }

    const pill = e.target.closest(".radio-pill");
    if (pill) {
      const row = pill.closest(".radio-row");
      row?.querySelectorAll(".radio-pill").forEach((b) => b.classList.remove("active"));
      pill.classList.add("active");
      return;
    }

    const thumb = e.target.closest(".thumb-btn");
    if (thumb) {
      e.preventDefault();
      e.stopPropagation();
      const main = document.getElementById("detail-main-img");
      if (main) main.src = thumb.dataset.img;
      return;
    }

    const qtyBtn = e.target.closest(".qty-btn");
    if (qtyBtn) {
      const input = document.getElementById("detail-qty");
      if (!input) return;
      const v = Number(input.value || 1);
      input.value = String(qtyBtn.dataset.action === "plus" ? v + 1 : Math.max(1, v - 1));
      return;
    }

    const media = e.target.closest(".product-media");
    if (media && window.matchMedia("(hover: none)").matches) {
      const now = Date.now();
      if (now - lastTouchFlipAt < 120) return;
      lastTouchFlipAt = now;
      media.classList.toggle("flipped");
      if (!hasSeenFlipHint()) {
        setSeenFlipHint();
        document.querySelectorAll(".flip-hint").forEach((n) => n.classList.add("hide"));
      }
      e.preventDefault();
      return;
    }

    const card = e.target.closest(".product-card");
    if (!card) return;
    if (e.target.closest("button, input, select, textarea, a, .radio-row")) return;
    window.location.href = `product.html?id=${card.dataset.productId}`;
  });
}

function initCartUI() {
  const sidebar = document.getElementById("cart-sidebar");
  if (!sidebar) return;
  if (!document.getElementById("cart-overlay")) {
    const overlay = document.createElement("div");
    overlay.id = "cart-overlay";
    overlay.className = "cart-overlay";
    overlay.addEventListener("click", () => toggleCart(false));
    document.body.appendChild(overlay);
  }
  if (!sidebar.querySelector(".cart-close")) {
    const closeBtn = document.createElement("button");
    closeBtn.className = "cart-close";
    closeBtn.type = "button";
    closeBtn.innerHTML = "&times;";
    closeBtn.onclick = () => toggleCart(false);
    sidebar.prepend(closeBtn);
  }
}

function initAuthUI() {
  const actions = document.querySelector(".actions");
  if (!actions) return;
  if (!actions.querySelector(".fav-nav-btn")) {
    const fav = document.createElement("a");
    fav.className = "icon-btn fav-nav-btn";
    fav.href = "favorites.html";
    fav.innerHTML = "&#10084;<span id='fav-count' class='fav-count'>0</span>";
    actions.insertBefore(fav, actions.querySelector(".icon-btn:nth-child(2)") || actions.firstChild);
  }
  const existing = actions.querySelector(".auth-btn");
  if (existing) existing.remove();
  actions.querySelector(".profile-nav-btn")?.remove();
  actions.querySelector(".admin-nav-link")?.remove();
  if (isLoggedIn()) {
    const profile = document.createElement("a");
    profile.className = "auth-btn profile-nav-btn";
    profile.href = "profile.html";
    profile.textContent = "Profile";
    actions.appendChild(profile);

    if (localStorage.getItem("user_role") === "admin") {
      const admin = document.createElement("a");
      admin.className = "auth-btn admin-nav-link";
      admin.href = "admin-dashboard.html";
      admin.textContent = "Admin";
      actions.appendChild(admin);
    }
  }
  const btn = document.createElement(isLoggedIn() ? "button" : "a");
  btn.className = "auth-btn";
  if (isLoggedIn()) {
    btn.type = "button";
    btn.textContent = "Logout";
    btn.addEventListener("click", () => {
      logoutUser();
      showToast("Logged out");
      initAuthUI();
    });
  } else {
    btn.textContent = "Login";
    btn.href = "login.html";
  }
  actions.appendChild(btn);
  updateFavoriteCount();
}

function initReveal() {
  const nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;
  const obs = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add("show"); obs.unobserve(entry.target); } }), { threshold: 0.15 });
  nodes.forEach((n) => obs.observe(n));
}

function initPopupBanner() {
  const container = document.getElementById("deal-popup-container");
  if (!container) return;
  const banner = container.querySelector(".deal-popup-banner");
  const floatingBall = document.getElementById("floating-deal-ball");
  if (!banner || !floatingBall) return;
  
  let bannerClosed = localStorage.getItem("gm_popup_closed") === "1";
  let permanentlyClosed = localStorage.getItem("gm_popup_permanently_closed") === "1";
  const countdownEl = banner.querySelector(".popup-countdown");
  const ballCountdownEl = floatingBall.querySelector(".ball-countdown");
  
  const showBanner = () => {
    banner.style.display = "block";
    floatingBall.style.display = "none";
    container.style.display = "flex";
    localStorage.setItem("gm_popup_closed", "0");
    bannerClosed = false;
  };
  
  const showFloatingBall = () => {
    banner.style.display = "none";
    floatingBall.style.display = "flex";
    container.style.display = "flex";
    localStorage.setItem("gm_popup_closed", "1");
    bannerClosed = true;
  };
  
  const bannerCountdownCallback = (secondsLeft) => {
    if (countdownEl) {
      countdownEl.textContent = formatCountdown(secondsLeft);
    }
    if (ballCountdownEl) {
      ballCountdownEl.textContent = formatCountdown(secondsLeft);
    }
    if (permanentlyClosed || secondsLeft <= 0) {
      container.style.display = "none";
    } else {
      container.style.display = "flex";
    }
  };
  
  registerCountdownCallback(bannerCountdownCallback);
  startGlobalCountdownTick();
  
  const closeBtn = banner.querySelector(".popup-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      showFloatingBall();
    });
  }
  
  const expandBtn = floatingBall.querySelector(".ball-expand");
  if (expandBtn) {
    expandBtn.addEventListener("click", () => {
      showBanner();
    });
  }
  
  const ballCloseBtn = floatingBall.querySelector(".ball-close");
  if (ballCloseBtn) {
    ballCloseBtn.addEventListener("click", () => {
      floatingBall.style.display = "none";
      container.style.display = "none";
      localStorage.setItem("gm_popup_permanently_closed", "1");
      permanentlyClosed = true;
    });
  }
  
  if (permanentlyClosed) {
    container.style.display = "none";
  } else if (bannerClosed) {
    banner.style.display = "none";
    floatingBall.style.display = "flex";
    container.style.display = "flex";
  } else {
    banner.style.display = "block";
    floatingBall.style.display = "none";
    container.style.display = "flex";
  }
}

async function initHome() {
  if (!document.getElementById("featured-products")) return;
  try {
    const response = await apiCall(`${GM_API_BASE_URL}/products/featured/`);
    const products = (response.results || response).map(normalizeProduct);
    if (products.length) {
      setLiveProducts(products);
      renderProducts("featured-products", products.slice(0, 4));
      return;
    }
  } catch (error) {
    console.warn("Using local featured products:", error.message);
  }
  renderProducts("featured-products", [PRODUCTS[0], PRODUCTS[4], PRODUCTS[2], PRODUCTS[1]]);
}

function initStorefrontLiveUpdates() {
  if (!document.getElementById("product-grid") && !document.getElementById("featured-products")) return;
  let currentVersion = localStorage.getItem("gm_store_version") || "";
  const check = async () => {
    try {
      const data = await apiCall(`${GM_API_BASE_URL}/admin/changes/`);
      if (!data.version || data.version === currentVersion) return;
      if (currentVersion) {
        showToast("Store updated. Refreshing products.");
        if (document.getElementById("product-grid")) await initShopControls();
        if (document.getElementById("featured-products")) await initHome();
      }
      currentVersion = data.version;
      localStorage.setItem("gm_store_version", currentVersion);
    } catch (error) {
      console.warn("Live update check failed:", error.message);
    }
  };
  check();
  setInterval(check, 15000);
}

function initHeroStatTabs() {
  const wrap = document.getElementById("hero-stat-tabs");
  if (!wrap) return;
  const subtitle = document.getElementById("hero-subtitle");
  const subtitleMap = [
    "Performance-ready summer essentials for energetic daily wear.",
    "Crafted with breathable natural fibers for cool all-day comfort.",
    "Fast and reliable delivery to keep your season moving."
  ];
  const tabs = [...wrap.querySelectorAll(".stat-tab")];
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      if (subtitle) subtitle.textContent = subtitleMap[index] || subtitleMap[0];
    });
  });
}

function initProductSwipe() {
  const main = document.getElementById("detail-main-img");
  if (!main) return;
  const thumbs = [...document.querySelectorAll(".thumb-btn")];
  const dots = [...document.querySelectorAll(".swipe-dot")];
  const images = thumbs.map((t) => t.dataset.img).filter(Boolean);
  if (!images.length) return;
  let current = 0;
  let startX = 0;
  let startY = 0;
  let mouseDown = false;
  const setImage = (idx) => {
    current = (idx + images.length) % images.length;
    main.classList.add("changing");
    main.src = images[current];
    setTimeout(() => main.classList.remove("changing"), 120);
    thumbs.forEach((t) => t.classList.toggle("active", Number(t.dataset.index) === current));
    dots.forEach((d) => d.classList.toggle("active", Number(d.dataset.dotIndex) === current));
  };
  setImage(0);
  main.addEventListener("touchstart", (e) => {
    startX = e.changedTouches[0].clientX;
    startY = e.changedTouches[0].clientY;
  }, { passive: true });
  main.addEventListener("touchend", (e) => {
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const delta = endX - startX;
    if (Math.abs(delta) < 30 || Math.abs(endY - startY) > 40) return;
    setImage(delta < 0 ? current + 1 : current - 1);
  }, { passive: true });
  main.addEventListener("mousedown", (e) => {
    mouseDown = true;
    startX = e.clientX;
    startY = e.clientY;
  });
  main.addEventListener("mouseup", (e) => {
    if (!mouseDown) return;
    mouseDown = false;
    const delta = e.clientX - startX;
    if (Math.abs(delta) < 30 || Math.abs(e.clientY - startY) > 50) return;
    setImage(delta < 0 ? current + 1 : current - 1);
  });
  main.addEventListener("mouseleave", () => { mouseDown = false; });
  document.querySelectorAll(".img-nav").forEach((btn) => {
    btn.addEventListener("click", () => setImage(current + Number(btn.dataset.dir || 1)));
  });
  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => setImage(Number(thumb.dataset.index || 0)));
  });
}

function initLayoutSpacing() {
  document.body.classList.toggle("has-fixed-header", Boolean(document.querySelector(".topbar")));
}

function formatCountdown(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const mins = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  return [hours, mins, secs].map((n) => String(n).padStart(2, "0")).join(":");
}

function initLimitedBadges() {
  const badges = [...document.querySelectorAll(".limited-badge[data-ends-seconds]")];
  if (!badges.length) return;
  
  const badgesCountdownCallback = (secondsLeft) => {
    badges.forEach((badge) => {
      badge.textContent = secondsLeft ? `Ends in ${formatCountdown(secondsLeft)}` : "Deal ended";
      badge.classList.toggle("expired", secondsLeft === 0);
    });
  };
  
  registerCountdownCallback(badgesCountdownCallback);
  startGlobalCountdownTick();
}

document.addEventListener("DOMContentLoaded", () => {
  initGlobalDealTimer();
  initLayoutSpacing();
  initAuthUI();
  initCartUI();
  renderCart();
  initHeroSlider();
  initHome();
  initShopControls();
  initProductDetail();
  initProductSwipe();
  initCheckoutPage();
  initFavoritesPage();
  initLoginPage();
  initCardInteractions();
  initReveal();
  initHeroStatTabs();
  initLimitedBadges();
  initPopupBanner();
  initStorefrontLiveUpdates();
  if (hasSeenFlipHint()) {
    document.querySelectorAll(".flip-hint").forEach((n) => n.classList.add("hide"));
  }
});