/**
 * Advanced Cinematic Hero Slider
 * Handles dynamic animations based on banner settings
 */
class HeroSlider {
  constructor() {
    this.slides = [...document.querySelectorAll(".hero-slide")];
    if (!this.slides.length) return;

    this.currentIndex = 0;
    this.interval = 6000;
    this.init();
  }

  init() {
    // Initial activation
    this.activateSlide(0);

    if (this.slides.length > 1) {
      setInterval(() => this.next(), this.interval);
    }
  }

  next() {
    this.slides[this.currentIndex].classList.remove("active");
    this.currentIndex = (this.currentIndex + 1) % this.slides.length;
    this.activateSlide(this.currentIndex);
  }

  activateSlide(index) {
    const slide = this.slides[index];
    slide.classList.add("active");

    // Trigger animation-specific logic if needed
    const animation = slide.dataset.animation;
    const theme = slide.dataset.theme;

    // We can add specific JS-driven effects here if CSS isn't enough
    // For example, subtle parallax or zoom
    if (animation === 'parallax') {
        this.applyParallax(slide);
    }
  }

  applyParallax(slide) {
      // Logic for parallax if chosen
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new HeroSlider();
});
