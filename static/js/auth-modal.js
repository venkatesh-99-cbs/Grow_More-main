/**
 * Premium Modal Authentication System
 * Replaces inline auth pages with elegant modal experience
 */

class AuthModalManager {
  constructor() {
    this.modal = null;
    this.overlay = null;
    this.currentPane = 'login';
    this.isInitialized = false;
  }

  init() {
    if (this.isInitialized) return;
    this.createModal();
    this.attachEventListeners();
    this.isInitialized = true;
  }

  createModal() {
    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'auth-modal-overlay';
    this.overlay.innerHTML = `
      <div class="auth-modal glass-effect">
        <button class="auth-modal-close" aria-label="Close">✕</button>
        
        <div class="auth-modal-header">
          <div class="auth-modal-logo">
             <img src="/media/logo/Grow_More_logo.png" alt="Grow More" style="width: 60px; height: 60px; object-fit: contain; margin-bottom: 12px; filter: drop-shadow(0 4px 12px rgba(81, 226, 245, 0.4));">
          </div>
          <h2 class="auth-modal-title">Elevate Your Style</h2>
          <p class="auth-modal-subtitle">Join the Grow More community</p>
        </div>

        <div class="auth-tabs">
          <button class="auth-tab-btn active" data-pane="login">Sign In</button>
          <button class="auth-tab-btn" data-pane="signup">Join Now</button>
        </div>

        <!-- Login Pane -->
        <form class="auth-pane active" data-pane="login" id="auth-login-form">
          <div class="auth-error" style="display: none;"></div>
          <div class="input-group">
            <input
              type="email"
              class="auth-input"
              placeholder="Email address"
              name="username"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="password"
              class="auth-input"
              placeholder="Password"
              name="password"
              required
            />
          </div>
          <div class="auth-options">
            <label class="check-line">
              <input type="checkbox" name="remember" />
              <span>Keep me signed in</span>
            </label>
            <a href="/accounts/password/reset/" class="forgot-link">Forgot?</a>
          </div>
          <button type="submit" class="auth-button primary">Sign In</button>

          <div class="auth-divider">
            <span class="auth-divider-text">OR CONTINUE WITH</span>
          </div>

          <button type="button" class="social-login-btn google-btn" data-google-login>
            <span class="social-icon">
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
            </span>
            Google
          </button>
        </form>

        <!-- Sign Up Pane -->
        <form class="auth-pane" data-pane="signup" id="auth-signup-form">
          <div class="auth-error" style="display: none;"></div>
          <div class="input-group">
            <input
              type="text"
              class="auth-input"
              placeholder="Username"
              name="username"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="email"
              class="auth-input"
              placeholder="Email address"
              name="email"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="password"
              class="auth-input"
              placeholder="Create password"
              name="password"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="password"
              class="auth-input"
              placeholder="Confirm password"
              name="password_confirm"
              required
            />
          </div>
          <button type="submit" class="auth-button primary">Create Account</button>

          <div class="auth-divider">
            <span class="auth-divider-text">OR JOIN WITH</span>
          </div>

          <button type="button" class="social-login-btn google-btn" data-google-login>
            <span class="social-icon">
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
            </span>
            Google
          </button>
        </form>
      </div>
    `;

    document.body.appendChild(this.overlay);
    this.modal = this.overlay.querySelector('.auth-modal');
  }

  attachEventListeners() {
    // Close button
    this.overlay.querySelector('.auth-modal-close').addEventListener('click', () => this.close());

    // Overlay click to close
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) this.close();
    });

    // Tab switching
    this.overlay.querySelectorAll('.auth-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.switchPane(btn.dataset.pane);
      });
    });

    // Form submissions
    this.overlay.querySelector('#auth-login-form').addEventListener('submit', (e) => this.handleLogin(e));
    this.overlay.querySelector('#auth-signup-form').addEventListener('submit', (e) => this.handleSignup(e));

    // Google login
    this.overlay.querySelectorAll('[data-google-login]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleGoogleLogin();
        });
    });
  }

  switchPane(pane) {
    this.currentPane = pane;

    // Update tabs
    this.overlay.querySelectorAll('.auth-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.pane === pane);
    });

    // Update panes
    this.overlay.querySelectorAll('.auth-pane').forEach(pane_el => {
      pane_el.classList.toggle('active', pane_el.dataset.pane === pane);
    });

    // Clear errors
    this.overlay.querySelectorAll('.auth-error').forEach(err => {
      err.style.display = 'none';
      err.textContent = '';
    });
  }

  async handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const errorEl = form.querySelector('.auth-error');
    const submitBtn = form.querySelector('button[type="submit"]');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in...';

    try {
      const response = await fetch('/accounts/login/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCsrfToken()
        }
      });

      if (response.ok) {
        window.location.reload();
      } else {
        const data = await response.json();
        this.showError(errorEl, data.errors || 'Invalid login credentials');
      }
    } catch (err) {
      // If server doesn't support AJAX login, fallback to standard form submit
      form.method = 'POST';
      form.action = '/accounts/login/';
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = this.getCsrfToken();
      form.appendChild(csrfInput);
      form.submit();
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  }

  async handleSignup(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const errorEl = form.querySelector('.auth-error');
    const submitBtn = form.querySelector('button[type="submit"]');

    if (formData.get('password') !== formData.get('password_confirm')) {
      this.showError(errorEl, 'Passwords do not match');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';

    try {
      const response = await fetch('/accounts/register/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCsrfToken()
        }
      });

      if (response.ok) {
        window.location.href = '/accounts/profile/';
      } else {
        const data = await response.json();
        this.showError(errorEl, data.errors || 'Registration failed. Please check your details.');
      }
    } catch (err) {
      // Fallback
      form.method = 'POST';
      form.action = '/accounts/register/';
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = this.getCsrfToken();
      form.appendChild(csrfInput);
      form.submit();
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Account';
    }
  }

  handleGoogleLogin() {
    // Redirect to the allauth google login URL
    window.location.href = '/accounts/google/login/?process=login';
  }

  showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
    element.classList.add('shake');
    setTimeout(() => element.classList.remove('shake'), 500);
  }

  getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] ||
           '';
  }

  open(pane = 'login') {
    this.init();
    this.switchPane(pane);
    this.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  close() {
    if (!this.overlay) return;
    this.overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Create global instance
const authModal = new AuthModalManager();

// Handle triggers
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-auth-trigger]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const pane = trigger.dataset.authTrigger || 'login';
      authModal.open(pane);
    });
  });
});

window.authModal = authModal;
