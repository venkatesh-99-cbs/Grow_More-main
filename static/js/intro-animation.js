/**
 * Premium Intro/Loading Animation
 * Cinematic logo reveal with luxury effects
 * Plays before homepage loads
 */

class IntroAnimation {
  constructor() {
    this.isPlaying = false;
    this.duration = 3500; // 3.5 seconds
    this.init();
  }

  init() {
    // Only show if not previously shown in this session
    if (sessionStorage.getItem('introShown')) {
      this.skip();
      return;
    }

    this.createIntroScreen();
    this.startAnimation();
    sessionStorage.setItem('introShown', 'true');
  }

  createIntroScreen() {
    const intro = document.createElement('div');
    intro.id = 'intro-animation';
    intro.innerHTML = `
      <div class="intro-overlay">
        <div class="intro-container">
          {# Background with animated gradients #}
          <div class="intro-bg">
            <div class="intro-gradient-1"></div>
            <div class="intro-gradient-2"></div>
            <div class="intro-particles"></div>
          </div>

          {# Logo and branding #}
          <div class="intro-content">
            <div class="intro-logo-wrapper">
              <img 
                src="/media/logo/Grow_More_logo.png" 
                alt="Grow More"
                class="intro-logo"
              />
              <div class="intro-logo-glow"></div>
            </div>

            <h1 class="intro-title">GROW MORE</h1>
            <p class="intro-tagline">Own The Heat. Stay Cool. Move Bold.</p>

            <div class="intro-progress">
              <div class="intro-progress-bar"></div>
            </div>
          </div>

          {# Skip button #}
          <button class="intro-skip" id="intro-skip-btn">Skip</button>
        </div>
      </div>
    `;

    document.body.insertBefore(intro, document.body.firstChild);
    this.setupEventListeners();
  }

  setupEventListeners() {
    const skipBtn = document.getElementById('intro-skip-btn');
    if (skipBtn) {
      skipBtn.addEventListener('click', () => this.skip());
    }

    // Also skip on any key press
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.skip();
    }, { once: true });
  }

  startAnimation() {
    this.isPlaying = true;
    const intro = document.getElementById('intro-animation');
    
    // Trigger animations
    setTimeout(() => {
      intro.classList.add('intro-active');
    }, 100);

    // Auto-finish after duration
    setTimeout(() => {
      this.finish();
    }, this.duration);
  }

  finish() {
    const intro = document.getElementById('intro-animation');
    if (intro) {
      intro.classList.add('intro-exit');
      setTimeout(() => {
        intro.remove();
        // Unblock main content
        document.body.style.overflow = '';
      }, 500);
    }
    this.isPlaying = false;
  }

  skip() {
    if (!this.isPlaying) return;
    const intro = document.getElementById('intro-animation');
    if (intro) {
      intro.classList.add('intro-skip-exit');
      setTimeout(() => {
        intro.remove();
        document.body.style.overflow = '';
      }, 400);
    }
    this.isPlaying = false;
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  new IntroAnimation();
});

// Export for external use
window.IntroAnimation = IntroAnimation;
