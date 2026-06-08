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
    this.indicators = [...document.querySelectorAll(".indicator")];
    // Initial activation
    this.activateSlide(0);

    if (this.slides.length > 1) {
      this.startAutoplay();
      this.bindIndicators();
    }
  }

  startAutoplay() {
    this.autoplayInterval = setInterval(() => this.next(), this.interval);
  }

  stopAutoplay() {
    clearInterval(this.autoplayInterval);
  }

  bindIndicators() {
    this.indicators.forEach(indicator => {
      indicator.addEventListener("click", () => {
        const index = parseInt(indicator.dataset.index);
        this.goTo(index);
        this.stopAutoplay();
        this.startAutoplay();
      });
    });
  }

  goTo(index) {
    if (index === this.currentIndex) return;
    this.slides[this.currentIndex].classList.remove("active");
    this.indicators[this.currentIndex]?.classList.remove("active");
    this.currentIndex = index;
    this.activateSlide(this.currentIndex);
  }

  next() {
    const nextIndex = (this.currentIndex + 1) % this.slides.length;
    this.goTo(nextIndex);
  }

  activateSlide(index) {
    const slide = this.slides[index];
    slide.classList.add("active");
    this.indicators[index]?.classList.add("active");

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
