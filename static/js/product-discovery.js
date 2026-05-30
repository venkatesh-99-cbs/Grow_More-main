/**
 * Product Discovery Intro Screen
 * Displays Grow More logo with product discovery progress bar
 * Shows loading messages related to discovering store products
 */

class ProductDiscoveryIntro {
  constructor(options = {}) {
    this.duration = options.duration || 4000; // 4 seconds
    this.sessionKey = 'grow_more_intro_shown';
    this.messages = [
      'Discovering our latest collections...',
      'Loading premium products...',
      'Preparing exclusive offers...',
      'Curating the best selections...',
      'Ready to explore Grow More!',
    ];
    this.currentMessageIndex = 0;

    // Check if already shown this session
    if (this.shouldShow()) {
      this.init();
    }
  }

  shouldShow() {
    // Show once per session
    if (!sessionStorage.getItem(this.sessionKey)) {
      sessionStorage.setItem(this.sessionKey, 'true');
      return true;
    }
    return false;
  }

  init() {
    this.createIntroScreen();
    this.startAnimation();
  }

  createIntroScreen() {
    const screen = document.createElement('div');
    screen.id = 'product-discovery-intro';
    screen.innerHTML = `
      <div class="discovery-container">
        <div class="discovery-content">
          <!-- Logo -->
          <div class="discovery-logo-wrapper">
            <img 
              src="/media/logo/Grow_More_logo.png" 
              alt="Grow More Logo" 
              class="discovery-logo"
              onerror="this.src='/static/images/placeholder-logo.png'"
            />
          </div>

          <!-- Title -->
          <h1 class="discovery-title">Welcome to Grow More</h1>
          <p class="discovery-subtitle">Discover Premium Menswear</p>

          <!-- Progress Bar Container -->
          <div class="discovery-progress-container">
            <div class="discovery-progress-bar">
              <div class="discovery-progress-fill"></div>
            </div>
            <div class="discovery-progress-text">
              <span class="discovery-message">Discovering our latest collections...</span>
              <span class="discovery-percentage">0%</span>
            </div>
          </div>

          <!-- Skip Button -->
          <button class="discovery-skip-btn" id="discovery-skip-btn">
            Skip (Press ESC)
          </button>
        </div>

        <!-- Background Gradient -->
        <div class="discovery-gradient"></div>
      </div>
    `;

    document.body.appendChild(screen);
    this.screen = screen;

    // Setup event listeners
    screen.querySelector('#discovery-skip-btn').addEventListener('click', () => this.finish());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.finish();
    });
  }

  startAnimation() {
    const startTime = Date.now();
    const progressFill = this.screen.querySelector('.discovery-progress-fill');
    const messageElement = this.screen.querySelector('.discovery-message');
    const percentageElement = this.screen.querySelector('.discovery-percentage');
    const container = this.screen.querySelector('.discovery-container');

    // Fade in container
    container.style.animation = 'discoveryFadeIn 0.5s ease-out';

    // Animate progress
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min((elapsed / this.duration) * 100, 100);

      // Update progress bar
      progressFill.style.width = progress + '%';
      percentageElement.textContent = Math.floor(progress) + '%';

      // Update message based on progress
      const messageIndex = Math.floor((progress / 100) * (this.messages.length - 1));
      if (messageIndex !== this.currentMessageIndex && messageIndex < this.messages.length) {
        this.currentMessageIndex = messageIndex;
        messageElement.textContent = this.messages[messageIndex];
        messageElement.style.animation = 'discoveryMessagePop 0.4s ease-out';
      }

      if (progress < 100) {
        requestAnimationFrame(animate);
      } else {
        // Complete
        setTimeout(() => this.finish(), 500);
      }
    };

    requestAnimationFrame(animate);
  }

  finish() {
    if (!this.screen) return;

    const container = this.screen.querySelector('.discovery-container');
    container.style.animation = 'discoveryFadeOut 0.6s ease-in forwards';

    setTimeout(() => {
      if (this.screen && this.screen.parentNode) {
        this.screen.parentNode.removeChild(this.screen);
      }
    }, 600);
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ProductDiscoveryIntro();
  });
} else {
  new ProductDiscoveryIntro();
}
