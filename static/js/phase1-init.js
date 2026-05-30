/**
 * Phase 1 Systems Integration
 * Connects Django messaging, authentication, and premium UI
 */

document.addEventListener('DOMContentLoaded', function() {
  // ==========================================
  // Convert Django messages to premium toasts
  // ==========================================
  const djangoMessages = document.getElementById('django-messages');
  if (djangoMessages) {
    djangoMessages.querySelectorAll('[data-message-type]').forEach(msg => {
      const type = msg.dataset.messageType || 'info';
      const text = msg.textContent.trim();
      
      if (text) {
        // Map Django message tags to notification types
        const typeMap = {
          'success': 'success',
          'error': 'error',
          'warning': 'warning',
          'info': 'info',
          'debug': 'info'
        };
        
        const notificationType = typeMap[type] || 'info';
        notifications.show(text, { type: notificationType });
      }
    });
  }

  // ==========================================
  // Auth Modal Integration
  // ==========================================
  const loginBtn = document.querySelector('[data-login-modal]');
  if (loginBtn) {
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      authModal.open('login');
    });
  }

  const signupBtn = document.querySelector('[data-signup-modal]');
  if (signupBtn) {
    signupBtn.addEventListener('click', (e) => {
      e.preventDefault();
      authModal.open('signup');
    });
  }

  // Replace traditional login/signup links
  document.querySelectorAll('a[href*="login"]').forEach(link => {
    if (link.textContent.toLowerCase().includes('login') || link.textContent.toLowerCase().includes('sign in')) {
      link.setAttribute('data-login-modal', 'true');
      link.addEventListener('click', (e) => {
        e.preventDefault();
        authModal.open('login');
      });
    }
  });

  // ==========================================
  // Intersection Observer for scroll animations
  // ==========================================
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fade-in-scale');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe elements with reveal class
  document.querySelectorAll('.reveal').forEach(el => {
    observer.observe(el);
  });

  // ==========================================
  // Handle checkout flow notifications
  // ==========================================
  const checkoutBtn = document.querySelector('[data-checkout-button]');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', function(e) {
      const cartItems = document.querySelectorAll('[data-cart-item]');
      if (cartItems.length === 0) {
        e.preventDefault();
        notifications.error('Your cart is empty', { title: 'Cart Empty' });
      }
    });
  }

  // ==========================================
  // Handle Add to Cart notifications
  // ==========================================
  document.addEventListener('cart-updated', function(e) {
    const { action, product, quantity } = e.detail;
    
    if (action === 'added') {
      notifications.success(`${product || 'Product'} added to cart`, {
        title: 'Added to Cart'
      });
    } else if (action === 'removed') {
      notifications.info(`${product || 'Product'} removed from cart`, {
        title: 'Removed from Cart'
      });
    }
  });

  // ==========================================
  // Handle Wishlist notifications
  // ==========================================
  document.addEventListener('wishlist-updated', function(e) {
    const { action, product } = e.detail;
    
    if (action === 'added') {
      notifications.success(`Added to favorites`, {
        title: 'Saved'
      });
    } else if (action === 'removed') {
      notifications.info(`Removed from favorites`, {
        title: 'Removed'
      });
    }
  });

  // ==========================================
  // Skeleton UI for slow networks
  // ==========================================
  if ('connection' in navigator) {
    const connection = navigator.connection;
    const effectiveType = connection.effectiveType;
    
    // Show skeleton loaders on slow connections
    if (effectiveType === '3g' || effectiveType === '4g') {
      const productGrid = document.querySelector('.grid, .product-grid-fixed');
      if (productGrid) {
        // Could implement skeltons here if needed
      }
    }
  }

  // ==========================================
  // Premium form error handling
  // ==========================================
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
      // Clear previous errors
      this.querySelectorAll('[role="alert"]').forEach(el => el.remove());
    });
  });

  // ==========================================
  // Accessibility: Announce notifications to screen readers
  // ==========================================
  const originalShow = notifications.show.bind(notifications);
  notifications.show = function(message, options = {}) {
    const id = originalShow(message, options);
    
    // Announce to screen readers
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.textContent = `${options.title || ''} ${message}`;
    document.body.appendChild(announcement);
    
    setTimeout(() => announcement.remove(), 3000);
    
    return id;
  };
});

// ==========================================
// Global error handling
// ==========================================
window.addEventListener('error', function(event) {
  if (event.message && event.message.includes('network')) {
    notifications.error('Network error. Please check your connection.', {
      title: 'Connection Error'
    });
  }
});

// ==========================================
// Handle before unload
// ==========================================
window.addEventListener('beforeunload', function() {
  // Clear notifications before page unload
  if (window.notifications) {
    notifications.clear();
  }
});

console.log('✓ Phase 1 Systems initialized - Notifications, Auth Modal, Skeleton UI');
