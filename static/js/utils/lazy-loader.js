/**
 * Professional Lazy Content Loader
 * Uses Intersection Observer to load components/sections only when approaching the viewport.
 */

class LazyLoader {
    constructor() {
        this.observerOptions = {
            root: null,
            rootMargin: '100px 0px',
            threshold: 0.01
        };

        this.observer = new IntersectionObserver(this.handleIntersection.bind(this), this.observerOptions);
    }

    init() {
        // Observe lazy-load sections
        const sections = document.querySelectorAll('[data-lazy-section]');
        sections.forEach(section => this.observer.observe(section));

        // Initialize lazy images
        this.initLazyImages();
    }

    handleIntersection(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                this.loadSectionContent(target);
                observer.unobserve(target);
            }
        });
    }

    async loadSectionContent(container) {
        const url = container.dataset.lazyUrl;
        if (!url) return;

        container.classList.add('loading-progressive');
        container.setAttribute('aria-busy', 'true');
        container.setAttribute('aria-live', 'polite');

        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (response.ok) {
                const html = await response.text();
                // Smooth transition from skeleton to content
                container.style.opacity = '0';
                setTimeout(() => {
                    container.innerHTML = html;
                    container.style.opacity = '1';
                    container.classList.remove('loading-progressive');
                    container.removeAttribute('aria-busy');
                    // Re-initialize any JS needed for new content
                    document.dispatchEvent(new CustomEvent('content-loaded', { detail: { container } }));
                }, 300);
            }
        } catch (error) {
            console.error('Lazy load failed:', error);
            container.classList.remove('loading-progressive');
        }
    }

    initLazyImages() {
        // Native lazy loading for modern browsers
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');

        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('.blur-up-image').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
}

// Global instance
window.growMoreLazyLoader = new LazyLoader();
document.addEventListener('DOMContentLoaded', () => window.growMoreLazyLoader.init());
