/**
 * Skeleton UI Loading System
 * Premium placeholders while content loads
 */

class SkeletonLoader {
  static createProductCardSkeleton() {
    return `
      <div class="product-card skeleton-card">
        <div class="product-media">
          <div class="skeleton skeleton-image" style="height: 240px;"></div>
        </div>
        <div class="product-body">
          <div class="skeleton skeleton-line" style="width: 100%;"></div>
          <div class="skeleton skeleton-line" style="width: 85%;"></div>
          <div class="skeleton skeleton-line short" style="margin-top: 12px;"></div>
          <div class="skeleton skeleton-line short"></div>
          <div style="margin-top: 16px;">
            <div class="skeleton" style="height: 40px; border-radius: 10px;"></div>
          </div>
        </div>
      </div>
    `;
  }

  static createHeroSkeleton() {
    return `
      <div class="hero-wrap" style="background: linear-gradient(135deg, rgba(162,128,137,.1) 0%, rgba(162,128,137,.05) 100%); display: flex; align-items: center; justify-content: center;">
        <div class="skeleton" style="width: 300px; height: 150px; border-radius: 16px;"></div>
      </div>
    `;
  }

  static createGridSkeleton(count = 6, type = 'card') {
    const skeleton = type === 'card' ? this.createProductCardSkeleton() : this.createProductCardSkeleton();
    return Array(count).fill(skeleton).join('');
  }

  static loadProducts(container, count = 6, timeout = 2000) {
    container.innerHTML = this.createGridSkeleton(count);
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(true);
      }, timeout);
    });
  }

  static loadHero(container, timeout = 1500) {
    container.innerHTML = this.createHeroSkeleton();
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(true);
      }, timeout);
    });
  }

  static hide(element) {
    element.style.opacity = '0';
    setTimeout(() => {
      element.remove();
    }, 300);
  }
}

// Export for external use
window.SkeletonLoader = SkeletonLoader;
