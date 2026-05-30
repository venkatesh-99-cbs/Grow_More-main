/**
 * Premium Modal Authentication System
 * Replaces inline auth pages with elegant modal experience
 */

class AuthModalManager {
  constructor() {
    this.modal = null;
    this.overlay = null;
    this.currentPane = 'login';
    this.init();
  }

  init() {
    this.createModal();
    this.attachEventListeners();
  }

  createModal() {
    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'auth-modal-overlay';
    this.overlay.innerHTML = `
      <div class="auth-modal">
        <button class="auth-modal-close" aria-label="Close">✕</button>
        
        <div class="auth-modal-header">
          <h2 class="auth-modal-title">Welcome to Grow More</h2>
          <p class="auth-modal-subtitle">Premium Summer Menswear</p>
        </div>

        <div class="auth-tabs">
          <button class="auth-tab-btn active" data-pane="login">Sign In</button>
          <button class="auth-tab-btn" data-pane="signup">Create Account</button>
          <button class="auth-tab-btn" data-pane="social">Continue</button>
        </div>

        <!-- Login Pane -->
        <form class="auth-pane active" data-pane="login" id="auth-login-form">
          <div class="auth-error" style="display: none;"></div>
          <input 
            type="email" 
            class="auth-input" 
            placeholder="Email address"
            name="email"
            required
          />
          <input 
            type="password" 
            class="auth-input" 
            placeholder="Password"
            name="password"
            required
          />
          <label class="check-line">
            <input type="checkbox" name="remember" />
            Remember me
          </label>
          <button type="submit" class="auth-button primary">Sign In</button>
          <div class="auth-footer">
            Don't have an account? <a href="#" class="switch-pane" data-pane="signup">Create one</a>
          </div>
        </form>

        <!-- Sign Up Pane -->
        <form class="auth-pane" data-pane="signup" id="auth-signup-form">
          <div class="auth-error" style="display: none;"></div>
          <input 
            type="text" 
            class="auth-input" 
            placeholder="Full name"
            name="full_name"
            required
          />
          <input 
            type="email" 
            class="auth-input" 
            placeholder="Email address"
            name="email"
            required
          />
          <input 
            type="password" 
            class="auth-input" 
            placeholder="Create password"
            name="password"
            required
          />
          <input 
            type="password" 
            class="auth-input" 
            placeholder="Confirm password"
            name="password_confirm"
            required
          />
          <label class="check-line">
            <input type="checkbox" name="terms" required />
            I agree to Terms and Conditions
          </label>
          <button type="submit" class="auth-button primary">Create Account</button>
          <div class="auth-footer">
            Already have an account? <a href="#" class="switch-pane" data-pane="login">Sign in</a>
          </div>
        </form>

        <!-- Social/Continue Pane -->
        <div class="auth-pane" data-pane="social">
          <div class="auth-error" style="display: none;"></div>
          <p style="text-align: center; color: #5f5860; font-size: 0.9rem; margin-bottom: 16px;">
            Choose your preferred login method
          </p>
          <button class="social-login-btn" id="google-login-btn">
            <span class="social-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
            </span>
            Continue with Google
          </button>
          <div class="auth-divider">
            <span class="auth-divider-text">or</span>
          </div>
          <a href="#" class="social-login-btn" onclick="authModal.switchPane('login'); return false;">
            <span class="social-icon">✉</span>
            Sign In with Email
          </a>
          <div class="auth-footer">
            New to Grow More? <a href="#" class="switch-pane" data-pane="signup">Create an account</a>
          </div>
        </div>
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

    // Pane switching links
    this.overlay.querySelectorAll('.switch-pane').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        this.switchPane(link.dataset.pane);
      });
    });

    // Form submissions
    this.overlay.querySelector('#auth-login-form').addEventListener('submit', (e) => this.handleLogin(e));
    this.overlay.querySelector('#auth-signup-form').addEventListener('submit', (e) => this.handleSignup(e));

    // Google login
    this.overlay.querySelector('#google-login-btn').addEventListener('click', (e) => {
      e.preventDefault();
      this.handleGoogleLogin();
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

  handleLogin(e) {
    e.preventDefault();
    
    const form = e.target;
    const email = form.querySelector('input[name="email"]').value;
    const password = form.querySelector('input[name="password"]').value;
    const errorEl = form.querySelector('.auth-error');

    if (!email || !password) {
      this.showError(errorEl, 'Please fill in all fields');
      return;
    }

    // Submit to actual login endpoint
    const loginForm = document.createElement('form');
    loginForm.method = 'POST';
    loginForm.action = window.location.origin + '/accounts/login/';
    loginForm.innerHTML = `
      <input type="hidden" name="username" value="${this.escapeHtml(email)}">
      <input type="hidden" name="password" value="${this.escapeHtml(password)}">
    `;
    
    // Add CSRF token
    const csrftoken = this.getCsrfToken();
    if (csrftoken) {
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrftoken;
      loginForm.appendChild(csrfInput);
    }

    document.body.appendChild(loginForm);
    loginForm.submit();
  }

  handleSignup(e) {
    e.preventDefault();
    
    const form = e.target;
    const fullName = form.querySelector('input[name="full_name"]').value;
    const email = form.querySelector('input[name="email"]').value;
    const password = form.querySelector('input[name="password"]').value;
    const passwordConfirm = form.querySelector('input[name="password_confirm"]').value;
    const errorEl = form.querySelector('.auth-error');

    if (!fullName || !email || !password || !passwordConfirm) {
      this.showError(errorEl, 'Please fill in all fields');
      return;
    }

    if (password !== passwordConfirm) {
      this.showError(errorEl, 'Passwords do not match');
      return;
    }

    // Submit to actual signup endpoint
    const signupForm = document.createElement('form');
    signupForm.method = 'POST';
    signupForm.action = window.location.origin + '/accounts/register/';
    signupForm.innerHTML = `
      <input type="hidden" name="full_name" value="${this.escapeHtml(fullName)}">
      <input type="hidden" name="email" value="${this.escapeHtml(email)}">
      <input type="hidden" name="password" value="${this.escapeHtml(password)}">
      <input type="hidden" name="password_confirm" value="${this.escapeHtml(passwordConfirm)}">
    `;
    
    // Add CSRF token
    const csrftoken = this.getCsrfToken();
    if (csrftoken) {
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrftoken;
      signupForm.appendChild(csrfInput);
    }

    document.body.appendChild(signupForm);
    signupForm.submit();
  }

  handleGoogleLogin() {
    // Trigger Google OAuth flow
    window.location.href = '/accounts/google/login/callback/';
  }

  showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
  }

  getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] ||
           '';
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  open(pane = 'login') {
    this.switchPane(pane);
    this.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  toggle(pane = 'login') {
    if (this.overlay.classList.contains('active')) {
      this.close();
    } else {
      this.open(pane);
    }
  }
}

// Create global instance
const authModal = new AuthModalManager();

// Handle login button clicks
document.addEventListener('DOMContentLoaded', function() {
  // Check if user should see auth modal
  const authLink = document.querySelector('[data-auth-modal]');
  if (authLink) {
    authLink.addEventListener('click', (e) => {
      const pane = authLink.dataset.authModal || 'login';
      e.preventDefault();
      authModal.open(pane);
    });
  }

  // Handle Continue with Google buttons
  document.querySelectorAll('[data-google-login]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      authModal.open('social');
    });
  });
});

// Export for external use
window.authModal = authModal;
